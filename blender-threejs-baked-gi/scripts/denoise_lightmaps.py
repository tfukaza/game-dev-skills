"""Geometry-guarded denoising of linear diffuse lighting, never material color.

Only NumPy and the standard library are required. Default guide orientation is
Blender bottom-up, reflected from glTF TEXCOORD_2. Both choices are configurable.
The API never overwrites inputs. The CLI writes a separate NPY and optional NPZ
guides; raw EXRs, explicit coverage, padding and encoding remain caller-owned.
"""
from pathlib import Path
import json
import math
import struct
import argparse

import numpy as np


_DTYPES = {5120: 'i1', 5121: 'u1', 5122: '<i2', 5123: '<u2', 5125: '<u4', 5126: '<f4'}
_WIDTHS = {'SCALAR': 1, 'VEC2': 2, 'VEC3': 3, 'VEC4': 4, 'MAT4': 16}


def _read_glb(path):
    data = Path(path).read_bytes()
    if len(data) < 28 or struct.unpack_from('<III', data) != (0x46546C67, 2, len(data)):
        raise ValueError('Expected a complete glTF 2 binary donor')
    document, binary, offset = None, None, 12
    while offset + 8 <= len(data):
        size, kind = struct.unpack_from('<II', data, offset)
        if size % 4 or offset + 8 + size > len(data):
            raise ValueError('Invalid GLB chunk length')
        payload = data[offset + 8:offset + 8 + size]
        if kind == 0x4E4F534A:
            document = json.loads(payload)
        elif kind == 0x004E4942:
            binary = payload
        offset += 8 + size
    if offset != len(data) or document is None or binary is None:
        raise ValueError('Expected embedded JSON and BIN chunks')
    if document.get('asset', {}).get('version') != '2.0' or document.get('extensionsRequired'):
        raise ValueError('Use an audited glTF 2 donor without required extensions')
    if document.get('skins') or document.get('animations'):
        raise ValueError('Skinning and animation are unsupported; export a static donor')
    buffers = document.get('buffers', [])
    if len(buffers) != 1 or 'uri' in buffers[0] or buffers[0].get('byteLength', 0) > len(binary):
        raise ValueError('Donor must use one embedded buffer')
    return document, binary


def _accessor(document, binary, index):
    spec = document['accessors'][index]
    if 'sparse' in spec or 'bufferView' not in spec:
        raise ValueError('Sparse donor accessors are unsupported')
    if spec.get('extensions'):
        raise ValueError('Accessor extensions are unsupported')
    view = document['bufferViews'][spec['bufferView']]
    if view.get('buffer', 0) != 0 or view.get('extensions'):
        raise ValueError('Use an embedded, uncompressed donor buffer')
    if spec.get('componentType') not in _DTYPES or spec.get('type') not in _WIDTHS:
        raise ValueError('Unsupported accessor component or shape')
    dtype, width = np.dtype(_DTYPES[spec['componentType']]), _WIDTHS[spec['type']]
    count = spec.get('count', 0)
    stride = view.get('byteStride', dtype.itemsize * width)
    within = spec.get('byteOffset', 0)
    start = view.get('byteOffset', 0) + within
    end = start + (count - 1) * stride + dtype.itemsize * width
    if (not isinstance(count, int) or count <= 0 or stride < dtype.itemsize * width
            or within < 0 or start < 0 or end > len(binary)
            or end > view.get('byteOffset', 0) + view['byteLength']):
        raise ValueError('Accessor exceeds its buffer view')
    values = np.ndarray((spec['count'], width), dtype=dtype, buffer=binary,
                        offset=view.get('byteOffset', 0) + spec.get('byteOffset', 0),
                        strides=(view.get('byteStride', dtype.itemsize * width), dtype.itemsize))
    if spec.get('normalized') and dtype.kind in 'iu':
        info = np.iinfo(dtype)
        return np.maximum(values.astype(np.float64) / info.max, -1)
    return values


