// First-party recorder for one explicitly configured native command.
// This verifies configured evidence, not the correctness of a game or its tests.
import fs from 'node:fs';
import crypto from 'node:crypto';
import { spawn } from 'node:child_process';

const digest = bytes => crypto.createHash('sha256').update(bytes).digest('hex');
const fileHash = filename => digest(fs.readFileSync(filename));
const inside = (filename, directory) => directory === '/' || filename === directory || filename.startsWith(directory + '/');
const ownFile = fs.realpathSync(new URL(import.meta.url));
const utc = () => new Date().toISOString();

function absolute(value, label) {
  if (typeof value !== 'string' || !value.startsWith('/') || value.includes('\0') ||
      value.split('/').some(part => part === '.' || part === '..')) {
    throw Error(`${label} must be an absolute path without dot components`);
  }
  return '/' + value.split('/').filter(Boolean).join('/');
}

function validate(config, output) {
  if (!config || typeof config !== 'object' || Array.isArray(config)) throw Error('config must be an object');
  config.cwd = fs.realpathSync(absolute(config.cwd, 'cwd'));
  config.inputRoot = fs.realpathSync(absolute(config.inputRoot, 'inputRoot'));
  for (const key of ['cwd', 'inputRoot']) {
    if (!fs.statSync(config[key]).isDirectory()) throw Error(`${key} must be a directory`);
  }
  if (!Array.isArray(config.command) || config.command.length === 0 ||
      config.command.some(arg => typeof arg !== 'string' || arg.includes('\0'))) {
    throw Error('command must be a nonempty string array without NUL bytes');
  }
  absolute(config.command[0], 'command executable');
  if (!Number.isFinite(config.wallLimitMs) || config.wallLimitMs < 1 || config.wallLimitMs > 60000) {
    throw Error('wallLimitMs must be finite and within 1..60000');
  }
  if (!Number.isInteger(config.expectedNativeExit) || config.expectedNativeExit < 0 || config.expectedNativeExit > 255) {
    throw Error('expectedNativeExit must be an integer within 0..255');
  }
  if (!Array.isArray(config.inputs) || config.inputs.length === 0) throw Error('inputs must be a nonempty array');
  const paths = new Set();
  for (const input of config.inputs) {
    if (!input || typeof input.path !== 'string' || input.path.includes('\0') ||
        input.path.split('/').some(part => !part || part === '.' || part === '..') ||
        !/^[a-f0-9]{64}$/.test(input.sha256 ?? '') || paths.has(input.path)) {
      throw Error('inputs require unique relative file paths and lowercase SHA-256 strings');
    }
    paths.add(input.path);
    if (inside(config.inputRoot + '/' + input.path, output)) throw Error('source inputs cannot reside in the output directory');
  }
  let assertions = 0;
  for (const key of ['requiredStdout', 'forbiddenStdout', 'requiredStderr', 'forbiddenStderr']) {
    if (!Array.isArray(config[key]) || config[key].some(s => typeof s !== 'string' || s.length === 0)) {
      throw Error(`${key} must be an array of nonempty literal strings`);
    }
    assertions += config[key].length;
  }
  if (config.stdoutEmpty !== undefined && typeof config.stdoutEmpty !== 'boolean') throw Error('stdoutEmpty must be boolean');
  if (assertions === 0 && config.stdoutEmpty !== true) throw Error('configure an output assertion; native exit alone is not acceptance');
  return config;
}

function inspect(config, output) {
  return config.inputs.map(input => {
    const record = { path: input.path, expectedSha256: input.sha256, actualSha256: null, error: null };
    try {
      const resolved = fs.realpathSync(config.inputRoot + '/' + input.path);
      if (!inside(resolved, config.inputRoot) || inside(resolved, output)) throw Error('resolved source escapes inputRoot or enters output directory');
      if (!fs.statSync(resolved).isFile()) throw Error('source input is not a regular file');
      record.resolvedPath = resolved;
      record.actualSha256 = fileHash(resolved);
    } catch (error) {
      record.error = error.message;
    }
    return record;
  });
}

function outputAssertions(config, stdout, stderr, stdoutBytes) {
  const checks = [];
  for (const [stream, text] of [['Stdout', stdout], ['Stderr', stderr]]) {
    for (const kind of ['required', 'forbidden']) {
      for (const literal of config[kind + stream]) {
        checks.push({ stream: stream.toLowerCase(), kind, literal,
          passed: kind === 'required' ? text.includes(literal) : !text.includes(literal) });
      }
    }
  }
  if (config.stdoutEmpty === true) checks.push({ stream: 'stdout', kind: 'empty', passed: stdoutBytes === 0 });
  return checks;
}

function writeNew(output, name, value) {
  const bytes = Buffer.from(JSON.stringify(value, null, 2) + '\n');
  fs.writeFileSync(output + '/' + name, bytes, { flag: 'wx' });
  return digest(bytes);
}

