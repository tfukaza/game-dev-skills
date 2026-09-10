/** Application-adapter QA helpers; no assumptions about UI, Three internals or URLs. */
export function landmarkErrors(expected, observed, {width,height,tolerance=.02}) {
  if(!Number.isFinite(width)||width<=0||!Number.isFinite(height)||height<=0||!Number.isFinite(tolerance)||tolerance<0)throw new TypeError('Invalid frame/tolerance');
  const entries=Object.entries(expected);
  if(!entries.length)throw new Error('At least one named reference landmark required');
  const point=p=>Array.isArray(p)&&p.length===2&&p.every(Number.isFinite);
  return entries.map(([id,p])=>{
    if(!point(p))throw new Error('Invalid reference point '+id);
    const actual=observed[id];
    if(!point(actual))return {id,pass:false,reason:'missing or invalid observed landmark'};
    const dx=(actual[0]-p[0])/width,dy=(actual[1]-p[1])/height;
    return {id,dx,dy,pass:Math.abs(dx)<=tolerance&&Math.abs(dy)<=tolerance};
  });
}
export async function captureViews(adapter,{views,modes=['production'],signal}={}) {
  for(const method of ['saveState','restoreState','setView','setMode','ready','render','capture'])
    if(typeof adapter[method]!=='function')throw new TypeError('Missing '+method);
  if(!views?.length||!modes.length)throw new TypeError('Nonempty views/modes required');
  const initial=await adapter.saveState(),captures=[];
  try {
    for(const view of views)for(const mode of modes) {
      if(signal?.aborted)throw new DOMException('Capture aborted','AbortError');
      await adapter.restoreState(initial); await adapter.setView(view);await adapter.setMode(mode);
      await adapter.ready(signal);await adapter.render();
      if(signal?.aborted)throw new DOMException('Capture aborted','AbortError');
      const result=await adapter.capture({view,mode});
      if(signal?.aborted)throw new DOMException('Capture aborted','AbortError');
      captures.push({view:view.id,mode,result});
    } return captures;
  } finally {await adapter.restoreState(initial);}
}
const counts = s => {
  if(!s||!Object.keys(s).length)throw new TypeError('Nonempty resource snapshot required');
  for(const [k,v]of Object.entries(s))if(!Number.isSafeInteger(v)||v<0)throw new TypeError('Invalid resource counter '+k);
  return s;
};
export async function lifecycleProbe(adapter,{phases=['ready','fetch','decode'],cycles=2}={}) {
  for(const method of ['snapshot','begin','waitForPhase','dispose','settle'])
    if(typeof adapter[method]!=='function')throw new TypeError('Missing '+method);
  if(!Number.isInteger(cycles)||cycles<1||!phases.length)throw new TypeError('Nonempty phases and positive cycles required');
  const baseline=structuredClone(counts(await adapter.snapshot())),rows=[];
  for(let cycle=0;cycle<cycles;cycle++)for(const phase of phases) {
    const abort=new AbortController();let handle;
    const failures=[];
    try {
      handle=await adapter.begin({signal:abort.signal});
      await adapter.waitForPhase(handle,phase);
    } catch(error) {failures.push(error);}
    finally {
      abort.abort();
      if(handle!==undefined) for(const step of ['dispose','settle','dispose']) {
        try {await adapter[step](handle);} catch(error) {failures.push(error);}
      }
    }
    if(failures.length)throw new AggregateError(failures,'Lifecycle phase or cleanup failed');
    const after=structuredClone(counts(await adapter.snapshot()));
    const keys=new Set([...Object.keys(baseline),...Object.keys(after)]);
    const leaks=[...keys].filter(key=>(after[key]??0)>(baseline[key]??0));
    rows.push({cycle,phase,after,pass:!leaks.length,leaks});
  }
  return {baseline,rows,pass:rows.every(r=>r.pass),limitation:'Ownership counter trend only; not exact GPU residency'};
}