def _local_matrix(node):
    if 'matrix' in node:
        return np.asarray(node['matrix'], dtype=np.float64).reshape(4, 4).T
    x, y, z, w = node.get('rotation', [0, 0, 0, 1])
    matrix = np.eye(4, dtype=np.float64)
    matrix[:3, :3] = [[1 - 2 * (y*y + z*z), 2 * (x*y - z*w), 2 * (x*z + y*w)],
                      [2 * (x*y + z*w), 1 - 2 * (x*x + z*z), 2 * (y*z - x*w)],
                      [2 * (x*z - y*w), 2 * (y*z + x*w), 1 - 2 * (x*x + y*y)]]
    matrix[:3, :3] *= np.asarray(node.get('scale', [1, 1, 1]))[None, :]
    matrix[:3, 3] = node.get('translation', [0, 0, 0])
    return matrix


def _triangles(document, binary, uv_channel=2, flip_v=True):
    nodes = document['nodes']
    children = {child for node in nodes for child in node.get('children', [])}
    roots = document.get('scenes', [{}])[document.get('scene', 0)].get('nodes',
                    [index for index in range(len(nodes)) if index not in children])
    positions, normals, uvs, owners = [], [], [], []
    visited = set()
    semantic = f'TEXCOORD_{uv_channel}'

    def visit(index, parent):
        if index in visited:
            raise ValueError('Repeated or cyclic donor node hierarchy')
        visited.add(index)
        node = nodes[index]
        if 'skin' in node or 'weights' in node or node.get('extensions'):
            raise ValueError('Skinned, morphed or extended nodes are unsupported')
        matrix = parent @ _local_matrix(node)
        if not np.isfinite(matrix).all() or abs(np.linalg.det(matrix[:3, :3])) < 1e-12:
            raise ValueError('Non-finite or singular donor transform')
        if 'mesh' in node:
            normal_matrix = np.linalg.inv(matrix[:3, :3]).T
            mesh = document['meshes'][node['mesh']]
            if mesh.get('weights') or mesh.get('extensions'):
                raise ValueError('Morph weights and mesh extensions are unsupported')
            for primitive in mesh['primitives']:
                if primitive.get('targets') or primitive.get('extensions'):
                    raise ValueError('Morphed or extended primitives are unsupported')
                if primitive.get('mode', 4) != 4 or semantic not in primitive['attributes']:
                    raise ValueError('Every receiver needs triangles and ' + semantic)
                attrs = primitive['attributes']
                local = _accessor(document, binary, attrs['POSITION']).astype(np.float64)
                world = local @ matrix[:3, :3].T + matrix[:3, 3]
                uv = _accessor(document, binary, attrs[semantic]).astype(np.float64).copy()
                if local.shape[1] != 3 or uv.shape != (len(local), 2):
                    raise ValueError('Positions and atlas UVs have mismatched shapes')
                if flip_v:
                    uv[:, 1] = 1 - uv[:, 1]
                if 'indices' in primitive:
                    index_spec = document['accessors'][primitive['indices']]
                    if index_spec.get('type') != 'SCALAR' or index_spec.get('componentType') not in (5121, 5123, 5125) or index_spec.get('normalized'):
                        raise ValueError('Indices must be unsigned, unnormalized SCALAR accessors')
                indices = (_accessor(document, binary, primitive['indices']).reshape(-1)
                           if 'indices' in primitive else np.arange(len(local)))
                if indices.dtype.kind not in 'iu' or len(indices) % 3 or indices.min() < 0 or indices.max() >= len(local):
                    raise ValueError('Invalid triangle indices')
                ids = indices.reshape(-1, 3)
                p = world[ids]
                if 'NORMAL' in attrs:
                    n = _accessor(document, binary, attrs['NORMAL']) @ normal_matrix.T
                    if n.shape != local.shape or not np.isfinite(n).all() or (np.linalg.norm(n, axis=1) < 1e-12).any():
                        raise ValueError('Invalid donor normals')
                    n /= np.maximum(np.linalg.norm(n, axis=1, keepdims=True), 1e-20)
                    n = n[ids]
                else:
                    n = np.cross(p[:, 1] - p[:, 0], p[:, 2] - p[:, 0])
                    # World-edge winding flips under reflections; match local
                    # face normals transformed by inverse transpose instead.
                    if np.linalg.det(matrix[:3, :3]) < 0:
                        n *= -1
                    if (np.linalg.norm(n, axis=1) < 1e-12).any():
                        raise ValueError('Degenerate receiver geometry')
                    n /= np.maximum(np.linalg.norm(n, axis=1, keepdims=True), 1e-20)
                    n = np.repeat(n[:, None, :], 3, axis=1)
                positions.append(p); normals.append(n); uvs.append(uv[ids])
                owners.extend([index] * len(ids))
        for child in node.get('children', []):
            visit(child, matrix)

    for index in roots:
        visit(index, np.eye(4))
    if not positions:
        raise ValueError('Donor has no receivers')
    return np.concatenate(positions), np.concatenate(normals), np.concatenate(uvs), owners