async function run(configFile, output) {
  const result = { schema: 1, scope: 'Configured native command evidence only; no game correctness or execution authorization implied',
    recorderStarted: utc(), childStarted: false, started: null, ended: null,
    nativeExit: null, signal: null, error: null, timedOut: false, gatePassed: false };
  let config;
  try {
    const bytes = fs.readFileSync(configFile);
    result.config = { source: fs.realpathSync(configFile), sha256: digest(bytes) };
    result.helper = { source: ownFile, sha256: fileHash(ownFile) };
    if (inside(result.config.source, output) || inside(ownFile, output)) throw Error('config/helper cannot reside in output directory');
    fs.writeFileSync(output + '/config.json', bytes, { flag: 'wx' });
    config = validate(JSON.parse(bytes), output);
    result.command = config.command;
    result.cwd = config.cwd;
    result.expectedNativeExit = config.expectedNativeExit;
    result.wallLimitMs = config.wallLimitMs;
    result.expectedHash = writeNew(output, 'expected.json', { config: result.config, helper: result.helper,
      inputs: config.inputs, command: config.command, cwd: config.cwd });
  } catch (error) {
    result.error = error.message;
    result.refusal = 'invalid configuration';
    result.preflightHash = writeNew(output, 'preflight.json', { at: utc(), successful: false,
      childStarted: false, error: error.message });
    result.recorderExit = 2;
    writeNew(output, 'result.json', result);
    return result;
  }

  result.inputsBefore = inspect(config, output);
  const successful = result.inputsBefore.every(r => !r.error && r.actualSha256 === r.expectedSha256);
  result.preflightHash = writeNew(output, 'preflight.json', { at: utc(), successful,
    childStarted: false, config: result.config, helper: result.helper, inputs: result.inputsBefore });
  if (!successful) {
    result.refusal = 'input preflight failed; child not started';
    result.recorderExit = 1;
    writeNew(output, 'result.json', result);
    return result;
  }

  let stdoutFd, stderrFd;
  try {
    stdoutFd = fs.openSync(output + '/stdout.bin', 'wx');
    stderrFd = fs.openSync(output + '/stderr.bin', 'wx');
    const monotonicStart = performance.now();
    result.started = utc();
    const child = spawn(config.command[0], config.command.slice(1), {
      cwd: config.cwd, shell: false, stdio: ['ignore', stdoutFd, stderrFd],
    });
    result.childStarted = Boolean(child.pid);
    result.pid = child.pid ?? null;
    let killError = null;
    const timer = setTimeout(() => {
      // Latch failure before killing precisely the child created above.
      result.timedOut = true;
      try { if (!child.kill('SIGKILL')) killError = 'own child kill returned false'; }
      catch (error) { killError = error.message; }
    }, Math.max(1, config.wallLimitMs - (performance.now() - monotonicStart)));
    const native = await new Promise(resolve => {
      child.once('error', error => resolve({ nativeExit: null, signal: null, error: error.message }));
      child.once('close', (nativeExit, signal) => resolve({ nativeExit, signal, error: null }));
    });
    clearTimeout(timer);
    Object.assign(result, native);
    result.ended = utc();
    result.elapsedMs = performance.now() - monotonicStart;
    if (result.elapsedMs > config.wallLimitMs) result.timedOut = true;
    result.killError = killError;
  } catch (error) {
    result.error = error.message;
    result.ended = utc();
  } finally {
    if (stdoutFd !== undefined) fs.closeSync(stdoutFd);
    if (stderrFd !== undefined) fs.closeSync(stderrFd);
  }

  result.inputsAfter = inspect(config, output);
  result.integrity = { inputs: JSON.stringify(result.inputsBefore) === JSON.stringify(result.inputsAfter),
    config: false, helper: false, expected: false, preflight: false };
  try {
    result.integrity.config = fileHash(result.config.source) === result.config.sha256 &&
      fileHash(output + '/config.json') === result.config.sha256;
    result.integrity.helper = fileHash(ownFile) === result.helper.sha256;
    result.integrity.expected = fileHash(output + '/expected.json') === result.expectedHash;
    result.integrity.preflight = fileHash(output + '/preflight.json') === result.preflightHash;
  } catch (error) { result.integrityError = error.message; }
  try {
    const stdout = fs.readFileSync(output + '/stdout.bin');
    const stderr = fs.readFileSync(output + '/stderr.bin');
    result.logs = { stdout: { path: 'stdout.bin', bytes: stdout.length, sha256: digest(stdout) },
      stderr: { path: 'stderr.bin', bytes: stderr.length, sha256: digest(stderr) } };
    result.assertions = outputAssertions(config, stdout.toString('utf8'), stderr.toString('utf8'), stdout.length);
  } catch (error) { result.error = result.error ?? error.message; }
  result.gatePassed = result.childStarted && !result.error && !result.timedOut &&
    result.nativeExit === config.expectedNativeExit && result.signal === null &&
    Object.values(result.integrity).every(Boolean) && !!result.assertions &&
    result.assertions.every(check => check.passed);
  result.recorderExit = result.gatePassed ? 0 : 1;
  writeNew(output, 'result.json', result);
  return result;
}

async function main() {
  if (process.argv.length !== 4) throw Error('usage: node record-run.mjs CONFIG.json NEW_OUTPUT_DIRECTORY');
  let output = absolute(process.argv[3], 'output directory');
  if (output === '/') throw Error('output directory must be new');
  const slash = output.lastIndexOf('/');
  const parent = fs.realpathSync(output.slice(0, slash) || '/');
  output = (parent === '/' ? '' : parent) + output.slice(slash);
  // Exclusive directory creation precedes every output write and child launch.
  fs.mkdirSync(output);
  const result = await run(process.argv[2], output);
  process.stdout.write(JSON.stringify({ output, childStarted: result.childStarted,
    nativeExit: result.nativeExit, timedOut: result.timedOut, gatePassed: result.gatePassed,
    recorderExit: result.recorderExit, error: result.error }) + '\n');
  process.exitCode = result.recorderExit;
}

main().catch(error => {
  process.stderr.write('Recorder refusal: ' + error.message + '\n');
  process.exitCode = 2;
});
