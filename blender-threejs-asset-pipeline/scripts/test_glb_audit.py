"""Small generated fixtures; no Blender, network or third-party dependencies."""
import json
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import unittest

from glb_audit import GLB, compare, inspect, uv_audit


def pack(doc, binary):
    payload=json.dumps(doc,separators=(',',':')).encode(); payload+=b' '*((-len(payload))%4)
    binary+=b'\0'*((-len(binary))%4)
    chunks=struct.pack('<II',len(payload),0x4E4F534A)+payload+struct.pack('<II',len(binary),0x004E4942)+binary
    return struct.pack('<III',0x46546C67,2,12+len(chunks))+chunks


def fixture(split=False, extra_uv=False, change=None, interleaved=False):
    positions=[(0,0,0),(0,0,1),(1,0,1),(1,0,0)]
    uv=[(0,0),(0,1),(1,1),(1,0)]
    indices=[0,1,2,0,2,3]
    order=[2,3,0,1,2,0] if split else list(range(4))
    attrs={'POSITION':[positions[i] for i in order], 'NORMAL':[(0,1,0)]*len(order),
           'TANGENT':[(1,0,0,1)]*len(order), 'TEXCOORD_0':[uv[i] for i in order],
           'TEXCOORD_1':[(uv[i][0]*.5,uv[i][1]*.5) for i in order]}
    if extra_uv: attrs['TEXCOORD_2']=[uv[i] for i in order]
    if split: indices=list(range(6))
    if change: change(attrs,indices)
    doc={'asset':{'version':'2.0'},'scene':0,'scenes':[{'nodes':[0]}],
         'nodes':[{'name':'receiver','mesh':0,'extras':{'surfaceIds':['wall-a'],'layoutRevision':'layout-1'}}],
         'meshes':[{'name':'receiverMesh','primitives':[{'attributes':{},'material':0}]}],
         'materials':[{'name':'plaster','pbrMetallicRoughness':{'roughnessFactor':.8}}],
         'accessors':[],'bufferViews':[],'buffers':[{'byteLength':0}]}
    binary=bytearray()
    def add(values,kind,component=5126):
        nonlocal binary
        binary+=b'\0'*((-len(binary))%4); start=len(binary)
        code='f' if component==5126 else 'H'; width=len(values[0]); stride=width*struct.calcsize(code)
        padding=b'\0'*4 if interleaved and component==5126 else b''
        for value in values: binary+=struct.pack('<'+code*width,*value)+padding
        view={'buffer':0,'byteOffset':start,'byteLength':len(binary)-start}
        if padding: view['byteStride']=stride+4
        doc['bufferViews'].append(view)
        doc['accessors'].append({'bufferView':len(doc['bufferViews'])-1,'componentType':component,'count':len(values),'type':kind})
        return len(doc['accessors'])-1
    primitive=doc['meshes'][0]['primitives'][0]
    for name,values in attrs.items(): primitive['attributes'][name]=add(values,'VEC'+str(len(values[0])))
    primitive['indices']=add([(i,) for i in indices],'SCALAR',5123)
    doc['buffers'][0]['byteLength']=len(binary)
    return doc,bytes(binary)


def model(**kwargs): return GLB(pack(*fixture(**kwargs)))


