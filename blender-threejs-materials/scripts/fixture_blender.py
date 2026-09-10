"""CPU-only graph execution against fixture_expected.mjs output; no user scene.
Blender -b --factory-startup --python-exit-code 1 --python fixture_blender.py -- --expected FILE --report FILE
"""
import argparse,json,sys,subprocess,shutil
from pathlib import Path
import bpy,numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parent))
from stochastic_blender import stochastic_material
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--expected',type=Path,required=True);parser.add_argument('--report',type=Path,required=True)
args=parser.parse_args(sys.argv[sys.argv.index('--')+1:])
expected=json.loads(args.expected.read_text());size=expected['size']
bpy.ops.wm.read_factory_settings(use_empty=True)
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=1
scene.render.threads_mode='FIXED';scene.render.threads=2
scene.render.bake.margin=0;scene.render.bake.use_clear=True
bpy.ops.mesh.primitive_plane_add(size=2);obj=bpy.context.object
base=obj.data.uv_layers[0];base.name='SourceUV';atlas=obj.data.uv_layers.new(name='BakeUV')
for source,target in zip(base.data,atlas.data):
 u,v=source.uv[:];target.uv=(u,v)
 source.uv=(expected['uvMin']+expected['uvSpan']*u,1-(expected['uvMin']+expected['uvSpan']*v))
base.active_render=True
images={}
for role,rgb in {'color':(.2,.35,.5),'normal':(.65,.45,.965),'orm':(.85,.72,.1)}.items():
 im=bpy.data.images.new(role,4,4,float_buffer=True);im.colorspace_settings.name='Non-Color'
 if hasattr(im,'use_half_precision'):im.use_half_precision=False
 im.pixels.foreach_set(np.tile([*rgb,1],16).astype(np.float32));images[role]=im
report={'size':size,'device':'CPU','input':'constant linear image values; transforms still vary over positive/negative cells','presets':{}}
for preset in expected['presets']:
 mat=bpy.data.materials.new(preset);mat.use_nodes=True;obj.data.materials.clear();obj.data.materials.append(mat)
 tree=mat.node_tree;tree.nodes.clear();uv=tree.nodes.new('ShaderNodeUVMap');uv.uv_map='SourceUV'
 outputs=stochastic_material(tree,uv.outputs['UV'],images,preset)
 groups=[n.node_tree for n in tree.nodes if n.type=='GROUP'];assert len(groups)==1
 assert sum(n.type=='TEX_IMAGE' for n in groups[0].nodes)==9
 again=stochastic_material(tree,uv.outputs['UV'],images,preset)
 assert len({n.node_tree for n in tree.nodes if n.type=='GROUP'})==1
 emission=tree.nodes.new('ShaderNodeEmission');out=tree.nodes.new('ShaderNodeOutputMaterial');tree.links.new(emission.outputs[0],out.inputs['Surface'])
 target=bpy.data.images.new('target-'+preset,size,size,float_buffer=True);target.colorspace_settings.name='Non-Color'
 texture=tree.nodes.new('ShaderNodeTexImage');texture.image=target;tree.nodes.active=texture
 if 'sampledCoordinates' not in report:
  # Cycles' bake rasterizer perturbs triangle barycentrics slightly. Measure its
  # actual sample coordinates before comparing shader math; do not loosen the
  # numerical tolerance to hide a pixel-center assumption.
  scale=tree.nodes.new('ShaderNodeVectorMath');scale.operation='MULTIPLY';scale.inputs[1].default_value=(.25,-.25,0)
  offset=tree.nodes.new('ShaderNodeVectorMath');offset.operation='ADD';offset.inputs[1].default_value=(.5,.75,0)
  tree.links.new(uv.outputs['UV'],scale.inputs[0]);tree.links.new(scale.outputs[0],offset.inputs[0]);tree.links.new(offset.outputs[0],emission.inputs['Color'])
  bpy.ops.object.bake(type='EMIT',uv_layer='BakeUV',margin=0)
  coordinates=np.empty(size*size*4,np.float32);target.pixels.foreach_get(coordinates)
  coordinates=coordinates.reshape(-1,4)[:,:2]*4-2
  ideal=np.array([[-1.2+(x+.5)/size*2.4,-1.2+(y+.5)/size*2.4] for y in range(size) for x in range(size)])
  report['sampledCoordinates']={'maxDeviationFromPixelCenter':float(np.max(np.abs(coordinates-ideal)))}
  coord_path=args.expected.with_suffix('.coordinates.json');coord_path.write_text(json.dumps({'size':size,'uvs':coordinates.tolist()}))
  sampled=args.expected.with_suffix('.sampled.json')
  subprocess.run([shutil.which('node') or 'node',str(Path(__file__).with_name('fixture_expected.mjs')),str(sampled),str(coord_path)],check=True)
  expected=json.loads(sampled.read_text());coord_path.unlink();sampled.unlink()
 points=expected['presets'][preset]
 errors={}
 for role in ('color','normal','orm'):
  tree.links.new(outputs[role],emission.inputs['Color'])
  bpy.ops.object.bake(type='EMIT',uv_layer='BakeUV',margin=0)
  pixels=np.empty(size*size*4,np.float32);target.pixels.foreach_get(pixels)
  actual=pixels.reshape(-1,4)[:,:3];reference=np.array([p[role] for p in points])
  error=float(np.max(np.abs(actual-reference)));errors[role]=error
  print('PARITY_ROLE',preset,role,error,flush=True)
  assert np.isfinite(actual).all() and error<.0002,(preset,role,error)
 report['presets'][preset]={'maxError':errors,'sharedImageNodes':9,'groupReuse':True}
assert [u.name for u in obj.data.uv_layers]==['SourceUV','BakeUV'] and base.active_render
report['passed']=True;args.report.write_text(json.dumps(report,indent=2)+'\n')
print('STOCHASTIC_GRAPH_PARITY',json.dumps(report),flush=True)
