#!/usr/bin/env python3
"""Run built packages through uvx, npx and pnpx outside the source checkout."""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import tempfile
import zipfile


def run(args, cwd):
    env = {**os.environ, 'PYTHONUTF8': '1', 'HARNESS_PYTHON': sys.executable}
    command = [shutil.which(args[0]) or args[0], *args[1:]]
    result = subprocess.run(command, cwd=cwd, env=env, text=True, encoding='utf-8', capture_output=True, timeout=180)
    if result.returncode:
        raise RuntimeError(f'{args[0]} failed ({result.returncode}):\n{result.stdout}\n{result.stderr}')
    return result.stdout


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--wheel', required=True, type=Path)
    parser.add_argument('--npm', required=True, type=Path)
    args = parser.parse_args()
    wheel, npm = args.wheel.resolve(), args.npm.resolve()
    with zipfile.ZipFile(wheel) as archive:
        python_bundle = json.loads(archive.read('harness_agile/data/template.json'))
    with tarfile.open(npm) as archive:
        assert not any(member.issym() or member.islnk() for member in archive), 'npm artifact contains links'
        node_bundle = json.load(archive.extractfile('package/harness_agile/data/template.json'))
    assert python_bundle['source']['content_sha256'] == node_bundle['source']['content_sha256'], 'Entry points bundled different template content'
    with tempfile.TemporaryDirectory(prefix='harness-package-e2e-') as temp:
        parent = Path(temp)
        rows = []
        commands = [
            ('uvx', ['uvx', '--from', str(wheel), 'harness-agile'], 'auto'),
            ('npx', ['npx', '--yes', '--package', str(npm), 'create-harness-agile'], 'copy'),
            ('pnpx', ['pnpx', str(npm)], 'copy'),
        ]
        for label, command, mode in commands:
            target = parent / (label + ' 專案 with spaces')
            output = run([*command, 'init', str(target), '--name', '套件驗證', '--one-liner', '保留 $() 與 `literal`。', '--skill-mode', mode, '--no-input', '--json'], parent)
            report = json.loads(output.strip().splitlines()[-1])
            assert report['skills'] == 30, report
            assert not (target / 'package.json').exists()
            assert not (target / 'pyproject.toml').exists()
            assert not (target / '.git').exists()
            assert not (target / '.tmpl.docs').exists()
            assert '保留 $() 與 `literal`。' in (target / 'AGENTS.md').read_text(encoding='utf-8')
            run([sys.executable, '-B', str(target / 'scripts/verify-project.py')], parent)
            rows.append({'entry': label, 'skills': report['skills'], 'mode': report['skill_mode'], 'passed': True})
        print(json.dumps({'platform': sys.platform, 'python': sys.version.split()[0], 'source': python_bundle['source'], 'checks': rows}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