class AuditTests(unittest.TestCase):
    def test_vertex_split_reordering_and_interleaved_layout_preserve_corners(self):
        source=model(); target=model(split=True,extra_uv=True,interleaved=True)
        result=compare(source,target,['TEXCOORD_2'])
        self.assertTrue(result['passed'],result)
        self.assertEqual(inspect(target)['triangles'],2)
        self.assertFalse(compare(source,target)['passed'])

    def test_uv_tangent_winding_and_material_changes_fail(self):
        source=model()
        def uv(attrs,indices): attrs['TEXCOORD_0'][0]=(.125,0)
        def tangent(attrs,indices): attrs['TANGENT'][0]=(1,0,0,-1)
        def winding(attrs,indices): indices[0],indices[1]=indices[1],indices[0]
        for mutation in (uv,tangent,winding):
            with self.subTest(mutation=mutation.__name__): self.assertFalse(compare(source,model(change=mutation))['passed'])
        doc,binary=fixture(); doc['materials'][0]['pbrMetallicRoughness']['roughnessFactor']=.3
        self.assertFalse(compare(source,GLB(pack(doc,binary)))['passed'])

    def test_metadata_is_strict_except_named_revision(self):
        source=model(); doc,binary=fixture()
        doc['nodes'][0]['extras']['lightingRevision']='light-2'
        target=GLB(pack(doc,binary))
        self.assertFalse(compare(source,target)['passed'])
        self.assertTrue(compare(source,target,allow_extra_keys=['lightingRevision'])['passed'])
        doc['nodes'][0]['translation']=[0,.1,0]
        self.assertFalse(compare(source,GLB(pack(doc,binary)),allow_extra_keys=['lightingRevision'])['passed'])

    def test_embedded_image_bytes_and_document_extras_survive(self):
        doc,binary=fixture(); offset=len(binary); payload=b'example-image'
        doc['bufferViews'].append({'buffer':0,'byteOffset':offset,'byteLength':len(payload)})
        doc['images']=[{'bufferView':len(doc['bufferViews'])-1,'mimeType':'image/png'}]
        doc['buffers'][0]['byteLength']=offset+len(payload)
        source=GLB(pack(doc,binary+payload))
        changed=GLB(pack(doc,binary+b'changed-image'))
        self.assertFalse(compare(source,changed)['passed'])
        doc['extras']={'revision':'new'}
        self.assertFalse(compare(source,GLB(pack(doc,binary+payload)))['passed'])

    def test_unique_uv_shared_edge_passes_and_overlap_is_exact(self):
        result=uv_audit(model(extra_uv=True),'TEXCOORD_2')
        self.assertTrue(result['passed'],result); self.assertEqual(result['overlapCount'],0)
        self.assertAlmostEqual(result['areaSum'],1)
        def overlap(attrs,indices): attrs['TEXCOORD_2'][3:]=attrs['TEXCOORD_2'][:3]
        result=uv_audit(model(split=True,extra_uv=True,change=overlap),'TEXCOORD_2')
        self.assertFalse(result['passed']); self.assertEqual(result['overlapCount'],1)
        self.assertAlmostEqual(result['overlapExamples'][0]['area'],.5)

    def test_collapsed_outside_and_missing_uv_fail(self):
        def collapsed(attrs,indices): attrs['TEXCOORD_2']=[(0,0)]*len(attrs['POSITION'])
        def outside(attrs,indices): attrs['TEXCOORD_2'][0]=(-.1,0)
        for change in (collapsed,outside):
            self.assertFalse(uv_audit(model(extra_uv=True,change=change),'TEXCOORD_2')['passed'])
        with self.assertRaisesRegex(ValueError,'missing'): uv_audit(model(),'TEXCOORD_2')

    def test_unsupported_inputs_fail_closed(self):
        def animation(d): d['animations']=[{}]
        def skin(d): d['nodes'][0]['skin']=0
        def sparse(d): d['accessors'][0]['sparse']={}
        def compression(d): d['extensionsUsed']=['EXT_meshopt_compression']
        def external(d): d['buffers'][0]['uri']='data.bin'
        def morph(d): d['meshes'][0]['primitives'][0]['targets']=[{}]
        def instance(d): d['nodes'].append({'name':'duplicate','mesh':0})
        for mutation in (animation,skin,sparse,compression,external,morph,instance):
            doc,binary=fixture(); mutation(doc)
            with self.subTest(mutation=mutation.__name__), self.assertRaises(ValueError): GLB(pack(doc,binary))

    def test_malformed_ranges_hierarchy_and_transforms_fail(self):
        def accessor(d): d['accessors'][0]['byteOffset']=99999
        def alignment(d): d['accessors'][0]['byteOffset']=1
        def cycle(d): d['nodes'][0]['children']=[0]
        def bad_scene(d): d['scenes'][0]['nodes']=[2]
        def nan(d): d['nodes'][0]['translation']=[0,float('nan'),0]
        def mixed(d): d['nodes'][0].update(matrix=[1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1],translation=[0,0,0])
        for mutation in (accessor,alignment,cycle,bad_scene,nan,mixed):
            doc,binary=fixture(); mutation(doc)
            with self.subTest(mutation=mutation.__name__), self.assertRaises(ValueError): GLB(pack(doc,binary))

    def test_cli_exit_codes_and_json(self):
        here=Path(__file__).parent
        with tempfile.TemporaryDirectory(dir=here) as directory:
            source=Path(directory)/'source.glb'; target=Path(directory)/'target.glb'
            source.write_bytes(pack(*fixture())); target.write_bytes(pack(*fixture(split=True,extra_uv=True)))
            base=[sys.executable,str(here/'glb_audit.py')]
            result=subprocess.run(base+['compare',str(source),str(target),'--allow-added','TEXCOORD_2','--uv','TEXCOORD_2'],capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stderr); self.assertEqual(json.loads(result.stdout)['uvAudit']['overlapCount'],0)
            result=subprocess.run(base+['compare',str(source),str(target)],capture_output=True,text=True)
            self.assertEqual(result.returncode,1); self.assertFalse(json.loads(result.stdout)['passed'])
            target.write_bytes(b'broken')
            result=subprocess.run(base+['inspect',str(target)],capture_output=True,text=True)
            self.assertEqual(result.returncode,2); self.assertIn('error',json.loads(result.stderr))


if __name__=='__main__': unittest.main()
