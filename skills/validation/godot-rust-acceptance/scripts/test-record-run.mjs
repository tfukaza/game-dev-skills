// First-party synthetic process controls; no Rust, Godot, or game timing runs.
import fs from 'node:fs';
import crypto from 'node:crypto';
import { spawnSync } from 'node:child_process';
import os from 'node:os';
import path from 'node:path';

const root = fs.mkdtempSync(path.join(os.tmpdir(), 'godot-rust-recorder-tests-'));
const helper = new URL('./record-run.mjs', import.meta.url).pathname;
const hash = bytes => crypto.createHash('sha256').update(bytes).digest('hex');
const check = (condition, message) => { if (!condition) throw Error(message); };
const read = filename => JSON.parse(fs.readFileSync(filename, 'utf8'));
const results = [];

function scenario(name, code, changes = {}) {
  const directory = root + '/' + name;
  fs.mkdirSync(directory);
  fs.writeFileSync(directory + '/input.txt', 'original input\n');
  const output = directory + '/output';
  const config = { cwd: directory, inputRoot: directory,
    inputs: [{ path: 'input.txt', sha256: hash(fs.readFileSync(directory + '/input.txt')) }],
    command: [process.execPath, '-e', code(directory, output)], wallLimitMs: 2000,
    expectedNativeExit: 0, requiredStdout: ['DONE'], forbiddenStdout: ['PASS'],
    requiredStderr: [], forbiddenStderr: [], ...changes };
  fs.writeFileSync(directory + '/config.json', JSON.stringify(config) + '\n');
  return { directory, output, config };
}

function execute(s) {
  const native = spawnSync(process.execPath, [helper, s.directory + '/config.json', s.output], {
    encoding: 'utf8', timeout: 8000,
  });
  check(!native.error && native.signal === null, 'recorder unexpectedly failed to terminate');
  return { native, receipt: fs.existsSync(s.output + '/result.json') ? read(s.output + '/result.json') : null };
}

function control(name, body) {
  try {
    const evidence = body();
    results.push({ name, passed: true, ...evidence });
  } catch (error) {
    results.push({ name, passed: false, error: error.message });
  }
}

control('success and full raw streams with prelaunch evidence', () => {
  const stdout = Buffer.concat([Buffer.from('raw line\n'.repeat(70000)), Buffer.from([0, 255, 128]), Buffer.from('\nDONE\n')]);
  const stderr = Buffer.from('stderr line\n'.repeat(50000));
  const s = scenario('success', (_directory, output) => `
    const fs = require('node:fs');
    const preflight = JSON.parse(fs.readFileSync(${JSON.stringify(output + '/preflight.json')}, 'utf8'));
    if (!preflight.successful || preflight.childStarted) process.exit(7);
    fs.accessSync(${JSON.stringify(output + '/expected.json')});
    fs.writeSync(1, Buffer.concat([Buffer.from('raw line\\n'.repeat(70000)), Buffer.from([0,255,128]), Buffer.from('\\nDONE\\n')]));
    fs.writeSync(2, Buffer.from('stderr line\\n'.repeat(50000)));
  `);
  const { native, receipt } = execute(s);
  check(native.status === 0 && receipt.nativeExit === 0 && receipt.gatePassed, 'success not accepted');
  check(fs.readFileSync(s.output + '/stdout.bin').equals(stdout), 'stdout bytes lost or truncated');
  check(fs.readFileSync(s.output + '/stderr.bin').equals(stderr), 'stderr bytes lost or truncated');
  check(receipt.logs.stdout.sha256 === hash(stdout) && receipt.logs.stderr.sha256 === hash(stderr), 'raw hashes disagree');
  check(receipt.inputsBefore[0].actualSha256 === receipt.inputsAfter[0].actualSha256, 'success input changed');
  return { output: s.output, recorderExit: native.status, childExit: receipt.nativeExit, rawBytes: stdout.length + stderr.length };
});

control('intended exit2 diagnostic with empty stdout and no PASS', () => {
  const s = scenario('negative', () => "process.stderr.write('typed diagnostic: invalid input\\n'); process.exitCode = 2;", {
    expectedNativeExit: 2, requiredStdout: [], stdoutEmpty: true, requiredStderr: ['typed diagnostic: invalid input'],
  });
  const { native, receipt } = execute(s);
  check(native.status === 0 && receipt.nativeExit === 2 && receipt.gatePassed, 'expected negative status confused with recorder failure');
  check(fs.statSync(s.output + '/stdout.bin').size === 0, 'negative stdout not empty');
  check(fs.readFileSync(s.output + '/stderr.bin', 'utf8') === 'typed diagnostic: invalid input\n', 'negative diagnostic missing');
  return { output: s.output, recorderExit: native.status, childExit: receipt.nativeExit };
});

