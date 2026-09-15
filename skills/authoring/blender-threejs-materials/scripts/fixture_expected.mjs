import fs from 'node:fs';
import {PRESETS,sample} from './stochastic.mjs';
const measured=process.argv[3]?JSON.parse(fs.readFileSync(process.argv[3],'utf8')):null;
const size=measured?.size??32, output={size,uvMin:-1.2,uvSpan:2.4,presets:{}};
const textures={color:()=>[.2,.35,.5],normal:()=>[.65,.45,.965],orm:()=>[.85,.72,.1]};
for(const [name,preset] of Object.entries(PRESETS)) {
 output.presets[name]=[];
 for(let y=0;y<size;y++)for(let x=0;x<size;x++)output.presets[name].push(sample(measured?.uvs[y*size+x]??[-1.2+(x+.5)/size*2.4,-1.2+(y+.5)/size*2.4],textures,preset));
}
if(!process.argv[2])throw new Error('Usage: node fixture_expected.mjs output.json');
fs.writeFileSync(process.argv[2],JSON.stringify(output));
