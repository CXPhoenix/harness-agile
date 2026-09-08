const fs = require('node:fs');
const path = require('node:path');
const { execute, root } = require('./python.cjs');
if (fs.existsSync(path.join(root, 'scripts', 'init-project.py'))) {
  process.exitCode = execute([
    '-c', 'import sys; sys.path.insert(0, sys.argv[1]); from harness_agile.bundle import build; build(sys.argv[1])', root,
  ]);
} else if (!fs.existsSync(path.join(root, 'harness_agile', 'data', 'template.json'))) {
  console.error('Template bundle missing; install from the complete Git source or a built package.');
  process.exitCode = 1;
}
