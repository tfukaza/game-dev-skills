/** Browser-compatible frame recorder and conservative serial ABBA experiment.
 * No Three.js dependency, readbacks, DOM counters, or implicit quality changes.
 */
const finitePositive = (n, name) => { if (!Number.isFinite(n) || n <= 0) throw new TypeError(name + ' must be positive'); };
const percentile = (sorted, q) => sorted[Math.min(sorted.length - 1, Math.floor((sorted.length - 1) * q))];
export function summarizeFrames(timestamps, budgetMs = 1000 / 60) {
  finitePositive(budgetMs, 'budgetMs');
  if (!Array.isArray(timestamps) || timestamps.length < 3 || timestamps.some(v => !Number.isFinite(v))) throw new TypeError('At least three finite frame timestamps required');
  const durations = timestamps.slice(1).map((v, i) => v - timestamps[i]);
  if (durations.some(v => v <= 0)) throw new TypeError('Timestamps must increase strictly');
  const sorted = [...durations].sort((a,b) => a-b);
  const total = durations.reduce((a,b) => a+b, 0);
  return {frames: durations.length, durationMs: total, meanMs: total / durations.length,
    medianMs: percentile(sorted,.5), p95Ms: percentile(sorted,.95), p99Ms: percentile(sorted,.99),
    maximumMs: sorted.at(-1), averageFps: durations.length * 1000 / total,
    overBudgetFrames: durations.filter(v => v > budgetMs).length,
    stallsOver50Ms: durations.filter(v => v > 50).length, budgetMs};
}
export function recordFrames({durationMs = 30000, signal, raf = globalThis.requestAnimationFrame?.bind(globalThis), cancel = globalThis.cancelAnimationFrame?.bind(globalThis)} = {}) {
  finitePositive(durationMs, 'durationMs');
  if (!raf || !cancel) throw new TypeError('Browser RAF or injected scheduler required');
  return new Promise((resolve,reject) => {
    let id, start, done = false; const timestamps = [];
    const finish = (error) => { if (done) return; done = true; if (id !== undefined) cancel(id); signal?.removeEventListener('abort', abort); error ? reject(error) : resolve(timestamps); };
    const abort = () => finish(new DOMException('Sampling aborted','AbortError'));
    const frame = stamp => {
      if (done) return;
      if (!Number.isFinite(stamp) || (timestamps.length && stamp <= timestamps.at(-1))) return finish(new Error('Invalid RAF timestamps'));
      start ??= stamp; timestamps.push(stamp);
      if (stamp - start >= durationMs && timestamps.length >= 3) finish();
      else id = raf(frame);
    };
    if (signal?.aborted) return abort();
    signal?.addEventListener('abort',abort,{once:true}); id = raf(frame);
  });
}
const canonical = value => {
  if (Array.isArray(value)) return '[' + value.map(canonical).join(',') + ']';
  if (value && typeof value === 'object') return '{' + Object.keys(value).sort().map(k => JSON.stringify(k)+':'+canonical(value[k])).join(',') + '}';
  return JSON.stringify(value);
};
export function compareABBA(runs, {minimumRelativeGain = .03} = {}) {
  if (!Number.isFinite(minimumRelativeGain) || minimumRelativeGain < 0 || minimumRelativeGain >= 1) throw new TypeError('Invalid gain tolerance');
  if (!Array.isArray(runs) || runs.length < 4 || runs.length % 4) throw new TypeError('Full ABBA blocks required');
  const reference = canonical(runs[0].conditions);
  const required = ['viewport','drawingBuffer','camera','preset','device','sceneRevision'];
  for (let i=0;i<runs.length;i++) {
    const r = runs[i];
    if (r.variant !== ['A','B','B','A'][i%4]) throw new Error('Run ordering must be ABBA');
    if (!r.conditions || required.some(k => r.conditions[k] === undefined)) throw new Error('Missing controlled conditions');
    if (canonical(r.conditions) !== reference) return {verdict:'incomparable',reason:'Controlled conditions changed'};
    if (r.visualPassed !== true) return {verdict:'rejected-quality',reason:'Every run requires explicit visual/gameplay acceptance'};
    finitePositive(r.stats?.medianMs, 'medianMs');
  }
  const pairs = [];
  for (let i=0;i<runs.length;i+=2) {
    const a = runs[i].variant === 'A' ? runs[i] : runs[i+1];
    const b = runs[i].variant === 'B' ? runs[i] : runs[i+1];
    pairs.push((a.stats.medianMs-b.stats.medianMs)/a.stats.medianMs);
  }
  const mean = values => values.reduce((a,b)=>a+b,0)/values.length;
  return {verdict:pairs.every(v => v > minimumRelativeGain) ? 'consistent-gain' : pairs.every(v => v < -minimumRelativeGain) ? 'consistent-regression' : 'inconclusive',
    pairRelativeGains:pairs, meanRelativeGain:mean(pairs), minimumRelativeGain,
    caveat:'Consistency heuristic only; not statistical significance or proof on other devices'};
}
export async function runABBA(adapter, {blocks=1, signal} = {}) {
  if (!Number.isInteger(blocks) || blocks < 1) throw new TypeError('blocks must be a positive integer');
  for (const name of ['saveState','restoreState','setVariant','ready','warmup','measure','conditions','checkQuality'])
    if (typeof adapter[name] !== 'function') throw new TypeError('Missing adapter method '+name);
  const state = await adapter.saveState(), runs = [];
  const checkAbort = () => { if (signal?.aborted) throw new DOMException('Experiment aborted','AbortError'); };
  try {
    for (let i=0;i<blocks;i++) for (const variant of ['A','B','B','A']) {
      checkAbort(); await adapter.setVariant(variant); await adapter.ready(signal); checkAbort();
      await adapter.warmup(signal); checkAbort();
      const conditions = structuredClone(await adapter.conditions());
      const timestamps = await adapter.measure(signal); checkAbort();
      if (canonical(conditions) !== canonical(await adapter.conditions())) throw new Error('Conditions changed during sample');
      const visualPassed=await adapter.checkQuality(variant);checkAbort();
      runs.push({variant,conditions,stats:summarizeFrames(timestamps, adapter.budgetMs),visualPassed,timestamps});
    }
    return {runs,comparison:compareABBA(runs)};
  } finally { await adapter.restoreState(state); }
}