def _chart_ids(positions, uvs, owners, world_tolerance=1e-5, uv_tolerance=1e-7):
    """Join only edges that share physical positions and UVs within one object.

    Exported normals/material seams can duplicate vertices within one UV chart.
    Quantization only absorbs float export roundoff; distant atlas neighbors never
    become connected merely because their UV edge coordinates happen to touch.
    """
    parent = list(range(len(uvs)))
    edges = {}

    def find(index):
        while parent[index] != index:
            parent[index] = parent[parent[index]]
            index = parent[index]
        return index

    keys = np.rint(np.concatenate((positions / world_tolerance, uvs / uv_tolerance), axis=2)).astype(np.int64)
    for index, vertices in enumerate(keys):
        vertices = [tuple(vertex) for vertex in vertices]
        for a, b in ((0, 1), (1, 2), (2, 0)):
            key = (owners[index], *sorted((vertices[a], vertices[b])))
            if key in edges:
                parent[find(index)] = find(edges[key])
            else:
                edges[key] = index
    remap = {}
    result = np.empty(len(parent), dtype=np.int32)
    for index in range(len(parent)):
        root = find(index)
        result[index] = remap.setdefault(root, len(remap))
    return result


def rasterize_guides(donor_path, size, *, uv_channel=2, flip_v=True, world_tolerance=1e-5, uv_tolerance=1e-7):
    """Return world position/normal, chart_id, texel_size and coverage arrays.

    Coverage is the UV triangle pixel-center raster, not Cycles' authoritative
    bake mask. Intersect it with raw sky-pass coverage when integrating. Alpha in
    a combined lighting image is AO and must never be used as a coverage mask.
    """
    if not isinstance(size, (int, np.integer)) or size <= 0:
        raise ValueError('Size must be a positive square atlas resolution')
    if not isinstance(uv_channel, int) or uv_channel < 0:
        raise ValueError('UV channel must be a nonnegative integer')
    if any(not math.isfinite(v) or v <= 0 for v in (world_tolerance, uv_tolerance)):
        raise ValueError('Chart tolerances must be finite and positive')
    document, binary = _read_glb(donor_path)
    positions, normals, uvs, owners = _triangles(document, binary, uv_channel, flip_v)
    if not np.isfinite(positions).all() or not np.isfinite(uvs).all() or uvs.min() < -1e-5 or uvs.max() > 1 + 1e-5:
        raise ValueError('Invalid donor positions or atlas UV bounds')
    charts = _chart_ids(positions, uvs, owners, world_tolerance, uv_tolerance)
    guides = {'position': np.zeros((size, size, 3), np.float32),
              'normal': np.zeros((size, size, 3), np.float32),
              'chart_id': np.full((size, size), -1, np.int32),
              'texel_size': np.zeros((size, size), np.float32)}
    for p, n, uv, chart in zip(positions, normals, uvs, charts):
        pixel = uv * size
        low = np.maximum(np.ceil(pixel.min(axis=0) - .5).astype(int), 0)
        high = np.minimum(np.floor(pixel.max(axis=0) - .5).astype(int), size - 1)
        if np.any(high < low):
            continue
        delta = np.stack((pixel[1] - pixel[0], pixel[2] - pixel[0]), axis=1)
        det = np.linalg.det(delta)
        if abs(det) < 1e-12:
            continue
        inverse = np.linalg.inv(delta)
        xs, ys = np.meshgrid(np.arange(low[0], high[0] + 1) + .5, np.arange(low[1], high[1] + 1) + .5)
        a = (xs - pixel[0, 0]) * inverse[0, 0] + (ys - pixel[0, 1]) * inverse[0, 1]
        b = (xs - pixel[0, 0]) * inverse[1, 0] + (ys - pixel[0, 1]) * inverse[1, 1]
        inside = (a >= -1e-7) & (b >= -1e-7) & (a + b <= 1 + 1e-7)
        if not inside.any():
            continue
        area = np.s_[low[1]:high[1] + 1, low[0]:high[0] + 1]
        previous = guides['chart_id'][area]
        if np.any(inside & (previous >= 0) & (previous != chart)):
            raise ValueError('UV2 chart interiors overlap at a texel; use an audited donor')
        weights = np.stack((1 - a - b, a, b), axis=-1)
        world = weights @ p
        normal = weights @ n
        normal /= np.maximum(np.linalg.norm(normal, axis=2, keepdims=True), 1e-20)
        # Maximum world-space pixel-axis footprint bounds anisotropic charts.
        jacobian = np.stack((p[1] - p[0], p[2] - p[0]), axis=1) @ inverse
        footprint = max(np.linalg.norm(jacobian[:, 0]), np.linalg.norm(jacobian[:, 1]), 1e-8)
        guides['position'][area][inside] = world[inside]
        guides['normal'][area][inside] = normal[inside]
        guides['chart_id'][area][inside] = chart
        guides['texel_size'][area][inside] = footprint
    guides['coverage'] = guides['chart_id'] >= 0
    return guides


