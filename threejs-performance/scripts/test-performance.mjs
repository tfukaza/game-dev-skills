import test from 'node:test';
import assert from 'node:assert/strict';
import {summarizeFrames,compareABBA,recordFrames,runABBA} from './benchmark.mjs';
import {textureBytes,inventory} from './inventory.mjs';
const conditions={viewport:[800,600],drawingBuffer:[1600,1200],camera:'fixed',preset:'day',device:'test',sceneRevision:'fixture'};
const makeRuns=(ms=[20,16,16,20])=>ms.map((v,i)=>({variant:['A','B','B','A'][i],conditions:structuredClone(conditions),stats:{medianMs:v},visualPassed:true}));
test('per-frame tails preserve stalls and total duration',()=>{
 const s=summarizeFrames([0,10,20,80,90]);assert.equal(s.frames,4);assert.equal(s.durationMs,90);assert.equal(s.stallsOver50Ms,1);assert.equal(s.maximumMs,60);
 assert.throws(()=>summarizeFrames([0,0,1]));assert.throws(()=>summarizeFrames([0,NaN,2]));
});
test('ABBA gain, mixed result, regression, quality and conditions',()=>{
 assert.equal(compareABBA(makeRuns()).verdict,'consistent-gain');
 assert.equal(compareABBA(makeRuns([20,16,24,20])).verdict,'inconclusive');
 assert.equal(compareABBA(makeRuns([20,24,24,20])).verdict,'consistent-regression');
 const bad=makeRuns();bad[2].visualPassed=false;assert.equal(compareABBA(bad).verdict,'rejected-quality');
 const changed=makeRuns();changed[1].conditions.drawingBuffer=[800,600];assert.equal(compareABBA(changed).verdict,'incomparable');
 assert.throws(()=>compareABBA(makeRuns().slice(1)));
});
test('ABBA restores prior variant after failure and records actual order',async()=>{
 let variant='original',calls=[],restore=0;
 const adapter={saveState:()=>variant,restoreState:s=>{variant=s;restore++;},setVariant:s=>{variant=s;calls.push(s);},ready:async()=>{},warmup:async()=>{},conditions:()=>conditions,
 measure:async()=>[0,variant==='A'?20:16,variant==='A'?40:32],checkQuality:async()=>true};
 const result=await runABBA(adapter);assert.deepEqual(calls,['A','B','B','A']);assert.equal(variant,'original');assert.equal(result.comparison.verdict,'consistent-gain');
 adapter.measure=async()=>{throw Error('decode failed');};await assert.rejects(runABBA(adapter),/decode failed/);assert.equal(variant,'original');assert.equal(restore,2);
});
test('RAF sampling abort releases pending callback',async()=>{
 let callback,cancelled=0;const ac=new AbortController();
 const p=recordFrames({signal:ac.signal,raf:fn=>{callback=fn;return 7;},cancel:id=>{assert.equal(id,7);cancelled++;}});
 callback(0);ac.abort();await assert.rejects(p,{name:'AbortError'});assert.equal(cancelled,1);
});
test('texture payload accounts for mips faces blocks and multisample',()=>{
 assert.equal(textureBytes({width:16,height:16,levels:5,format:'rgba8'}),1364);
 assert.equal(textureBytes({width:16,height:16,levels:5,faces:6,format:'rgba8'}),8184);
 assert.equal(textureBytes({width:2,height:2,format:'bc1'}),8);
 assert.equal(textureBytes({width:4,height:4,samples:4,format:'rgba16f'}),512);
 assert.throws(()=>textureBytes({width:16,height:16,levels:6,format:'rgba8'}));
 assert.throws(()=>textureBytes({width:2,height:2,format:'uastc'}),/actual GPU format/);
});
test('inventory deduplicates shared objects without inventing unknown memory',()=>{
 const file={url:'https://example.test/a.ktx2',bytes:100};const tex={id:'shared',kind:'texture',width:16,height:16,format:'rgba8',levels:5};
 const r=inventory({files:[file,{...file}],resources:[tex,{...tex},{id:'pending',kind:'texture',format:'unknown'}]});
 assert.equal(r.transferBytes,100);assert.equal(r.estimatedGpuPayloadBytes,1364);assert.equal(r.estimateComplete,false);
 assert.throws(()=>inventory({files:[file,{...file,bytes:99}]}),/Conflicting/);
});
test('abort in final quality callback is propagated and restores state',async()=>{
 const ac=new AbortController();let checked=0,restored=false;
 const adapter={saveState:()=>0,restoreState:()=>{restored=true;},setVariant:()=>{},ready:()=>{},warmup:()=>{},conditions:()=>conditions,
 measure:()=>[0,16,32],checkQuality:async()=>{if(++checked===4)ac.abort();return true;}};
 await assert.rejects(runABBA(adapter,{signal:ac.signal}),{name:'AbortError'});assert.equal(restored,true);
});
