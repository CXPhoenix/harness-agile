#!/usr/bin/env python3
"""Run built packages through uvx, npx and pnpx outside the source checkout."""
import argparse
import base64
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
    notice_paths = [name for name in python_bundle['files'] if
                    name in {'LICENSE', 'THIRD_PARTY_NOTICES.md'} or
                    name.endswith('/LICENSE') or name.endswith('/THIRD_PARTY_NOTICES.md') or
                    name.endswith('/JetBrainsMono-OFL.txt')]
    assert '.agents/skills/evidence-report/LICENSE' in notice_paths
    assert not any(any(part in {'.proj.vuln.recur', 'node_modules'} for part in name.split('/'))
                   for name in python_bundle['files']), 'Private lab or development dependencies in bundle'
    with zipfile.ZipFile(wheel) as archive:
        license_roots = [name for name in archive.namelist() if name.endswith('.dist-info/METADATA')]
        assert len(license_roots) == 1
        license_root = license_roots[0].rsplit('/', 1)[0] + '/licenses/'
        for name in notice_paths:
            assert archive.read(license_root + name) == base64.b64decode(python_bundle['files'][name]), name
    with tarfile.open(npm) as archive:
        assert not any(member.issym() or member.islnk() for member in archive), 'npm artifact contains links'
        assert not any(any(part in {'.proj.vuln.recur', 'node_modules'} for part in member.name.split('/')) for member in archive), 'Private lab or development dependencies in npm archive'
        manifest = json.load(archive.extractfile('package/package.json'))
        assert not ({'prepare', 'prepack', 'preinstall', 'install', 'postinstall'} & manifest.get('scripts', {}).keys()), 'npm install must not require build scripts'
        node_files = {name: base64.b64encode(archive.extractfile('package/' + name).read()).decode('ascii') for name in python_bundle['files']}
    assert python_bundle['files'] == node_files, 'Entry points bundled different template content'
    with tempfile.TemporaryDirectory(prefix='harness-package-e2e-') as temp:
        parent = Path(temp)
        # dlx caches local tarball specifiers; each run must install today's bytes.
        fresh_npm = parent / npm.name
        shutil.copyfile(npm, fresh_npm)
        rows = []
        commands = [
            ('uvx', ['uvx', '--from', str(wheel), 'harness-agile'], 'auto'),
            ('npx', ['npx', '--yes', '--package', str(fresh_npm), 'create-harness-agile'], 'copy'),
            ('pnpx', ['pnpx', str(fresh_npm)], 'copy'),
        ]
        for label, command, mode in commands:
            target = parent / (label + ' 專案 with spaces')
            output = run([*command, 'init', str(target), '--name', '套件驗證', '--one-liner', '保留 $() 與 `literal`。', '--skill-mode', mode, '--no-input', '--json'], parent)
            report = json.loads(output.strip().splitlines()[-1])
            assert report['source']['content_sha256'] == python_bundle['source']['content_sha256'], report
            assert report['skills'] == 31, report
            for name in notice_paths:
                assert (target / name).read_bytes() == base64.b64decode(python_bundle['files'][name]), (label, name)
            assert not (target / 'CHANGELOG.md').exists()
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