def _noise_estimate(luminance, guides, valid):
    differences = []
    for dy, dx in ((0, 1), (1, 0)):
        a = np.s_[dy:, dx:]
        b = np.s_[:luminance.shape[0] - dy, :luminance.shape[1] - dx]
        eligible = valid[a] & valid[b] & (guides['chart_id'][a] == guides['chart_id'][b])
        eligible &= np.sum(guides['normal'][a] * guides['normal'][b], axis=2) > .97
        values = np.abs(luminance[a] - luminance[b])[eligible]
        if len(values):
            differences.append(values[::max(1, len(values) // 100000)])
    if not differences:
        return .001
    # Median absolute differences of independent Gaussian samples: sqrt(2)*MAD.
    return max(.001, float(np.median(np.concatenate(differences))) / .95387255)


def _chart_noise_estimate(luminance, guides, valid):
    """Keep unlit/internal charts from suppressing the noise estimate elsewhere.

    Exactly black pairs carry no information about Monte Carlo variance in the
    illuminated part of a chart. Excluding those pairs also handles a continuous
    chart whose hidden underside occupies most of its area. Actual black pixels
    still participate in filtering under the unchanged geometric/edge guards.
    """
    differences, chart_ids = [], []
    for dy, dx in ((0, 1), (1, 0)):
        a = np.s_[dy:, dx:]
        b = np.s_[:luminance.shape[0] - dy, :luminance.shape[1] - dx]
        eligible = valid[a] & valid[b] & (guides['chart_id'][a] == guides['chart_id'][b])
        eligible &= np.sum(guides['normal'][a] * guides['normal'][b], axis=2) > .97
        distance2 = np.sum((guides['position'][a] - guides['position'][b]) ** 2, axis=2)
        footprint = np.maximum(guides['texel_size'][a], guides['texel_size'][b])
        eligible &= distance2 <= (footprint * 2.5) ** 2
        eligible &= np.maximum(luminance[a], luminance[b]) > 1e-6
        values = np.abs(luminance[a] - luminance[b])[eligible]
        if len(values):
            # Bound sorting memory on large atlases without privileging a chart.
            stride = max(1, len(values) // 1000000)
            differences.append(values[::stride])
            chart_ids.append(guides['chart_id'][a][eligible][::stride])
    result = np.full(luminance.shape, .001, np.float32)
    if not differences:
        return result
    differences, chart_ids = np.concatenate(differences), np.concatenate(chart_ids)
    order = np.argsort(chart_ids, kind='stable')
    ids, starts, counts = np.unique(chart_ids[order], return_index=True, return_counts=True)
    values = differences[order]
    sigma_by_chart = np.full(int(guides['chart_id'][valid].max()) + 1, .001, np.float32)
    for chart, start, count in zip(ids, starts, counts):
        if count >= 6:
            sigma_by_chart[chart] = max(.001, float(np.median(values[start:start + count])) / .95387255)
    result[valid] = sigma_by_chart[guides['chart_id'][valid]]
    return result


def _finite_neighbor_median(samples, count):
    ordered = np.sort(np.where(np.isfinite(samples), samples, np.inf), axis=0)
    index = count.reshape((1, len(count)) + (1,) * (samples.ndim - 2))
    low = np.take_along_axis(ordered, (index - 1) // 2, axis=0)[0]
    high = np.take_along_axis(ordered, index // 2, axis=0)[0]
    return (low + high) * .5


def _prefilter_fireflies(rgb, guides, valid, row_chunk=64):
    """Replace isolated positive transport outliers using a coherent local RGB.

    A bright edge, thin light strip or smooth maximum has at least two nearby
    samples supporting its brightness. An isolated Monte Carlo spike does not.
    All statistics use only the same chart and physical tangent neighborhood;
    sparse chart borders are left unchanged rather than borrowing another face.
    """
    output = rgb.copy()
    height, width = valid.shape
    luma = np.array([.2126, .7152, .0722], np.float32)
    for y0 in range(0, height, row_chunk):
        y1 = min(height, y0 + row_chunk)
        if not valid[y0:y1].any():
            continue
        neighbors = np.full((8, y1 - y0, width, 3), np.nan, np.float32)
        tap = 0
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                if not dx and not dy:
                    continue
                cy0, cy1 = max(y0, -dy), min(y1, height - dy)
                cx0, cx1 = max(0, -dx), min(width, width - dx)
                if cy0 < cy1 and cx0 < cx1:
                    center = np.s_[cy0:cy1, cx0:cx1]
                    neighbor = np.s_[cy0 + dy:cy1 + dy, cx0 + dx:cx1 + dx]
                    local = np.s_[cy0 - y0:cy1 - y0, cx0:cx1]
                    allowed = valid[center] & valid[neighbor]
                    allowed &= guides['chart_id'][center] == guides['chart_id'][neighbor]
                    allowed &= np.sum(guides['normal'][center] * guides['normal'][neighbor], axis=2) >= .92
                    distance2 = np.sum((guides['position'][center] - guides['position'][neighbor]) ** 2, axis=2)
                    footprint = np.maximum(guides['texel_size'][center], guides['texel_size'][neighbor])
                    allowed &= distance2 <= (footprint ** 2) * (dx * dx + dy * dy) * 6.25
                    neighbors[tap][local] = np.where(allowed[:, :, None], rgb[neighbor], np.nan)
                tap += 1
        neighbor_luma = neighbors @ luma
        count = np.isfinite(neighbor_luma).sum(axis=0)
        eligible = valid[y0:y1] & (count >= 6)
        if not eligible.any():
            continue
        # Work only on coherent covered pixels. Sorting eight values directly
        # avoids masked-array reductions over millions of empty atlas texels.
        neighbor_luma = neighbor_luma[:, eligible]
        counts = count[eligible]
        median = _finite_neighbor_median(neighbor_luma, counts)
        sigma = 1.4826 * _finite_neighbor_median(np.abs(neighbor_luma - median), counts)
        local_rgb = _finite_neighbor_median(neighbors[:, eligible], counts)
        source = rgb[y0:y1][eligible]
        center_luma = source @ luma
        excess = center_luma - median
        threshold = np.maximum(np.maximum(2.75 * sigma, .04 * np.abs(median)), .003)
        support = (neighbor_luma >= median + excess * .5).sum(axis=0)
        isolated = (excess > threshold) & (support < 2)
        output[y0:y1][eligible] = np.where(isolated[:, None], local_rgb, source)
    return output


def denoise_with_guides(values, guides, *, steps=(1, 2, 4), noise_sigma=None, row_chunk=128, prefilter=True):
    """Denoise covered linear RGB at three scales; preserve input alpha exactly.

    Isolated positive fireflies are removed before luminance edge guidance is
    fixed, so an outlier cannot protect itself through every bilateral pass.
    Chart equality is a hard gate. Normal and physical-distance gates prevent a
    connected chart folding across a corner from carrying unrelated illumination.
    Invalid/uncovered pixels stay untouched for the caller's padding stage.
    """
    source = np.asarray(values)
    if source.ndim != 3 or source.shape[2] != 4 or source.dtype.kind != 'f' or not np.isfinite(source).all():
        raise ValueError('Lighting must be a finite floating-point H×W×4 array')
    shape = source.shape[:2]
    for name, expected in (('position', (*shape, 3)), ('normal', (*shape, 3)),
                           ('chart_id', shape), ('texel_size', shape), ('coverage', shape)):
        if np.asarray(guides[name]).shape != expected:
            raise ValueError('Guide shape mismatch: ' + name)
    if guides['coverage'].dtype != np.bool_ or guides['chart_id'].dtype.kind not in 'iu':
        raise ValueError('Coverage must be boolean and chart IDs integer')
    valid = np.asarray(guides['coverage'], dtype=bool) & (guides['chart_id'] >= 0)
    valid &= guides['texel_size'] > 0
    if any(not np.isfinite(guides[key][valid]).all() for key in ('position', 'normal', 'texel_size')):
        raise ValueError('Covered geometry guides must be finite')
    if valid.any() and not np.allclose(np.linalg.norm(guides['normal'][valid], axis=1), 1, atol=.01):
        raise ValueError('Covered guide normals must be unit vectors')
    if not isinstance(row_chunk, (int, np.integer)) or row_chunk <= 0 or any(not isinstance(step, (int, np.integer)) or step <= 0 for step in steps):
        raise ValueError('Filter scales and row chunk must be positive integers')
    output = source.copy()
    if not valid.any():
        return output
    # External guide IDs may be sparse. Compact without changing the input or
    # allowing a huge numeric ID to allocate an equally huge lookup array.
    guides = dict(guides)
    charts = np.full(shape, -1, np.int32)
    charts[valid] = np.unique(guides['chart_id'][valid], return_inverse=True)[1]
    guides['chart_id'] = charts
    rgb = source[:, :, :3].astype(np.float32, copy=True)
    if prefilter:
        rgb = _prefilter_fireflies(rgb, guides, valid, min(row_chunk, 64))
    raw_luminance = rgb @ np.array([.2126, .7152, .0722], dtype=np.float32)
    if noise_sigma is None:
        sigma = _chart_noise_estimate(raw_luminance, guides, valid)
    else:
        value = float(noise_sigma)
        if not math.isfinite(value) or value < 0:
            raise ValueError('Noise sigma must be finite and nonnegative')
        sigma = np.full(shape, value, np.float32)
    height, width = shape
    for step in steps:
        filtered = rgb.copy()
        for y0 in range(0, height, row_chunk):
            y1 = min(height, y0 + row_chunk)
            total = rgb[y0:y1].copy() * 4
            weight_sum = np.full((y1 - y0, width), 4, np.float32)
            for oy in (-1, 0, 1):
                for ox in (-1, 0, 1):
                    if not ox and not oy:
                        continue
                    dy, dx = oy * step, ox * step
                    cy0, cy1 = max(y0, -dy), min(y1, height - dy)
                    cx0, cx1 = max(0, -dx), min(width, width - dx)
                    if cy0 >= cy1 or cx0 >= cx1:
                        continue
                    center = np.s_[cy0:cy1, cx0:cx1]
                    neighbor = np.s_[cy0 + dy:cy1 + dy, cx0 + dx:cx1 + dx]
                    local = np.s_[cy0 - y0:cy1 - y0, cx0:cx1]
                    allowed = valid[center] & valid[neighbor]
                    allowed &= guides['chart_id'][center] == guides['chart_id'][neighbor]
                    normal_dot = np.sum(guides['normal'][center] * guides['normal'][neighbor], axis=2)
                    allowed &= normal_dot >= .92
                    distance2 = np.sum((guides['position'][center] - guides['position'][neighbor]) ** 2, axis=2)
                    footprint = np.maximum(guides['texel_size'][center], guides['texel_size'][neighbor])
                    spatial2 = np.maximum((footprint * step) ** 2 * (ox*ox + oy*oy), 1e-16)
                    allowed &= distance2 <= spatial2 * 6.25
                    delta = raw_luminance[center] - raw_luminance[neighbor]
                    sigma_l = np.maximum(1.8 * np.maximum(sigma[center], sigma[neighbor]), .04 * np.maximum(np.abs(raw_luminance[center]), np.abs(raw_luminance[neighbor]))) + 1e-5
                    allowed &= np.abs(delta) <= sigma_l * 3
                    exponent = -.5 * (delta / sigma_l) ** 2 - .5 * distance2 / spatial2
                    exponent -= np.maximum(0, 1 - normal_dot) * 48
                    weight = np.where(allowed, np.exp(np.maximum(exponent, -80)), 0).astype(np.float32)
                    weight *= 2 if not ox or not oy else 1
                    total[local] += rgb[neighbor] * weight[:, :, None]
                    weight_sum[local] += weight
            filtered[y0:y1] = total / weight_sum[:, :, None]
        rgb[valid] = filtered[valid]
    output[:, :, :3][valid] = rgb[valid]
    return output


def denoise_lighting(values, donor_path, size, *, uv_channel=2, flip_v=True):
    """Convenience API; cache rasterize_guides separately when filtering presets."""
    if np.asarray(values).shape != (size, size, 4):
        raise ValueError('Values must match the square donor raster size')
    return denoise_with_guides(values, rasterize_guides(donor_path, size, uv_channel=uv_channel, flip_v=flip_v))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path, help='Raw finite linear H×W×4 floating NPY; alpha is preserved')
    parser.add_argument('output', type=Path, help='New filtered NPY; existing files are never replaced')
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument('--guides', type=Path, help='NPZ containing position, normal, chart_id, texel_size, coverage')
    source.add_argument('--donor', type=Path, help='Static, uncompressed, audited embedded GLB')
    parser.add_argument('--coverage', type=Path, required=True, help='Authoritative boolean raw bake-coverage NPY; never AO alpha')
    parser.add_argument('--uv-channel', type=int, default=2)
    parser.add_argument('--keep-gltf-v', action='store_true', help='Use glTF V directly instead of Blender bottom-up reflection')
    parser.add_argument('--save-guides', type=Path, help='Write new NPZ guides after intersecting actual coverage')
    parser.add_argument('--noise-sigma', type=float)
    parser.add_argument('--no-firefly', action='store_true', help='Diagnostic comparison; retain isolated high samples')
    parser.add_argument('--row-chunk', type=int, default=128)
    args = parser.parse_args()
    if args.output.exists() or (args.save_guides and args.save_guides.exists()):
        parser.error('Output already exists; choose new paths to preserve earlier results')
    values = np.load(args.input, allow_pickle=False)
    coverage = np.load(args.coverage, allow_pickle=False)
    if coverage.dtype != np.bool_ or coverage.shape != values.shape[:2]:
        parser.error('Coverage must be a boolean H×W NPY matching the lighting')
    if args.guides:
        with np.load(args.guides, allow_pickle=False) as data:
            guides = {key: data[key] for key in ('position', 'normal', 'chart_id', 'texel_size', 'coverage')}
    else:
        if values.ndim != 3 or values.shape[0] != values.shape[1]:
            parser.error('Donor rasterization supports square atlases; use NPZ guides for rectangles')
        guides = rasterize_guides(args.donor, values.shape[0], uv_channel=args.uv_channel, flip_v=not args.keep_gltf_v)
    guides['coverage'] &= coverage
    result = denoise_with_guides(values, guides, noise_sigma=args.noise_sigma, row_chunk=args.row_chunk, prefilter=not args.no_firefly)
    with args.output.open('xb') as stream:
        np.save(stream, result, allow_pickle=False)
    if args.save_guides:
        with args.save_guides.open('xb') as stream:
            np.savez_compressed(stream, **guides)
    print(json.dumps({'shape': list(result.shape), 'covered': int(guides['coverage'].sum()),
                      'alphaUnchanged': bool(np.array_equal(result[:, :, 3], values[:, :, 3])),
                      'rawInputPreserved': True, 'output': str(args.output)}))


if __name__ == '__main__':
    main()
