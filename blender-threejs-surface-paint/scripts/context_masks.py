"""Seeded wall-wear / ground-deposit example; Python3 + Pillow, no NumPy.
Default preserves an existing output byte-for-byte. --refresh-context rebuilds
generated paint beneath retained manual pixel overrides. --reset-manual (legacy
alias --regenerate) backs up the active mask, then discards its overrides.
Mask RGBA = deposit/exposure/repair/grime;
alpha is DATA, never the wall's opacity. Coordinates and noise scales are metres.
"""
import argparse,hashlib,json,math
from pathlib import Path
from PIL import Image

def clamp(v):return max(0.,min(1.,v))
def smooth(v):
 v=clamp(v);return v*v*(3-2*v)
def noise(x,y,seed):
 i,j=math.floor(x),math.floor(y);u,v=smooth(x-i),smooth(y-j)
 def h(a,b):
  n=((a*374761393+b*668265263+seed*69069)&0xffffffff)
  n=((n^(n>>13))*1274126177)&0xffffffff
  return ((n^(n>>16))&0xffffffff)/4294967295
 return (h(i,j)*(1-u)+h(i+1,j)*u)*(1-v)+(h(i,j+1)*(1-u)+h(i+1,j+1)*u)*v
def field(x,y,seed):
 return sum(noise(x/s,y/s,seed+k*17)*w for k,(s,w) in enumerate(((1.7,.5),(.51,.3),(.12,.2))))
def profile_height(profile,x):
 for (a,ya),(b,yb) in zip(profile,profile[1:]):
  if x<=b:return ya+(yb-ya)*clamp((x-a)/(b-a))
 return profile[-1][1]
def segment_distance(x,y,segment):
 (a,b),(c,d)=segment;dx,dy=c-a,d-b;t=clamp(((x-a)*dx+(y-b)*dy)/max(dx*dx+dy*dy,1e-12))
 return math.hypot(x-a-t*dx,y-b-t*dy)
def mask_at(spec,x,y):
 seed=spec['seed'];n=field(x,y,seed);fine=noise(x/.027,y/.027,seed+97)
 if spec['kind']=='wall':
  distance=y-profile_height(spec['baseProfile'],x)
  if distance<0:return (0,0,0,0)
  envelope=smooth((.8+.38*field(x*.65,y*.65,seed+2)-distance)/.58)
  fragments=smooth((field(x*2.1,y*2.1,seed+13)-.27)/.42)
  exposure=envelope*fragments*(.65+.35*fine)
  chip=smooth((n-.68)/.17)*smooth((1.6-distance)/.7)*.45
  exposure=max(exposure,chip)
  repairs=[]
  for r in spec.get('repairs',[]):
   dx=(x-r['center'][0])/r['radius'][0];dy=(y-r['center'][1])/r['radius'][1]
   repairs.append(smooth((1+.17*(n-.5)-math.hypot(dx,dy))/.14)*r.get('strength',.7))
  repair=max(repairs,default=0);exposure*=1-repair
  grime=smooth((.16-distance)/.16)*(.2+.35*n)
  for drain in spec.get('drains',[]):
   ax,ay=drain['anchor'];down=ay-y
   if down<0:continue
   width=drain.get('radiusMeters',.06)+.018*min(down,2)
   bend=(noise(down/.22,ax,seed+89)-.5)*width*.6
   streak=math.exp(-((x-ax-bend)/width)**2)*math.exp(-down/drain.get('lengthMeters',1.2))
   grime=max(grime,drain.get('strength',.65)*streak*(.6+.4*fine))
  return (.07*envelope,clamp(exposure),repair,grime)
 # The domain warp and density both vary in2D, not just the edge of a strip.
 wx=x+(field(x,y,seed+101)-.5)*1.25;wy=y+(field(x,y,seed+211)-.5)*1.25
 distance=min(segment_distance(x,y,s) for s in spec['walls'])
 edge=math.exp(-distance/spec.get('spreadMeters',1.2))
 density=smooth((edge*.82+field(wx,wy,seed+37)*.75-.57)/.42)
 lane=spec.get('clearLane')
 if lane:
  d=segment_distance(x,y,lane['segment'])
  density*=1-lane.get('strength',.6)*math.exp(-(d/lane['radiusMeters'])**2)
 density*=.62+.38*fine
 return(clamp(density),0,0,0)

