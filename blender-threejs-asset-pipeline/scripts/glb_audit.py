#!/usr/bin/env python3
"""Read-only restricted static GLB corner/metadata and unique-UV auditor."""
import argparse
from collections import Counter, defaultdict
import copy
import hashlib
import json
import math
from pathlib import Path
import struct
import sys

FORMATS = {5120:'b',5121:'B',5122:'h',5123:'H',5125:'I',5126:'f'}
WIDTHS = {'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}
GEOMETRY_EXTENSIONS = {'EXT_meshopt_compression','KHR_draco_mesh_compression','EXT_mesh_gpu_instancing','KHR_mesh_quantization'}


def require(condition, message):
    if not condition: raise ValueError(message)


class GLB:
    def __init__(self, data):
        self.bytes = data
        require(len(data) >= 28 and struct.unpack_from('<III', data) == (0x46546C67,2,len(data)), 'Expected a complete glTF 2 binary')
        offset, chunks = 12, []
        while offset < len(data):
            require(offset+8 <= len(data), 'Truncated chunk header')
            size, kind = struct.unpack_from('<II',data,offset)
            require(size % 4 == 0 and offset+8+size <= len(data), 'Invalid chunk length/alignment')
            chunks.append((kind,data[offset+8:offset+8+size])); offset += 8+size
        require(len(chunks) == 2 and chunks[0][0] == 0x4E4F534A and chunks[1][0] == 0x004E4942, 'Expected one JSON and one BIN chunk')
        def invalid_constant(value): raise ValueError('Nonfinite JSON number: '+value)
        self.doc, self.binary = json.loads(chunks[0][1], parse_constant=invalid_constant), chunks[1][1]
        d = self.doc
        require(d.get('asset',{}).get('version') == '2.0', 'Only glTF 2.0 is supported')
        require(not d.get('animations') and not d.get('skins'), 'Animation and skinning are unsupported')
        require(not d.get('extensionsRequired'), 'Required extensions are unsupported; decode/validate them separately')
        require(not set(d.get('extensionsUsed',[])) & GEOMETRY_EXTENSIONS, 'Compressed, quantized or instanced geometry is unsupported')
        buffers = d.get('buffers',[])
        require(len(buffers) == 1 and 'uri' not in buffers[0], 'Use one embedded buffer')
        self.buffer_length = buffers[0]['byteLength']
        require(type(self.buffer_length) is int and 0 <= len(self.binary)-self.buffer_length <= 3, 'BIN length does not match its buffer')
        nodes = d.get('nodes',[])
        require(nodes and all(isinstance(n.get('name'),str) and n['name'] for n in nodes), 'Every node requires a stable nonempty name')
        require(len({n['name'] for n in nodes}) == len(nodes), 'Node names must be unique')
        self.nodes = {n['name']:n for n in nodes}
        meshes = d.get('meshes',[]); used = []
        parents = {}
        for index,node in enumerate(nodes):
            require('skin' not in node and not node.get('weights') and not node.get('extensions'), 'Skinned, morphing or extended nodes are unsupported')
            require('matrix' not in node or not any(k in node for k in ('translation','rotation','scale')), 'Do not combine matrix and TRS')
            for key,width in (('matrix',16),('translation',3),('rotation',4),('scale',3)):
                if key in node:
                    require(isinstance(node[key],list) and len(node[key])==width and all(type(v) in (int,float) and math.isfinite(v) for v in node[key]), 'Invalid node '+key)
            if 'matrix' in node:
                require(node['matrix'][3::4] == [0,0,0,1], 'Expected an affine node matrix')
            if 'rotation' in node:
                require(abs(sum(v*v for v in node['rotation'])-1)<1e-4, 'Node quaternion must be normalized')
            require('extras' not in node or isinstance(node['extras'],dict), 'Node extras must be an object in this audit contract')
            if 'mesh' in node:
                require(type(node['mesh']) is int and 0 <= node['mesh'] < len(meshes), 'Invalid mesh reference')
                used.append(node['mesh'])
            for child in node.get('children',[]):
                require(type(child) is int and 0 <= child < len(nodes) and child not in parents, 'Invalid child or multiple parents')
                parents[child] = index
        require(used and len(set(used)) == len(used) and set(used) == set(range(len(meshes))), 'Require one node instance per mesh and no uninstantiated meshes')
        for start in range(len(nodes)):
            visited = set(); index = start
            while index in parents:
                require(index not in visited, 'Cyclic node hierarchy'); visited.add(index); index = parents[index]
        scenes = d.get('scenes',[])
        require(scenes and type(d.get('scene',0)) is int and 0 <= d.get('scene',0)<len(scenes), 'Expected a valid default scene')
        for scene in scenes:
            roots = scene.get('nodes',[])
            require(roots and all(type(i) is int and 0<=i<len(nodes) and i not in parents for i in roots) and len(set(roots))==len(roots), 'Invalid scene roots')
        self.cache = {}
        for mesh in meshes:
            require(not mesh.get('weights') and not mesh.get('extensions'), 'Morphing or extended meshes are unsupported')
            require(mesh.get('primitives'), 'Empty meshes are unsupported')
            for primitive in mesh.get('primitives',[]):
                require(not primitive.get('targets') and not primitive.get('extensions'), 'Morph/compressed/extended primitives are unsupported')
                self.primitive(primitive)

    @classmethod
    def read(cls, path): return cls(Path(path).read_bytes())

    def accessor(self, index):
        if index in self.cache: return self.cache[index]
        specs = self.doc.get('accessors',[])
        require(type(index) is int and 0 <= index < len(specs), 'Invalid accessor reference')
        spec = specs[index]
        require('sparse' not in spec and 'bufferView' in spec and not spec.get('extensions'), 'Sparse/missing/extended accessors are unsupported')
        require(spec.get('componentType') in FORMATS and spec.get('type') in WIDTHS, 'Unsupported accessor type')
        require(type(spec.get('count')) is int and spec['count'] > 0, 'Accessor count must be positive')
        views = self.doc.get('bufferViews',[]); vi = spec['bufferView']
        require(type(vi) is int and 0 <= vi < len(views), 'Invalid bufferView reference')
        view = views[vi]
        require(view.get('buffer',0) == 0 and not view.get('extensions'), 'External/compressed bufferView is unsupported')
        fmt = '<'+FORMATS[spec['componentType']]*WIDTHS[spec['type']]
        width = struct.calcsize(fmt); stride = view.get('byteStride',width)
        component_width = struct.calcsize(FORMATS[spec['componentType']])
        start, offset, length = view.get('byteOffset',0), spec.get('byteOffset',0), view['byteLength']
        require(all(type(v) is int and v >= 0 for v in (start,offset,length,stride)), 'Invalid byte offsets')
        require(stride >= width and start+length <= self.buffer_length and offset+(spec['count']-1)*stride+width <= length, 'Accessor exceeds its bufferView')
        require((start+offset)%component_width == 0 and stride%component_width == 0, 'Misaligned accessor')
        require('byteStride' not in view or (4<=stride<=252 and stride%4==0), 'Invalid vertex byteStride')
        values = [struct.unpack_from(fmt,self.binary,start+offset+i*stride) for i in range(spec['count'])]
        require(all(math.isfinite(v) for row in values for v in row), 'Nonfinite accessor values')
        if spec.get('normalized'):
            require(spec['componentType'] in (5120,5121,5122,5123), 'Invalid normalized accessor')
        result = (spec,values)
        self.cache[index] = result; return result

    def primitive(self, primitive):
        require(primitive.get('mode',4) == 4, 'Only triangle primitives are supported')
        attrs = {name:self.accessor(index) for name,index in primitive['attributes'].items()}
        require('POSITION' in attrs and attrs['POSITION'][0]['type'] == 'VEC3' and attrs['POSITION'][0]['componentType']==5126, 'POSITION must be float VEC3')
        for name,(spec,values) in attrs.items():
            if name in ('NORMAL','TANGENT'):
                require(spec['type']==('VEC3' if name=='NORMAL' else 'VEC4') and spec['componentType']==5126, name+': expected float direction attribute')
            if name.startswith('TEXCOORD_'): require(spec['type']=='VEC2', name+': expected VEC2')
        count = len(attrs['POSITION'][1])
        require(all(len(values) == count for spec,values in attrs.values()), 'Attribute counts differ')
        if 'indices' in primitive:
            spec,values = self.accessor(primitive['indices'])
            require(spec['type'] == 'SCALAR' and spec['componentType'] in (5121,5123,5125) and not spec.get('normalized'), 'Invalid index accessor')
            indices = [row[0] for row in values]
        else: indices = list(range(count))
        require(indices and len(indices)%3 == 0 and max(indices)<count, 'Invalid triangle indices')
        if 'material' in primitive:
            require(type(primitive['material']) is int and 0 <= primitive['material'] < len(self.doc.get('materials',[])), 'Invalid material reference')
        return attrs,indices

    def triangles(self, node, omit=()):
        for primitive in self.doc['meshes'][node['mesh']]['primitives']:
            attrs,indices = self.primitive(primitive)
            metadata = {k:v for k,v in primitive.items() if k not in ('attributes','indices','mode')}
            metadata['mode'] = 4
            material = json.dumps(metadata,sort_keys=True,separators=(',',':'))
            names = sorted(set(attrs)-set(omit))
            for start in range(0,len(indices),3):
                corners = []
                for index in indices[start:start+3]:
                    corner = []
                    for name in names:
                        spec,values = attrs[name]
                        raw = struct.pack('<'+FORMATS[spec['componentType']]*WIDTHS[spec['type']],*values[index])
                        corner.append((name,spec['componentType'],spec['type'],bool(spec.get('normalized')),raw))
                    corners.append(tuple(corner))
                rotation = min(range(3),key=lambda i:corners[i:]+corners[:i])
                yield material,tuple(corners[rotation:]+corners[:rotation])


def node_contract(glb, node, allowed):
    result = copy.deepcopy(node); result.pop('mesh',None)
    result['children'] = [glb.doc['nodes'][i]['name'] for i in node.get('children',[])]
    result['extras'] = {k:v for k,v in node.get('extras',{}).items() if k not in allowed}
    if 'mesh' in node:
        result['meshMetadata'] = {k:v for k,v in glb.doc['meshes'][node['mesh']].items() if k not in ('primitives','name')}
    return result


def scene_contract(glb):
    result = []
    for scene in glb.doc.get('scenes',[]):
        record = copy.deepcopy(scene)
        record['nodes'] = [glb.doc['nodes'][i]['name'] for i in scene.get('nodes',[])]
        result.append(record)
    return glb.doc.get('scene',0),result


def compare(source, candidate, allow_added=(), allow_extra_keys=()):
    errors = []
    for key in ('asset','extras','materials','images','textures','samplers','extensions','extensionsUsed','extensionsRequired'):
        if source.doc.get(key) != candidate.doc.get(key): errors.append(key+' changed')
    def embedded_images(glb):
        payloads=[]
        for image in glb.doc.get('images',[]):
            if 'bufferView' not in image: continue
            view=glb.doc['bufferViews'][image['bufferView']]
            start,length=view.get('byteOffset',0),view['byteLength']
            require(view.get('buffer',0)==0 and type(start) is int and type(length) is int and start>=0 and length>=0 and start+length<=glb.buffer_length, 'Invalid embedded image bufferView')
            payloads.append(glb.binary[start:start+length])
        return payloads
    if embedded_images(source)!=embedded_images(candidate): errors.append('Embedded image bytes changed')
    if scene_contract(source) != scene_contract(candidate): errors.append('Scene membership/order changed')
    if source.nodes.keys() != candidate.nodes.keys(): errors.append('Node identities changed')
    for name in source.nodes.keys() & candidate.nodes.keys():
        a,b = source.nodes[name],candidate.nodes[name]
        if ('mesh' in a) != ('mesh' in b) or node_contract(source,a,allow_extra_keys) != node_contract(candidate,b,allow_extra_keys):
            errors.append(name+': metadata, hierarchy or transform changed')
        if 'mesh' not in a or 'mesh' not in b: continue
        source_names = set().union(*(p['attributes'] for p in source.doc['meshes'][a['mesh']]['primitives']))
        candidate_names = set().union(*(p['attributes'] for p in candidate.doc['meshes'][b['mesh']]['primitives']))
        extras = candidate_names-source_names
        if not extras <= set(allow_added): errors.append(name+': undeclared added attributes '+str(sorted(extras)))
        if Counter(source.triangles(a)) != Counter(candidate.triangles(b,extras)):
            errors.append(name+': triangle corners, winding, channels or material binding changed')
    return dict(passed=not errors, errors=errors, sourceSHA256=hashlib.sha256(source.bytes).hexdigest(), candidateSHA256=hashlib.sha256(candidate.bytes).hexdigest(),
                allowedAddedAttributes=list(allow_added), allowedNodeExtraKeys=list(allow_extra_keys))


def signed_area(points):
    return sum(a[0]*b[1]-a[1]*b[0] for a,b in zip(points,points[1:]+points[:1]))/2


def overlap_area(first, second):
    polygon = list(first); orientation = 1 if signed_area(second)>0 else -1
    for a,b in zip(second,second[1:]+second[:1]):
        def distance(p): return orientation*((b[0]-a[0])*(p[1]-a[1])-(b[1]-a[1])*(p[0]-a[0]))
        clipped = []
        if not polygon: return 0.0
        for p,q in zip(polygon,polygon[1:]+polygon[:1]):
            dp,dq = distance(p),distance(q)
            if dp>=0: clipped.append(p)
            if (dp>=0)!=(dq>=0):
                t=dp/(dp-dq); clipped.append(tuple(p[i]+(q[i]-p[i])*t for i in (0,1)))
        polygon=clipped
    return abs(signed_area(polygon)) if len(polygon)>=3 else 0.0


def numeric(spec, row):
    if not spec.get('normalized'): return row
    limits = {5120:127,5121:255,5122:32767,5123:65535}
    return tuple(max(-1,v/limits[spec['componentType']]) for v in row)


def uv_audit(glb, channel):
    triangles, labels, errors = [], [], []
    for name,node in glb.nodes.items():
        if 'mesh' not in node: continue
        for pi,primitive in enumerate(glb.doc['meshes'][node['mesh']]['primitives']):
            attrs,indices = glb.primitive(primitive)
            require(channel in attrs and attrs[channel][0]['type']=='VEC2', name+': requested UV channel missing or not VEC2')
            spec,values = attrs[channel]; uv = [numeric(spec,row) for row in values]
            pos = attrs['POSITION'][1]
            for start in range(0,len(indices),3):
                ids=indices[start:start+3]; triangle=[uv[i] for i in ids]; label=dict(node=name,primitive=pi,triangle=start//3)
                if any(v < -1e-6 or v > 1+1e-6 for p in triangle for v in p): errors.append(dict(**label,reason='UV outside 0..1'))
                ab,ac = [[pos[ids[j]][k]-pos[ids[0]][k] for k in range(3)] for j in (1,2)]
                area = math.sqrt(sum((ab[(k+1)%3]*ac[(k+2)%3]-ab[(k+2)%3]*ac[(k+1)%3])**2 for k in range(3)))/2
                if area>1e-12 and abs(signed_area(triangle))<=1e-16: errors.append(dict(**label,reason='Collapsed UV on physical triangle'))
                triangles.append(triangle); labels.append(label)
    bins=defaultdict(list); examples=[]; overlap_count=0; total_area=0.0
    for index,triangle in enumerate(triangles):
        area=abs(signed_area(triangle)); total_area+=area
        if area<=1e-16: continue
        lo=[max(0,min(31,int(min(p[k] for p in triangle)*32))) for k in (0,1)]
        hi=[max(0,min(31,int(max(p[k] for p in triangle)*32))) for k in (0,1)]
        cells=[(x,y) for x in range(lo[0],hi[0]+1) for y in range(lo[1],hi[1]+1)]
        candidates=set()
        for cell in cells: candidates.update(bins[cell])
        for other in candidates:
            overlap=overlap_area(triangles[other],triangle)
            if overlap>1e-12:
                overlap_count+=1
                if len(examples)<20: examples.append(dict(first=labels[other],second=labels[index],area=overlap))
        for cell in cells: bins[cell].append(index)
    return dict(passed=not errors and overlap_count==0, complete=True, channel=channel, triangles=len(triangles), areaSum=total_area, errors=errors, overlapCount=overlap_count, overlapExamples=examples)


def inspect(glb):
    count=0; channels=set()
    for mesh in glb.doc['meshes']:
        for primitive in mesh['primitives']:
            attrs,indices=glb.primitive(primitive); count+=len(indices)//3; channels.update(attrs)
    return dict(passed=True, sha256=hashlib.sha256(glb.bytes).hexdigest(), nodes=len(glb.nodes), meshes=len(glb.doc['meshes']), triangles=count, attributes=sorted(channels), scope='restricted static embedded uncompressed triangle GLB')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    sub=parser.add_subparsers(dest='mode',required=True)
    one=sub.add_parser('inspect'); one.add_argument('source'); one.add_argument('--uv')
    two=sub.add_parser('compare'); two.add_argument('source'); two.add_argument('candidate'); two.add_argument('--uv')
    two.add_argument('--allow-added',action='append',default=[]); two.add_argument('--allow-extra-key',action='append',default=[])
    args=parser.parse_args()
    try:
        source=GLB.read(args.source); target=GLB.read(args.candidate) if args.mode=='compare' else source
        report=compare(source,target,args.allow_added,args.allow_extra_key) if args.mode=='compare' else inspect(source)
        if args.uv:
            report['uvAudit']=uv_audit(target,args.uv); report['passed']=report['passed'] and report['uvAudit']['passed']
        print(json.dumps(report,indent=2,allow_nan=False)); return 0 if report['passed'] else 1
    except (ValueError,KeyError,TypeError,OSError,IndexError,struct.error) as error:
        print(json.dumps({'error':str(error)}),file=sys.stderr); return 2


if __name__ == '__main__': sys.exit(main())
