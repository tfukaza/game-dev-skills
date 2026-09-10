import test from 'node:test';
import assert from 'node:assert/strict';
import {landmarkErrors,captureViews,lifecycleProbe} from './scene-probes.mjs';
test('landmarks use normalized axes and reject missing evidence',()=>{
 const r=landmarkErrors({gate:[100,200],bridge:[0,0]},{gate:[110,205]},{width:1000,height:500,tolerance:.02});
 assert.equal(r[0].pass,true);assert.equal(r[1].pass,false);
 assert.throws(()=>landmarkErrors({}, {},{width:1,height:1}));
});
test('capture restores state between diagnostics and on failure',async()=>{
 let mode='original',view='start',capture=0;
 const adapter={saveState:()=>({mode,view}),restoreState:s=>{mode=s.mode;view=s.view;},setView:v=>{view=v.id;},
 setMode:m=>{assert.equal(mode,'original');mode=m;},ready:async()=>{},render:()=>{},
 capture:()=>{capture++;if(capture===3)throw Error('capture failed');return mode+':'+view;}};
 await assert.rejects(captureViews(adapter,{views:[{id:'front'},{id:'side'}],modes:['production','neutral']}),/capture failed/);
 assert.equal(mode,'original');assert.equal(view,'start');assert.equal(capture,3);
});
function resourceAdapter(leak=false) {
 const live=new Set(),bindings=new Set();let next=0;
 return {snapshot:()=>({resources:live.size,bindings:bindings.size}),
 begin:({signal})=>({id:++next,signal,disposed:false,pending:Promise.resolve()}),
 waitForPhase:async(h,p)=>{
   if(p==='ready'){live.add(h.id);bindings.add(h.id);}
   else if(p==='decode')h.pending=new Promise(resolve=>setTimeout(()=>{
     live.add(h.id);
     if(!h.disposed)bindings.add(h.id);else if(!leak)live.delete(h.id);
     resolve();
   },2));
 },
 dispose:async h=>{if(h.disposed)return;h.disposed=true;bindings.delete(h.id);live.delete(h.id);},
 settle:async h=>{await h.pending;}
 };
}
test('lifecycle probe waits for late decoder results after disposal',async()=>{
 const ok=await lifecycleProbe(resourceAdapter(),{cycles:2});assert.equal(ok.pass,true);assert.equal(ok.rows.length,6);
 const bad=await lifecycleProbe(resourceAdapter(true),{cycles:1});assert.equal(bad.pass,false);assert.deepEqual(bad.rows.at(-1).leaks,['resources']);
});
test('capture refuses aborted work and restores state',async()=>{
 let restored=0;const ac=new AbortController();ac.abort();
 const adapter={saveState:()=>0,restoreState:()=>{restored++;},setView:()=>{},setMode:()=>{},ready:()=>{},render:()=>{},capture:()=>{throw Error('should not run');}};
 await assert.rejects(captureViews(adapter,{views:[{id:'x'}],signal:ac.signal}),{name:'AbortError'});assert.equal(restored,1);
});
test('settlement still drains late work when disposal throws',async()=>{
 const steps=[];
 const adapter={snapshot:()=>({live:0}),begin:()=>({}),waitForPhase:()=>{},
 dispose:()=>{steps.push('dispose');throw Error('disposal failure');},settle:()=>{steps.push('settle');}};
 await assert.rejects(lifecycleProbe(adapter,{cycles:1,phases:['decode']}),error=>error instanceof AggregateError&&error.errors.length===2);
 assert.deepEqual(steps,['dispose','settle','dispose']);
});
test('historical lifecycle snapshots remain immutable',async()=>{
 const current={live:0};const adapter={snapshot:()=>current,begin:()=>({}),waitForPhase:()=>{current.live++;},dispose:()=>{},settle:()=>{}};
 const result=await lifecycleProbe(adapter,{cycles:2,phases:['ready']});assert.deepEqual(result.rows.map(r=>r.after.live),[1,2]);
});
test('abort during final capture rejects and restores',async()=>{
 const ac=new AbortController();let restored=0;
 const adapter={saveState:()=>0,restoreState:()=>{restored++;},setView:()=>{},setMode:()=>{},ready:()=>{},render:()=>{},capture:async()=>{ac.abort();return 'image';}};
 await assert.rejects(captureViews(adapter,{views:[{id:'front'}],signal:ac.signal}),{name:'AbortError'});assert.equal(restored,2);
});
test('phase and all cleanup errors remain visible after every attempted cleanup',async()=>{
 const errors=['phase','first dispose','settle','second dispose'].map(s=>Error(s));let dispose=0;
 const adapter={snapshot:()=>({live:0}),begin:()=>({}),waitForPhase:()=>{throw errors[0];},dispose:()=>{throw errors[++dispose===1?1:3];},settle:()=>{throw errors[2];}};
 await assert.rejects(lifecycleProbe(adapter,{cycles:1,phases:['decode']}),error=>{assert.ok(error instanceof AggregateError);assert.deepEqual(error.errors,errors);return true;});
});