control('mismatched input cannot launch marker child', () => {
  const s = scenario('mismatch', directory => `require('node:fs').writeFileSync(${JSON.stringify(directory + '/child-marker')}, 'launched'); console.log('DONE');`, {
    inputs: [{ path: 'input.txt', sha256: '0'.repeat(64) }],
  });
  const { native, receipt } = execute(s);
  check(native.status === 1 && !receipt.childStarted && !receipt.gatePassed, 'mismatch did not refuse');
  check(!fs.existsSync(s.directory + '/child-marker'), 'child launched after failed preflight');
  check(read(s.output + '/preflight.json').successful === false, 'failed preflight not retained');
  check(!fs.existsSync(s.output + '/stdout.bin'), 'launch streams created after refusal');
  return { output: s.output, recorderExit: native.status, childStarted: receipt.childStarted };
});

control('existing output directory remains untouched and no child', () => {
  const s = scenario('existing', directory => `require('node:fs').writeFileSync(${JSON.stringify(directory + '/child-marker')}, 'launched'); console.log('DONE');`);
  fs.mkdirSync(s.output);
  fs.writeFileSync(s.output + '/sentinel', 'preserve me');
  const { native, receipt } = execute(s);
  check(native.status === 2 && receipt === null, 'existing directory did not refuse');
  check(fs.readdirSync(s.output).join() === 'sentinel' && fs.readFileSync(s.output + '/sentinel', 'utf8') === 'preserve me', 'existing output was overwritten');
  check(!fs.existsSync(s.directory + '/child-marker'), 'existing output launched child');
  return { output: s.output, recorderExit: native.status, diagnostic: native.stderr.trim() };
});

control('input mutation during run fails integrity after native0', () => {
  const s = scenario('mutation', directory => `require('node:fs').writeFileSync(${JSON.stringify(directory + '/input.txt')}, 'changed by child'); console.log('DONE');`);
  const { native, receipt } = execute(s);
  check(native.status === 1 && receipt.nativeExit === 0 && !receipt.gatePassed, 'mutated native0 accepted');
  check(!receipt.integrity.inputs && receipt.inputsBefore[0].actualSha256 !== receipt.inputsAfter[0].actualSha256, 'mutation evidence absent');
  return { output: s.output, recorderExit: native.status, childExit: receipt.nativeExit };
});

control('exact own child timeout retains raw streams and cannot PASS', () => {
  const s = scenario('timeout', () => "process.stdout.write('READY\\n'); process.stderr.write('waiting\\n'); setTimeout(() => console.log('PASS'), 3000); setInterval(() => {}, 50);", {
    wallLimitMs: 500, requiredStdout: ['READY'],
  });
  const { native, receipt } = execute(s);
  check(native.status === 1 && receipt.timedOut && receipt.signal === 'SIGKILL' && !receipt.gatePassed, 'timeout did not latch failure');
  check(fs.readFileSync(s.output + '/stdout.bin', 'utf8') === 'READY\n' && fs.readFileSync(s.output + '/stderr.bin', 'utf8') === 'waiting\n', 'timeout raw output lost or late PASS occurred');
  let alive = true;
  try { process.kill(receipt.pid, 0); } catch (error) { if (error.code === 'ESRCH') alive = false; else throw error; }
  check(!alive, 'exact test child still alive');
  return { output: s.output, recorderExit: native.status, childSignal: receipt.signal, elapsedMs: receipt.elapsedMs };
});

const report = { scope: 'Six synthetic native recorder controls only; no game or benchmark execution',
  helperSha256: hash(fs.readFileSync(helper)), testSha256: hash(fs.readFileSync(new URL(import.meta.url))), results };
fs.writeFileSync(root + '/test-results.json', JSON.stringify(report, null, 2) + '\n', { flag: 'wx' });
process.stdout.write(JSON.stringify({ root, passed: results.filter(r => r.passed).length, total: results.length, results }) + '\n');
if (results.some(r => !r.passed)) process.exitCode = 1;
