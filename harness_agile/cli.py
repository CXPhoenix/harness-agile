"""Create a project from the bundled template or an explicit local source."""
import argparse
import datetime
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

from . import __version__
from .bundle import snapshot, unpack


def run(command, cwd):
    result = subprocess.run(command, cwd=cwd, text=True, encoding='utf-8', capture_output=True, env={**os.environ, 'PYTHONUTF8': '1'})
    if result.returncode:
        raise ValueError((result.stderr or result.stdout).strip())
    return result.stdout


def empty_target(target):
    if target.is_symlink() or (target.exists() and (not target.is_dir() or any(target.iterdir()))):
        raise ValueError(f'Target must be absent or an empty real directory: {target}')
    if not target.parent.is_dir():
        raise ValueError(f'Target parent directory must already exist: {target.parent}')


def create(args):
    target = Path(args.directory).expanduser().absolute()
    empty_target(target)
    if args.source:
        source = Path(args.source).expanduser().resolve()
        if target.resolve().is_relative_to(source) or source.is_relative_to(target.resolve()):
            raise ValueError('Target and local template source must be separate directories')
    for key in ('name', 'one_liner'):
        value = getattr(args, key)
        if not value and not args.no_input and not args.json and sys.stdin.isatty():
            value = input(f'Project {key.replace("_", " ")}: ').strip()
            setattr(args, key, value)
        if not value or not value.strip() or any(c in value for c in '\r\n\x00') or '{{' in value:
            raise ValueError(f'--{key.replace("_", "-")} requires a nonempty single line without template tokens')
    datetime.date.fromisoformat(args.date)
    if len(args.date) != 10:
        raise ValueError('--date must use YYYY-MM-DD')
    if args.source:
        bundle = snapshot(source)
    else:
        resource = Path(__file__).parent / 'data/template.json'
        if resource.is_file():
            bundle = json.loads(resource.read_text(encoding='utf-8'))
        else:
            # npm ships regular source files and needs no install-time scripts.
            bundle = snapshot(Path(__file__).resolve().parents[1])
    result = {'target': str(target), 'generator_version': __version__, 'source': bundle['source'], 'dry_run': args.dry_run}
    if args.dry_run:
        return result
    with tempfile.TemporaryDirectory(prefix='.harness-', dir=target.parent) as temp:
        staging = Path(temp) / 'project'
        staging.mkdir()
        unpack(bundle, staging)
        command = [sys.executable, '-B', 'scripts/init-project.py', '--name', args.name, '--one-liner', args.one_liner, '--date', args.date, '--skill-mode', args.skill_mode]
        if args.keep_template_files:
            command.append('--keep-template-files')
        run(command, staging)
        run([sys.executable, '-B', 'scripts/verify-project.py'], staging)
        entries = list((staging / '.claude/skills').iterdir())
        result.update(skills=len(entries), skill_mode='+'.join(sorted({'symlink' if p.is_symlink() else 'copy' for p in entries})))
        result['next_step'] = 'Open this directory in Claude Code or Codex and use grill-with-docs to define the Project Charter.'
        provenance = {**bundle['source'], 'generator_version': __version__, 'initialized_on': args.date, 'skill_mode': result['skill_mode']}
        (staging / 'docs/agents/template-source.json').write_text(json.dumps(provenance, indent=2) + '\n', encoding='utf-8')
        if args.git:
            run(['git', 'init', '-b', 'main'], staging)
        empty_target(target)
        if target.exists():
            target.rmdir()
        staging.rename(target)
    return result


def main(argv=None):
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--version', action='version', version=__version__)
    commands = parser.add_subparsers(dest='command', required=True)
    init = commands.add_parser('init', help='Create a new local project (no remote or commit)')
    init.add_argument('directory')
    init.add_argument('--name')
    init.add_argument('--one-liner')
    init.add_argument('--date', default=datetime.date.today().isoformat())
    init.add_argument('--source', help='Explicit local uninitialized template source; otherwise use the bundled version')
    init.add_argument('--skill-mode', choices=['auto', 'symlink', 'copy'], default='auto')
    for flag in ('keep-template-files', 'no-input', 'json', 'dry-run', 'git'):
        init.add_argument('--' + flag, action='store_true')
    args = parser.parse_args(argv)
    try:
        result = create(args)
    except (OSError, ValueError, KeyError, subprocess.SubprocessError) as error:
        if args.json:
            print(json.dumps({'error': str(error)}, ensure_ascii=False))
        else:
            print(f'Cannot create project: {error}', file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps(result, ensure_ascii=False))
    else:
        print(('Dry run: ' if args.dry_run else 'Created: ') + result['target'])
        print('Template content: ' + result['source']['content_sha256'])
        if not args.dry_run:
            print(f'Verified {result["skills"]} skills ({result["skill_mode"]}).')
            print(result['next_step'])
    return 0
