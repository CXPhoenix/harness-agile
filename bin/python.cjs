// Forward argv without a shell. Both entry points run the same Python package.
const { spawnSync } = require('node:child_process');
const path = require('node:path');
const root = path.resolve(__dirname, '..');

function interpreter() {
  const choices = process.env.HARNESS_PYTHON
    ? [[process.env.HARNESS_PYTHON]]
    : (process.platform === 'win32' ? [['py', '-3'], ['python'], ['python3']] : [['python3'], ['python']]);
  for (const choice of choices) {
    const result = spawnSync(choice[0], [...choice.slice(1), '-c', 'import sys; sys.exit(0 if sys.version_info >= (3,11) else 1)'], { stdio: 'ignore' });
    if (result.status === 0) return choice;
  }
  if (!process.env.HARNESS_PYTHON && spawnSync('uv', ['--version'], { stdio: 'ignore' }).status === 0) {
    return ['uv', 'run', '--no-project', '--python', '3.11', 'python'];
  }
  throw new Error('Python 3.11+ or uv is required. Install either, or set HARNESS_PYTHON to a Python executable.');
}

function execute(args) {
  try {
    const choice = interpreter();
    const result = spawnSync(choice[0], [...choice.slice(1), '-B', ...args], {
      stdio: 'inherit', env: { ...process.env, PYTHONUTF8: '1', PYTHONDONTWRITEBYTECODE: '1' },
    });
    if (result.error) throw result.error;
    return result.status ?? 1;
  } catch (error) {
    console.error(error.message);
    return 1;
  }
}

module.exports = { execute, root };
if (require.main === module) process.exitCode = execute(process.argv.slice(2));
