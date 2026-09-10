import copy,hashlib,json,math,tempfile,unittest
from pathlib import Path
from PIL import Image
from context_masks import mask_at,generate,write,blend_properties,layer_paths,preview_mask
ROOT=Path(__file__).resolve().parents[1]
class Masks(unittest.TestCase):
 def test_profile_moves_wear_and_leaves_quiet_upper_wall(self):
  spec=json.loads((ROOT/'fixtures/wall.json').read_text());moved=copy.deepcopy(spec)
  moved['baseProfile']=[[x,y+.6] for x,y in spec['baseProfile']]
  original=sum(mask_at(spec,x/10,2.0)[1] for x in range(1,79));changed=sum(mask_at(moved,x/10,2.0)[1] for x in range(1,79))
  self.assertGreater(changed,original*2)
  self.assertLess(sum(mask_at(spec,x/10,3.6)[1] for x in range(1,79)),.01)
 def test_ground_has_internal_variation_and_clearer_lane(self):
  spec=json.loads((ROOT/'fixtures/ground.json').read_text())
  protected=[mask_at(spec,.2,y/20)[0] for y in range(2,118)]
  lane=[mask_at(spec,4,y/20)[0] for y in range(2,118)]
  self.assertGreater(sum(protected),sum(lane)*2)
  self.assertGreater(max(protected)-min(protected),.2)
  self.assertGreater(sum(.1<v<.8 for v in protected),len(protected)*.4)
 def test_prepare_preserves_manual_pixels_and_regenerate_backs_up(self):
  with tempfile.TemporaryDirectory(dir=ROOT/'fixtures') as folder:
   out=Path(folder)/'mask.png';spec=ROOT/'fixtures/wall.json'
   write(spec,out,32);im=Image.open(out);im.putpixel((12,12),(1,234,56,78));im.save(out)
   manual=out.read_bytes();self.assertEqual(write(spec,out,32)['status'],'preserved');self.assertEqual(out.read_bytes(),manual)
   write(spec,out,32,True);self.assertNotEqual(out.read_bytes(),manual)
   self.assertEqual(next(out.parent.glob('*.before-regenerate.png')).read_bytes(),manual)
 def test_seeded_output_and_coherent_layer_endpoints(self):
  spec=json.loads((ROOT/'fixtures/wall.json').read_text());a,_=generate(spec,32);b,_=generate(spec,32)
  self.assertEqual(a.tobytes(),b.tobytes())
  base={'color':[.2,.3,.4],'roughness':.5,'normal':[0,0,1]};layer={'color':[.4,.5,.6],'roughness':.9,'normal':[.6,0,.8]}
  self.assertEqual(blend_properties(base,layer,0),base);self.assertEqual(blend_properties(base,layer,1),layer)
  mid=blend_properties(base,layer,.5);self.assertAlmostEqual(mid['roughness'],.7)
  self.assertAlmostEqual(sum(v*v for v in mid['normal']),1)
 def test_refresh_moves_profile_and_drain_but_keeps_154_manual_pixels(self):
  spec={'kind':'wall','seed':291,'worldMeters':[7.6,4.2],
        'baseProfile':[[0,.12],[2.1,.39],[5.3,.84],[7.6,1.14]],'repairs':[],
        'drains':[{'anchor':[6.2,2.9],'radiusMeters':.09,'lengthMeters':1.4}]}
  moved=copy.deepcopy(spec);moved['baseProfile']=[[x,y+.31] for x,y in spec['baseProfile']]
  moved['drains'][0]['anchor']=[4.8,2.5]
  # Drain must affect its own anchor and stop at the actual contact profile.
  self.assertGreater(mask_at(spec,6.2,2.6)[3],.2)
  self.assertLess(mask_at(moved,6.2,2.6)[3],.01)
  self.assertGreater(mask_at(moved,4.8,2.2)[3],.2)
  self.assertEqual(mask_at(moved,4.8,.01),(0,0,0,0))
  with tempfile.TemporaryDirectory() as folder:
   out=Path(folder)/'mask.png';source=Path(folder)/'wall.json';source.write_text(json.dumps(spec))
   write(source,out,96);old=Image.open(out).copy();manual=old.copy()
   selected={(x,y) for x in range(25,39) for y in range(20,31)}
   for xy in selected:manual.putpixel(xy,(0,0,224,0))
   manual.save(out);manual_bytes=out.read_bytes();source.write_text(json.dumps(moved))
   self.assertEqual(write(source,out,96)['status'],'preserved');self.assertEqual(out.read_bytes(),manual_bytes)
   result=write(source,out,96,refresh_context=True);active=Image.open(out).copy();generated,_=generate(moved,96)
   self.assertEqual(result['newManualPixels'],154);self.assertEqual(result['manualPixels'],154)
   changed=0
   for y in range(96):
    for x in range(96):
     xy=(x,y)
     if xy in selected:self.assertEqual(active.getpixel(xy),manual.getpixel(xy))
     else:
      self.assertEqual(active.getpixel(xy),generated.getpixel(xy))
      changed+=active.getpixel(xy)!=old.getpixel(xy)
   self.assertGreater(changed,400)
   self.assertEqual(Image.open(out.with_name('mask-preview.png')).tobytes(),preview_mask(moved,active).tobytes())
   # A second refresh retains accumulated overrides and captures an added edit.
   active.putpixel((71,14),(9,8,7,6));active.save(out);moved['seed']+=1;source.write_text(json.dumps(moved))
   result=write(source,out,96,refresh_context=True);active=Image.open(out)
   self.assertEqual(result['manualPixels'],155);self.assertEqual(result['newManualPixels'],1)
   self.assertTrue(all(active.getpixel(xy)==manual.getpixel(xy) for xy in selected))
   self.assertEqual(active.getpixel((71,14)),(9,8,7,6))
 def test_refresh_refuses_missing_baseline_registration_change_and_unknown_context(self):
  spec=json.loads((ROOT/'fixtures/wall.json').read_text())
  with tempfile.TemporaryDirectory() as folder:
   out=Path(folder)/'mask.png';source=Path(folder)/'wall.json';source.write_text(json.dumps(spec))
   write(source,out,32);original=out.read_bytes()
   changed=copy.deepcopy(spec);changed['worldMeters'][0]+=1;source.write_text(json.dumps(changed))
   with self.assertRaisesRegex(ValueError,'registration'):write(source,out,32,refresh_context=True)
   self.assertEqual(out.read_bytes(),original);source.write_text(json.dumps(spec))
   paths=layer_paths(out);baseline=Image.open(paths['generated']).copy();baseline.putpixel((1,1),(1,2,3,4));baseline.save(paths['generated'])
   with self.assertRaisesRegex(ValueError,'baseline was modified'):write(source,out,32,refresh_context=True)
   self.assertEqual(out.read_bytes(),original);paths['state'].unlink()
   with self.assertRaisesRegex(ValueError,'original generated baseline'):write(source,out,32,refresh_context=True)
   self.assertEqual(out.read_bytes(),original)
  spec['unsupportedFixture']=[]
  with self.assertRaisesRegex(ValueError,'Unsupported context'):generate(spec,32)
if __name__=='__main__':unittest.main()
