"""Build an editable three-region PBR group in Blender 4.5+/5.x.

Input UV is Blender (U,V); lattice coordinates are runtime (U,1-V).
Input/output normals use the original Blender tangent frame. No UVs, images,
existing nodes or materials are deleted. The caller owns all resources.
Image filtering is Blender-controlled, unlike the explicit GLSL gradients.
"""
import bpy

VERSION = 'surface-three-region-v1'
PRESETS = {
    'natural': ((.62, 0, .035, .025), (5, .45)),
    'courses': ((.90, 1, 0, .020), (7, .55)),
}


class Nodes:
    def __init__(self, tree):
        self.tree = tree
        self.nodes, self.links = tree.nodes, tree.links
        self.frame = None
        self.count = 0

    def node(self, kind, label):
        n = self.nodes.new(kind)
        n.label = label
        if self.frame:
            n.parent = self.frame
        n.location = ((self.count % 8) * 205, -(self.count // 8) * 150)
        self.count += 1
        return n

    def section(self, label, location):
        self.frame = self.nodes.new('NodeFrame')
        self.frame.label = label
        self.frame.name = label
        self.frame.location = location
        self.count = 0

    def input(self, target, value):
        if hasattr(value, 'is_output'):
            self.links.new(value, target)
        else:
            target.default_value = value

    def math(self, operation, a, b=None, label=None, c=None):
        n = self.node('ShaderNodeMath', label or operation.title())
        n.operation = operation
        self.input(n.inputs[0], a)
        if b is not None:
            self.input(n.inputs[1], b)
        if c is not None:
            self.input(n.inputs[2], c)
        return n.outputs[0]

    def add(self, a, b): return self.math('ADD', a, b)
    def sub(self, a, b): return self.math('SUBTRACT', a, b)
    def mul(self, a, b): return self.math('MULTIPLY', a, b)
    def div(self, a, b): return self.math('DIVIDE', a, b)
    def floor(self, a): return self.math('FLOOR', a)
    def fract(self, a): return self.sub(a, self.floor(a))
    def mod(self, a, b): return self.sub(a, self.mul(self.floor(self.div(a, b)), b))
    def mix(self, a, b, t): return self.add(a, self.mul(self.sub(b, a), t))

    def xyz(self, x, y, z=0):
        n = self.node('ShaderNodeCombineXYZ', 'Vector')
        for i, value in enumerate((x, y, z)):
            self.input(n.inputs[i], value)
        return n.outputs[0]

    def split(self, vector):
        n = self.node('ShaderNodeSeparateXYZ', 'Components')
        self.input(n.inputs[0], vector)
        return tuple(n.outputs)

    def vector(self, operation, a, b=None):
        n = self.node('ShaderNodeVectorMath', operation.title())
        n.operation = operation
        self.input(n.inputs[0], a)
        if b is not None:
            self.input(n.inputs[3 if operation == 'SCALE' else 1], b)
        return n.outputs['Value' if operation == 'DOT_PRODUCT' else 'Vector']

    def weighted(self, values, weights):
        parts = [self.vector('SCALE', value, weight) for value, weight in zip(values, weights)]
        return self.vector('ADD', self.vector('ADD', parts[0], parts[1]), parts[2])


def _hash(nodes, x, y):
    x, y = nodes.mod(x, 251), nodes.mod(y, 251)
    result = []
    for a, b, seed in ((37, 17, 19), (11, 53, 67), (71, 29, 131), (43, 101, 211)):
        h = nodes.mod(nodes.add(nodes.add(nodes.mul(x, a), nodes.mul(y, b)), seed), 251)
        h = nodes.mod(nodes.mul(nodes.mod(nodes.mul(h, h), 251), h), 251)
        result.append(nodes.div(nodes.add(h, .5), 251))
    return result


def _region(nodes, runtime_uv, cell, settings):
    size, half_turn, jitter, brightness = settings
    h = _hash(nodes, *cell)
    quarter = nodes.floor(nodes.mul(h[2], 2 if half_turn else 4))
    if half_turn:
        quarter = nodes.mul(quarter, 2)
    equal = lambda value: nodes.math('COMPARE', quarter, value, c=.1)
    c, s = nodes.sub(equal(0), equal(2)), nodes.sub(equal(1), equal(3))
    frequency = nodes.add(1, nodes.mul(nodes.sub(nodes.mul(h[3], 2), 1), jitter))
    anchor = (nodes.mul(nodes.add(cell[0], nodes.mul(cell[1], .5)), size),
              nodes.mul(cell[1], .8660254037844386 * size))
    u, v = [nodes.sub(value, origin) for value, origin in zip(runtime_uv, anchor)]
    sample_u = nodes.add(nodes.add(nodes.mul(nodes.sub(nodes.mul(c, u), nodes.mul(s, v)), frequency), anchor[0]), h[0])
    sample_v = nodes.add(nodes.add(nodes.mul(nodes.add(nodes.mul(s, u), nodes.mul(c, v)), frequency), anchor[1]), h[1])
    rgb_gain = nodes.add(1, nodes.mul(nodes.sub(nodes.mul(nodes.fract(nodes.mul(h[3], 17)), 2), 1), brightness))
    # Images use Blender UV while the lattice is defined in exported/runtime UV.
    return nodes.xyz(sample_u, nodes.sub(1, sample_v)), c, s, frequency, rgb_gain


def _build_group(family, images):
    settings, blend = PRESETS[family]
    group = bpy.data.node_groups.new(f'Surface / regional texture / {family} / {VERSION}', 'ShaderNodeTree')
    group['stochasticVersion'] = VERSION
    group['family'] = family
    group['settings'] = list(settings)
    group['blend'] = list(blend)
    group.interface.new_socket(name='UV', in_out='INPUT', socket_type='NodeSocketVector')
    for name in ('Color', 'Normal', 'ORM'):
        group.interface.new_socket(name=name, in_out='OUTPUT', socket_type='NodeSocketColor')
    nodes = Nodes(group)
    input_node = nodes.node('NodeGroupInput', 'Original Blender UV0')
    output_node = nodes.node('NodeGroupOutput', 'Shared PBR region blend')
    nodes.section('Runtime UV lattice — unique paint is independent', (0, 0))
    original_u, original_v, _ = nodes.split(input_node.outputs['UV'])
    uv = (original_u, nodes.sub(1, original_v))
    grid_u = nodes.div(nodes.sub(uv[0], nodes.mul(uv[1], .5773502691896258)), settings[0])
    grid_v = nodes.mul(uv[1], 1.1547005383792517 / settings[0])
    base_u, base_v = nodes.floor(grid_u), nodes.floor(grid_v)
    fu, fv = nodes.sub(grid_u, base_u), nodes.sub(grid_v, base_v)
    upper = nodes.math('GREATER_THAN', nodes.add(fu, fv), 1)
    cells = ((nodes.add(base_u, upper), nodes.add(base_v, upper)),
             (nodes.add(base_u, nodes.sub(1, upper)), nodes.add(base_v, upper)),
             (nodes.add(base_u, upper), nodes.add(base_v, nodes.sub(1, upper))))
    weights = (
        nodes.mix(nodes.sub(1, nodes.add(fu, fv)), nodes.sub(nodes.add(fu, fv), 1), upper),
        nodes.mix(fu, nodes.sub(1, fu), upper),
        nodes.mix(fv, nodes.sub(1, fv), upper),
    )
    samples = []
    for i, cell in enumerate(cells):
        nodes.section(f'Region {i + 1} — deterministic phase and rotation', (1800 * i, -1200))
        sample_uv, c, s, frequency, brightness = _region(nodes, uv, cell, settings)
        channels = {}
        for role in ('color', 'normal', 'orm'):
            image = nodes.node('ShaderNodeTexImage', f'{family} {role} / region {i + 1}')
            image.image = images[role]
            image.extension = 'REPEAT'
            image.interpolation = 'Linear'
            nodes.links.new(sample_uv, image.inputs['Vector'])
            channels[role] = image.outputs['Color']
        samples.append((channels, c, s, frequency, brightness))

    nodes.section('One linear-color weight set for every PBR channel', (0, -3900))
    color_weights = []
    for weight, (channels, *_rest) in zip(weights, samples):
        luminance = nodes.vector('DOT_PRODUCT', channels['color'], (.2126, .7152, .0722))
        influence = nodes.mix(1, nodes.math('MAXIMUM', luminance, .03), blend[1])
        w = nodes.mul(nodes.math('POWER', nodes.math('MAXIMUM', weight, 0), blend[0]), influence)
        color_weights.append(w)
    total = nodes.math('MAXIMUM', nodes.add(nodes.add(*color_weights[:2]), color_weights[2]), 1e-8)
    weights = [nodes.div(value, total) for value in color_weights]
    colors = [nodes.vector('SCALE', sample[0]['color'], sample[4]) for sample in samples]
    color = nodes.weighted(colors, weights)
    orm = nodes.weighted([sample[0]['orm'] for sample in samples], weights)

    nodes.section('Tangent slopes — F × transpose(J) × F', (2300, -3900))
    slopes = []
    for channels, c, s, frequency, _gain in samples:
        r, g, b = nodes.split(channels['normal'])
        denominator = nodes.math('MAXIMUM', nodes.sub(nodes.mul(b, 2), 1), .05)
        x = nodes.div(nodes.sub(nodes.mul(r, 2), 1), denominator)
        y = nodes.div(nodes.sub(nodes.mul(g, 2), 1), denominator)
        # J=sR in runtime UV. Conjugating with V reflection reverses the rotation
        # in the retained Blender tangent frame: F*J^T*F = sR.
        x_rot = nodes.mul(nodes.sub(nodes.mul(c, x), nodes.mul(s, y)), frequency)
        y_rot = nodes.mul(nodes.add(nodes.mul(s, x), nodes.mul(c, y)), frequency)
        slopes.append(nodes.xyz(x_rot, y_rot))
    xy = nodes.weighted(slopes, weights)
    x, y, _ = nodes.split(xy)
    decoded = nodes.vector('NORMALIZE', nodes.xyz(x, y, 1))
    encoded = nodes.vector('ADD', nodes.vector('SCALE', decoded, .5), (.5, .5, .5))
    for name, socket in (('Color', color), ('Normal', encoded), ('ORM', orm)):
        nodes.links.new(socket, output_node.inputs[name])
    input_node.location, output_node.location = (-350, 0), (5600, -4300)
    return group


def stochastic_material(node_tree, uv_socket, images_by_role, family):
    """Return color/encoded-normal/ORM sockets, sharing images and one node group.

    Image color spaces must already be sRGB for color, Non-Color for normal/ORM.
    The caller owns images, materials, UV maps and lifecycle. This helper only
    creates the group and one group instance in the supplied material node tree.
    """
    if family not in PRESETS:
        raise ValueError(f'Unknown surface preset: {family}')
    for role in ('color', 'normal', 'orm'):
        if role not in images_by_role:
            raise ValueError(f'Missing {family} {role} image')
    image_names = tuple(images_by_role[role].name for role in ('color', 'normal', 'orm'))
    group = next((g for g in bpy.data.node_groups
                  if g.get('stochasticVersion') == VERSION and g.get('family') == family
                  and tuple(g.get('settings', ())) == PRESETS[family][0]
                  and tuple(g.get('blend', ())) == PRESETS[family][1]
                  and tuple(g.get('sourceImages', ())) == image_names), None)
    if group is None:
        group = _build_group(family, images_by_role)
        group['sourceImages'] = list(image_names)
    instance = node_tree.nodes.new('ShaderNodeGroup')
    instance.node_tree = group
    instance.label = f'{family} / continuous regional PBR'
    node_tree.links.new(uv_socket, instance.inputs['UV'])
    return {role: instance.outputs[name] for role, name in (('color', 'Color'), ('normal', 'Normal'), ('orm', 'ORM'))}