def blend_properties(base,layer,coverage):
 t=clamp(coverage)
 normal=[(1-t)*a+t*b for a,b in zip(base['normal'],layer['normal'])];length=math.sqrt(sum(v*v for v in normal))
 return {'color':[(1-t)*a+t*b for a,b in zip(base['color'],layer['color'])],
         'roughness':base['roughness']*(1-t)+layer['roughness']*t,
         'normal':[v/max(length,1e-8) for v in normal]}

def generate(spec,size):
 if not 8<=size<=2048:raise ValueError('Example supports8–2048pixels; use a production baker for larger maps')
 width,height=spec['worldMeters']
 if width<=0 or height<=0:raise ValueError('World extents must be positive')
 common={'kind','seed','worldMeters'}
 if spec['kind']=='wall':
  supported=common|{'baseProfile','repairs','drains'}
  p=spec['baseProfile']
  if len(p)<2 or any(b[0]<=a[0] for a,b in zip(p,p[1:])):raise ValueError('Base profile X values must increase')
  for d in spec.get('drains',[]):
   if set(d)-{'anchor','radiusMeters','lengthMeters','strength'}:raise ValueError('Unsupported drain fields')
   if len(d['anchor'])!=2 or not all(math.isfinite(v) for v in d['anchor']):raise ValueError('Drain anchor must be two finite wall coordinates')
   if d.get('radiusMeters',.06)<=0 or d.get('lengthMeters',1.2)<=0:raise ValueError('Drain widths/lengths must be positive')
   if not 0<=d.get('strength',.65)<=1:raise ValueError('Drain strength must be in [0,1]')
 elif spec['kind']!='ground' or not spec.get('walls'):raise ValueError('Ground requires wall segments')
 else:supported=common|{'walls','spreadMeters','clearLane'}
 if set(spec)-supported:raise ValueError('Unsupported context fields: '+', '.join(sorted(set(spec)-supported)))
 image=Image.new('RGBA',(size,size));pixels=[]
 for row in range(size):
  y=(1-(row+.5)/size)*height
  for col in range(size):
   x=(col+.5)/size*width;values=mask_at(spec,x,y);pixels.append(tuple(round(clamp(v)*255) for v in values))
 image.putdata(pixels);return image,preview_mask(spec,image)

def preview_mask(spec,image):
 # Flat diagnostic of the ACTIVE composite, including manual repair/grime.
 width,height=spec['worldMeters'];preview=Image.new('RGB',image.size);rgb=[]
 for row in range(image.height):
  y=(1-(row+.5)/image.height)*height
  for col in range(image.width):
   x=(col+.5)/image.width*width
   n=field(x,y,spec['seed']);grain=(noise(x/.017,y/.017,spec['seed']+7)-.5)*.045
   color=[.67+grain+(n-.5)*.045,.65+grain,.60+grain];deposit,exposure,repair,grime=[v/255 for v in image.getpixel((col,row))]
   for coverage,target in ((exposure,[.56+grain,.52+grain,.44+grain]),(deposit,[.64+grain,.48+grain,.29+grain]),(repair,[.70+grain,.68+grain,.63+grain]),(grime,[.42+grain,.42+grain,.39+grain])):
    color=[a*(1-coverage)+b*coverage for a,b in zip(color,target)]
   rgb.append(tuple(round(clamp(v)*255) for v in color))
 preview.putdata(rgb);return preview

def layer_paths(output):
 output=Path(output)
 return {key:output.with_name(output.stem+suffix) for key,suffix in (
  ('generated','.generated.png'),('manual','.manual.png'),('coverage','.manual-coverage.png'),('state','.layers.json'))}

def load_image(path,mode,size):
 with Image.open(path) as src:
  if src.mode!=mode or src.size!=size:raise ValueError('Layer mode/size changed: '+str(path))
  return src.copy()

