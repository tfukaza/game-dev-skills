"""Create a small, inspectable context-refresh example in a NEW output directory."""
import argparse,copy,json
from pathlib import Path
from PIL import Image,ImageDraw
from context_masks import write,preview_mask

def fixture(folder):
 folder=Path(folder)
 if folder.exists():raise ValueError('Choose a new output directory; fixture will not replace existing paint')
 folder.mkdir(parents=True)
 original=json.loads((Path(__file__).resolve().parents[1]/'fixtures/wall.json').read_text())
 updated=copy.deepcopy(original);updated['baseProfile']=[[x,y+.28] for x,y in original['baseProfile']]
 updated['drains'][0]['anchor']=[3.7,2.4]
 before=folder/'initial.json';after=folder/'updated.json'
 before.write_text(json.dumps(original,indent=2)+'\n');after.write_text(json.dumps(updated,indent=2)+'\n')
 output=folder/'wall.png';write(before,output,128)
 manual=Image.open(output).copy();selected={(x,y) for x in range(30,44) for y in range(25,36)}
 for xy in selected:manual.putpixel(xy,(0,0,224,0))
 manual.save(output);before_preview=preview_mask(original,manual)
 result=write(after,output,128,refresh_context=True);active=Image.open(output).copy()
 preserved=sum(active.getpixel(xy)==manual.getpixel(xy) for xy in selected)
 assert preserved==154 and result['manualPixels']==154
 sheet=Image.new('RGB',(776,438),(32,34,37));draw=ImageDraw.Draw(sheet)
 for i,(label,im) in enumerate((('Initial context + manual repair',before_preview),('Moved slope / drain; repair retained',preview_mask(updated,active)),('Initial grime channel',manual.getchannel('A').convert('RGB')),('Refreshed grime channel',active.getchannel('A').convert('RGB')))):
  x=4+(i%2)*388;y=4+(i//2)*217;draw.text((x,y),label,fill=(232,232,232))
  sheet.paste(im.resize((384,192),Image.Resampling.NEAREST),(x,y+20))
 sheet.save(folder/'comparison.png')
 result.update({'retainedEditedPixels':preserved,'profileRaisedMeters':.28,'drainBefore':original['drains'][0]['anchor'],'drainAfter':updated['drains'][0]['anchor']})
 (folder/'result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))

if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('output_directory',type=Path);fixture(p.parse_args().output_directory)
