#!/usr/bin/env node
/** Logical GPU payload estimate; not driver residency. Input manifest is explicit. */
import {readFileSync} from 'node:fs';
import {pathToFileURL} from 'node:url';
const formats = {
  r8:[1,1,1], rg8:[1,1,2], rgb8:[1,1,3], rgba8:[1,1,4],
  r16f:[1,1,2], rg16f:[1,1,4], rgba16f:[1,1,8], rgba32f:[1,1,16],
  depth16:[1,1,2], depth24stencil8:[1,1,4], depth32f:[1,1,4],
  bc1:[4,4,8], bc3:[4,4,16], bc5:[4,4,16], bc7:[4,4,16],
  etc2rgb:[4,4,8], etc2rgba:[4,4,16], astc4x4:[4,4,16], astc6x6:[6,6,16]
};
const positive = (v,k) => {if (!Number.isSafeInteger(v)||v<1) throw new TypeError(k+' must be a positive integer');return v;};
export function textureBytes(r) {
  let width=positive(r.width,'width'),height=positive(r.height,'height');
  const layout=formats[r.format]; if (!layout) throw new TypeError('Unknown actual GPU format: '+r.format);
  const levels=r.levels ?? 1, layers=r.layers ?? 1, faces=r.faces ?? 1, samples=r.samples ?? 1;
  for (const [k,v] of Object.entries({levels,layers,faces,samples})) positive(v,k);
  if (![1,6].includes(faces)) throw new Error('faces must be 1 or 6');
  if (levels > 1+Math.floor(Math.log2(Math.max(width,height)))) throw new Error('Mip count exceeds dimensions');
  if (samples>1 && (levels>1 || layout[0]>1 || layers>1 || faces>1)) throw new Error('Multisample estimate supports only uncompressed single-level 2D renderbuffers');
  let bytes=0;
  for(let i=0;i<levels;i++) {bytes+=Math.ceil(width/layout[0])*Math.ceil(height/layout[1])*layout[2];width=Math.max(1,Math.floor(width/2));height=Math.max(1,Math.floor(height/2));}
  return bytes*layers*faces*samples;
}
function unique(items,key) {
  const map=new Map();
  for (const item of items) {
    if (typeof item[key]!=='string' || !item[key]) throw new Error('Missing '+key);
    const old=map.get(item[key]);
    if (old && JSON.stringify(Object.fromEntries(Object.entries(old).sort()))!==JSON.stringify(Object.fromEntries(Object.entries(item).sort()))) throw new Error('Conflicting duplicate '+item[key]);
    map.set(item[key],item);
  } return [...map.values()];
}
export function inventory({files=[],resources=[]}) {
  const downloads=unique(files,'url'), gpu=unique(resources,'id');
  let transferBytes=0,estimatedGpuPayloadBytes=0; const unknownResources=[];
  for (const file of downloads) {if(!Number.isSafeInteger(file.bytes)||file.bytes<0) throw new Error('Invalid file bytes'); transferBytes+=file.bytes;}
  const items=gpu.map(r=>{
    let bytes;
    if(r.kind==='buffer') {if(!Number.isSafeInteger(r.bytes)||r.bytes<0)throw new Error('Invalid buffer bytes');bytes=r.bytes;}
    else if(r.kind==='texture'||r.kind==='renderbuffer') {if(r.format==='unknown'){unknownResources.push(r.id);bytes=null;}else bytes=textureBytes(r);}
    else throw new Error('Unsupported resource kind '+r.kind);
    if(bytes!==null) estimatedGpuPayloadBytes+=bytes;
    return {id:r.id,bytes};
  });
  return {uniqueDownloads:downloads.length,transferBytes,uniqueResources:gpu.length,
    estimatedGpuPayloadBytes,estimateComplete:unknownResources.length===0,unknownResources,items,
    limitations:'Logical payload only; excludes driver overhead, alignment, program storage and unenumerated attachments/temporary decode buffers. Supply actual transcoded formats.'};
}
if(process.argv[1] && import.meta.url===pathToFileURL(process.argv[1]).href) {
  try {if(process.argv.length!==3)throw new Error('Usage: node inventory.mjs inventory.json');console.log(JSON.stringify(inventory(JSON.parse(readFileSync(process.argv[2],'utf8'))),null,2));}
  catch(e){console.error(e.message);process.exitCode=1;}
}