def write(spec_path,output,size=256,regenerate=False,refresh_context=False):
 output=Path(output)
 if output.suffix.lower()!='.png':raise ValueError('Mask output must be a PNG to preserve RGBA data')
 if regenerate and refresh_context:raise ValueError('Choose refresh-context or reset-manual, not both')
 if output.exists() and not regenerate and not refresh_context:return {'status':'preserved','sha256':hashlib.sha256(output.read_bytes()).hexdigest(),'preview':'not refreshed; an existing preview may predate manual edits'}
 spec=json.loads(Path(spec_path).read_text());paths=layer_paths(output)
 contract={'version':1,'size':size,'kind':spec['kind'],'worldMeters':spec['worldMeters']}
 manual=Image.new('RGBA',(size,size));coverage=Image.new('L',(size,size));edits=0
 if refresh_context:
  if not output.exists() or not all(p.exists() for p in paths.values()):raise ValueError('Context refresh requires the original generated baseline and manual sidecars; an old flattened mask cannot be inferred safely')
  state=json.loads(paths['state'].read_text())
  if any(state.get(k)!=v for k,v in contract.items()):raise ValueError('Pixel registration changed; reproject manual paint explicitly before refreshing')
  if hashlib.sha256(paths['generated'].read_bytes()).hexdigest()!=state['generatedSha256']:raise ValueError('Generated baseline was modified; refusing to infer manual edits')
  baseline=load_image(paths['generated'],'RGBA',(size,size));manual=load_image(paths['manual'],'RGBA',(size,size))
  coverage=load_image(paths['coverage'],'L',(size,size));current=load_image(output,'RGBA',(size,size))
  if any(v not in (0,255) for v in coverage.getdata()):raise ValueError('Manual coverage is a binary pixel override, not opacity')
  expected=Image.composite(manual,baseline,coverage)
  # Capture new edits to the active image. Existing explicit overrides persist,
  # even if their values happen to equal the next procedural generation.
  for i,(actual,prior) in enumerate(zip(current.getdata(),expected.getdata())):
   if actual!=prior:
    xy=(i%size,i//size);manual.putpixel(xy,actual);coverage.putpixel(xy,255);edits+=1
 image,preview=generate(spec,size)
 if output.exists() and regenerate:
  digest=hashlib.sha256(output.read_bytes()).hexdigest()[:12]
  backup=output.with_name(output.stem+'.'+digest+'.before-regenerate.png')
  if backup.exists() and backup.read_bytes()!=output.read_bytes():raise ValueError('Existing backup differs; refusing to replace the edited mask')
  if not backup.exists():backup.write_bytes(output.read_bytes())
 output.parent.mkdir(parents=True,exist_ok=True)
 image.save(paths['generated']);manual.save(paths['manual']);coverage.save(paths['coverage'])
 contract['generatedSha256']=hashlib.sha256(paths['generated'].read_bytes()).hexdigest()
 paths['state'].write_text(json.dumps(contract,indent=2)+'\n')
 image=Image.composite(manual,image,coverage);image.save(output)
 if refresh_context:preview=preview_mask(spec,image)
 preview.save(output.with_name(output.stem+'-preview.png'))
 return {'status':'refreshed' if refresh_context else 'generated','sha256':hashlib.sha256(output.read_bytes()).hexdigest(),'size':size,'newManualPixels':edits,'manualPixels':sum(v==255 for v in coverage.getdata())}
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('spec',type=Path);p.add_argument('output',type=Path)
 p.add_argument('--size',type=int,default=256);mode=p.add_mutually_exclusive_group()
 mode.add_argument('--refresh-context',action='store_true',help='Rebuild context while retaining manually edited pixels')
 mode.add_argument('--reset-manual','--regenerate',dest='regenerate',action='store_true',help='Back up active mask, discard manual overrides and rebuild all paint')
 a=p.parse_args();print(json.dumps(write(a.spec,a.output,a.size,a.regenerate,a.refresh_context)))
