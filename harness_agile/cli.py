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
from .bundle import load, unpack
from . import migrate


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


def record_source(project, source, date):
    """Add the bundle's provenance to the state init-project.py wrote."""
    path = project / 'docs/agents/template-source.json'
    provenance = {k: v for k, v in source.items() if k != 'template_version'}
    if path.is_file():
        state = json.loads(path.read_text(encoding='utf-8'))
        state.update(source=provenance, generator_version=__version__)
    else:
        # Sources up to 0.4.0 write no state; keep their provenance-only record.
        state = {**source, 'generator_version': __version__, 'initialized_on': date}
    path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


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
        migrate.single_line(f'--{key.replace("_", "-")}', value)
    datetime.date.fromisoformat(args.date)
    if len(args.date) != 10:
        raise ValueError('--date must use YYYY-MM-DD')
    bundle = load(source if args.source else None)
    result = {'target': str(target), 'generator_version': __version__, 'source': bundle['source'], 'dry_run': args.dry_run}
    if args.dry_run:
        return result
    with tempfile.TemporaryDirectory(prefix='.harness-', dir=target.parent) as temp:
        staging = Path(temp) / 'project'
        staging.mkdir()
        unpack(bundle, staging)
        answers = {'name': args.name, 'one_liner': args.one_liner, 'date': args.date}
        command = migrate.init_command(staging, answers, bundle['source'].get('template_version') or __version__, False)
        if args.skill_mode:
            print('Warning: --skill-mode is deprecated and ignored; each runtime keeps its own skill copies.', file=sys.stderr)
        if args.keep_template_files:
            command.append('--keep-template-files')
        run(command, staging)
        run([sys.executable, '-B', 'scripts/verify-project.py'], staging)
        # skill_mode stays for JSON compatibility; runtimes now keep separate copies.
        result.update(skills=sum(p.is_dir() for p in (staging / '.claude/skills').iterdir()), codex_skills=sum(p.is_dir() for p in (staging / '.agents/skills').iterdir()), skill_mode='copy')
        result['next_step'] = 'Open this directory in Claude Code or Codex and use grill-with-docs to define the Project Charter.'
        record_source(staging, bundle['source'], args.date)
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
    init.add_argument('--skill-mode', choices=['auto', 'symlink', 'copy'], help='Deprecated and ignored; each runtime keeps its own skill copies')
    for flag in ('keep-template-files', 'no-input', 'json', 'dry-run', 'git'):
        init.add_argument('--' + flag, action='store_true')
    migrate.add_parser(commands)
    args = parser.parse_args(argv)
    try:
        result = create(args) if args.command == 'init' else migrate.migrate(args)
    except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as error:
        if args.json:
            print(json.dumps({'error': str(error)}, ensure_ascii=False))
        else:
            print(f"Cannot {'create' if args.command == 'init' else 'migrate'} project: {error}", file=sys.stderr)
        return 1
    if args.command == 'migrate':
        if args.json:
            print(json.dumps(result, ensure_ascii=False))
        else:
            migrate.print_report(result)
        return 1 if (result['verify'] or {}).get('status') == 'failed' else 0
    if args.json:
        print(json.dumps(result, ensure_ascii=False))
    else:
        print(('Dry run: ' if args.dry_run else 'Created: ') + result['target'])
        print('Template content: ' + result['source']['content_sha256'])
        if not args.dry_run:
            print(f'Verified skills: {result["skills"]} Claude, {result["codex_skills"]} Codex.')
            print(result['next_step'])
    return 0
