#!/usr/bin/env node
const { execute, root } = require('./python.cjs');
process.exitCode = execute([
  '-c', 'import sys; sys.path.insert(0, sys.argv.pop(1)); from harness_agile.cli import main; sys.exit(main())',
  root, ...process.argv.slice(2),
]);
