"""Move an adopted project to the template version this CLI carries, up or down."""
from collections import namedtuple
import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

from . import __version__
from .bundle import check_path, load, unpack

STATE_FILE = 'docs/agents/template-source.json'
SCHEMA = 2
SIDECAR = '.harness-new'
# Same ownership rules as scripts/init-project.py; used when a render predates them.
SEEDED = ('README.md', '.gitignore', '.gitattributes', STATE_FILE)
PROJECT_DIRS = ('.git', '.proj.specs', '.proj.tickets', '.proj.handoffs')
CHECKOUT_ONLY = (
    'harness_agile', 'bin', 'hatch_build.py', 'pyproject.toml', 'package.json', '.github',
    'tests/test_bootstrap.py', 'tests/test_bundle.py', 'tests/test_verify_project.py',
    'tests/test_migrate.py', 'scripts/verify-distributions.py',
)
NOISE_DIRS = {'__pycache__', 'node_modules', '.venv'}
CATEGORIES = ('updated', 'added', 'removed', 'conflict', 'orphaned', 'skipped_deleted', 'adopted')

Step = namedtuple('Step', 'id version ops')
# Structural changes file sync cannot express. Each op must have an inverse in UNDO.
STEPS = (
    Step('handoffs-gitignore', '0.3.0', (('ensure_line', '.gitignore', '/.proj.handoffs/'),)),
)


def run(command, cwd):
    try:
        result = subprocess.run(command, cwd=cwd, text=True, encoding='utf-8', capture_output=True, env={**os.environ, 'PYTHONUTF8': '1'})
    except FileNotFoundError:
        return 127, f'{command[0]} not found'
    return result.returncode, (result.stdout + result.stderr).strip()


def single_line(flag, value):
    if not value or not value.strip() or any(c in value for c in '\r\n\x00') or '{{' in value:
        raise ValueError(f'{flag} requires a nonempty single line without template tokens')
    return value


def iso_date(flag, value):
    if not re.fullmatch(r'\d{4}-\d{2}-\d{2}', value or ''):
        raise ValueError(f'{flag} must use YYYY-MM-DD')
    datetime.date.fromisoformat(value)
    return value


def version_key(version):
    """Sortable X.Y.Z; a pre-release sorts before its final. None when unparseable."""
    match = re.fullmatch(r'v?(\d+)\.(\d+)\.(\d+)([^+]*)(\+.*)?', version or '')
    return (*map(int, match.groups()[:3]), 0 if match[4] else 1) if match else None


def at_least_zero(version):
    return version_key(version) or (0, 0, 0, 0)


def file_hash(path):
    return 'sha256:' + hashlib.sha256(path.read_bytes()).hexdigest()


def managed(rel):
    parts = rel.split('/')
    if rel in SEEDED or parts[-1] == '.DS_Store' or rel.endswith(('.pyc', '.bak', SIDECAR)) or NOISE_DIRS & set(parts):
        return False
    return not any(rel == p or rel.startswith(p + '/') for p in PROJECT_DIRS + CHECKOUT_ONLY)


def manifest(root):
    files = {}
    for folder, dirs, names in os.walk(root):
        dirs[:] = sorted(d for d in dirs if d not in NOISE_DIRS and d != '.git')
        for name in names:
            path = Path(folder, name)
            rel = path.relative_to(root).as_posix()
            if managed(rel) and path.is_file() and not path.is_symlink():
                files[rel] = file_hash(path)
    return dict(sorted(files.items()))


def sidecars(root):
    for folder, dirs, names in os.walk(root):
        dirs[:] = [d for d in dirs if d not in NOISE_DIRS and d != '.git']
        yield from (Path(folder, n).relative_to(root).as_posix() for n in names + dirs if n.endswith(SIDECAR))


def local_hash(project, rel):
    """Hash of a regular file, None when absent, or 'blocked' for links, junctions and non-files on the path."""
    path = project
    for part in rel.split('/'):
        path = path / part
        if path.is_symlink():
            return 'blocked'
        if not path.exists():
            return None
        # Junctions are not symlinks to Python 3.11 but resolve elsewhere.
        if not path.resolve().is_relative_to(project) or (path != project / rel and not path.is_dir()):
            return 'blocked'
    return file_hash(path) if path.is_file() else 'blocked'


# Declarative step operations. Text is decoded and encoded as-is so line endings survive.

def read(path):
    return path.read_bytes().decode('utf-8') if path.is_file() else None


def ensure_line(project, path, line):
    target = project / path
    body = read(target)
    if body is not None and line in (entry.strip() for entry in body.splitlines()):
        return []
    newline = '\r\n' if body and '\r\n' in body else '\n'
    suffix = ('' if not body or body.endswith('\n') else newline) + line + newline
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(((body or '') + suffix).encode('utf-8'))
    return [{'op': 'remove_line', 'path': path, 'line': line, 'suffix': suffix, 'delete_if_empty': body is None}]


def remove_line(project, path, line, suffix='', delete_if_empty=False):
    target = project / path
    body = read(target)
    if body is None:
        return
    if suffix and body.endswith(suffix):
        body = body[:-len(suffix)]
    else:
        lines = body.splitlines(keepends=True)
        matches = [i for i, entry in enumerate(lines) if entry.strip() == line]
        if not matches:
            return
        del lines[matches[-1]]
        body = ''.join(lines)
    if delete_if_empty and not body:
        target.unlink()
    else:
        target.write_bytes(body.encode('utf-8'))


APPLY = {'ensure_line': ensure_line}
UNDO = {'remove_line': {'path': str, 'line': str, 'suffix': str, 'delete_if_empty': bool}}
UNDO_FUNCTIONS = {'remove_line': remove_line}


def pending_steps(steps, journal, old, new):
    done = {entry['id'] for entry in journal}
    return [s for s in steps if at_least_zero(old) < at_least_zero(s.version) <= at_least_zero(new) and s.id not in done]


def apply_steps(project, steps, journal):
    journal = list(journal)
    for step in steps:
        undo = []
        for op, *params in step.ops:
            undo += APPLY[op](project, *params)
        journal.append({'id': step.id, 'version': step.version, 'undo': undo})
    return journal


def check_journal(journal):
    if not isinstance(journal, list):
        raise ValueError('State migrations must be a list')
    for entry in journal:
        if not isinstance(entry, dict) or not isinstance(entry.get('id'), str) or not isinstance(entry.get('version'), str) or not isinstance(entry.get('undo'), list):
            raise ValueError(f'Malformed migration journal entry: {entry!r}')
        for op in entry['undo']:
            fields = UNDO.get(op.get('op')) if isinstance(op, dict) else None
            if fields is None:
                raise ValueError(f'Unknown migration operation in {entry["id"]}: {op!r}; use a newer harness-agile')
            if not {'path', 'line'} <= op.keys() or any(k != 'op' and not isinstance(v, fields.get(k, ())) for k, v in op.items()):
                raise ValueError(f'Malformed migration operation in {entry["id"]}: {op!r}')
            check_path(op['path'])


def undo_steps(project, journal, target):
    check_journal(journal)
    keep = [e for e in journal if at_least_zero(e['version']) <= at_least_zero(target)]
    for entry in reversed([e for e in journal if at_least_zero(e['version']) > at_least_zero(target)]):
        for op in reversed(entry['undo']):
            UNDO_FUNCTIONS[op['op']](project, **{k: v for k, v in op.items() if k != 'op'})
    return keep


def init_command(root, answers, version, keep):
    """Run a template's own initializer; those up to 0.4.0 predate --template-version."""
    command = [sys.executable, '-B', 'scripts/init-project.py', '--name', answers['name'], '--one-liner', answers['one_liner'], '--date', answers['date']]
    if '--template-version' in run([sys.executable, '-B', 'scripts/init-project.py', '--help'], root)[1]:
        command += ['--template-version', version]
    if keep:
        command.append('--keep-template-files')
    return command


def render(bundle, answers, keep, workdir):
    """The target tree exactly as init would produce it for these answers."""
    root = Path(workdir) / 'render'
    root.mkdir(parents=True)
    unpack(bundle, root)
    code, output = run(init_command(root, answers, bundle['source'].get('template_version') or 'unknown', keep), root)
    if code:
        raise ValueError(f'Cannot render the template: {output}')
    state = root / STATE_FILE
    recorded = json.loads(state.read_text(encoding='utf-8')) if state.is_file() else {}
    files = recorded['files'] if recorded.get('schema') == SCHEMA else manifest(root)
    for rel in files:
        check_path(rel)
    return root, files


def plan_files(project, old, new):
    """Classify each path: what the template recorded (old), what is on disk, what the target renders (new)."""
    actions, files, blocked = {c: [] for c in CATEGORIES}, {}, []
    for rel in sorted(old.keys() | new.keys()):
        m, n, local = old.get(rel), new.get(rel), local_hash(project, rel)
        if local == 'blocked':
            blocked.append(rel)
            continue
        if n:
            files[rel] = n
        if m and local is None:
            if n:
                actions['skipped_deleted'].append(rel)
        elif m and local == m:
            if not n:
                actions['removed'].append(rel)
            elif n != local:
                actions['updated'].append(rel)
        elif m:
            if not n:
                actions['orphaned'].append(rel)
            elif n not in (local, m):
                actions['conflict'].append(rel)
        elif local is None:
            actions['added'].append(rel)
        elif local == n:
            actions['adopted'].append(rel)
        else:
            actions['conflict'].append(rel)
    # On a case-insensitive file system a case-only rename names the same file twice.
    renamed = {rel.casefold() for rel in files}
    actions['removed'] = [rel for rel in actions['removed'] if rel.casefold() not in renamed]
    if blocked:
        raise ValueError('Paths blocked by a link, junction or non-file: ' + ', '.join(blocked[:10]))
    return actions, files


def write_files(project, rendered, actions):
    for rel in actions['updated'] + actions['added']:
        target = project / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(rendered / rel, target)
    for rel in actions['conflict']:
        (project / (rel + SIDECAR)).write_bytes((rendered / rel).read_bytes())
    for rel in actions['removed']:
        (project / rel).unlink()
        parent = (project / rel).parent
        while parent != project and not any(parent.iterdir()):
            parent.rmdir()
            parent = parent.parent


def check_git(project, allow_no_git):
    code, output = run(['git', '-C', str(project), 'rev-parse', '--show-toplevel'], project)
    if 'dubious ownership' in output:
        raise ValueError(f'Git refuses this directory (dubious ownership): {output.splitlines()[0]}')
    if code:
        if allow_no_git:
            return 'Not a Git worktree; restore from your own backup if needed.'
        raise ValueError('Project must be a Git worktree so the change can be reviewed and reverted; pass --allow-no-git to skip')
    code, status = run(['git', '-C', str(project), 'status', '--porcelain', '--untracked-files=all', '--', '.'], project)
    if code or status:
        raise ValueError('Commit or stash uncommitted changes first: ' + ', '.join(status.splitlines()[:5]))
    return None


def check_state(state):
    files, answers = state.get('files'), state.get('answers')
    if not isinstance(files, dict) or not all(isinstance(k, str) and isinstance(v, str) for k, v in files.items()):
        raise ValueError(f'{STATE_FILE} files must map paths to hashes')
    if not isinstance(answers, dict) or not all(isinstance(answers.get(k), str) for k in ('name', 'one_liner', 'date')):
        raise ValueError(f'{STATE_FILE} answers are malformed')
    if not isinstance(state.get('options'), dict) or not isinstance(state.get('history'), list) or not isinstance(state.get('template_version'), str):
        raise ValueError(f'{STATE_FILE} options, history or template_version are malformed')
    for rel in files:
        check_path(rel)
    check_journal(state.get('migrations'))


def load_state(project, args):
    path = project / STATE_FILE
    state = json.loads(path.read_text(encoding='utf-8')) if path.is_file() else None
    if state is not None and not isinstance(state, dict):
        raise ValueError(f'{STATE_FILE} is not a JSON object')
    schema = (state or {}).get('schema')
    if isinstance(schema, int) and schema > SCHEMA:
        raise ValueError(f'{STATE_FILE} uses schema {schema}, newer than this harness-agile supports')
    if args.adopt:
        if schema == SCHEMA:
            raise ValueError('Project is already tracked; run without --adopt')
        legacy = state or {}
        answers = {}
        for key in ('name', 'one_liner'):
            value = getattr(args, key)
            if not value and not args.json and sys.stdin.isatty():
                value = input(f'Project {key.replace("_", " ")}: ').strip()
            answers[key] = single_line(f'--{key.replace("_", "-")}', value)
        legacy_date = legacy.get('initialized_on')
        answers['date'] = iso_date('--date', args.date or (legacy_date if isinstance(legacy_date, str) else None) or datetime.date.today().isoformat())
        return {'schema': SCHEMA, 'template_version': 'unknown', 'initialized_on': answers['date'], 'answers': answers,
                'options': {'keep_template_files': (project / '.tmpl.docs').is_dir()}, 'files': {}, 'migrations': [], 'history': []}
    if schema != SCHEMA:
        raise ValueError(f'{STATE_FILE} is missing or predates migrate; run once with --adopt')
    check_state(state)
    return state


def migrate(args):
    project = Path(args.directory).expanduser().resolve()
    if not project.is_dir():
        raise ValueError(f'Project directory does not exist: {project}')
    if not args.adopt and (args.baseline_source or args.name or args.one_liner or args.date):
        raise ValueError('--name, --one-liner, --date and --baseline-source only apply with --adopt')
    pending = sorted(sidecars(project))
    if pending:
        raise ValueError('Resolve and delete earlier *.harness-new files first: ' + ', '.join(pending[:10]))
    warning = check_git(project, args.allow_no_git)
    state = load_state(project, args)
    bundle = load(Path(args.source).expanduser().resolve() if args.source else None)
    old_version, new_version = state['template_version'], bundle['source'].get('template_version') or 'unknown'
    if version_key(new_version) is None:
        raise ValueError(f'Cannot tell the target template version ({new_version!r}); the source needs pyproject.toml')
    keep = state['options'].get('keep_template_files', False)
    with tempfile.TemporaryDirectory(prefix='harness-migrate-') as temp:
        # Paths outside template ownership never take part, even if a state lists them.
        old_files = {rel: h for rel, h in state['files'].items() if managed(rel)}
        if args.baseline_source:
            baseline = load(Path(args.baseline_source).expanduser().resolve())
            _, old_files = render(baseline, state['answers'], keep, Path(temp, 'baseline'))
            old_version = baseline['source'].get('template_version') or 'unknown'
        rendered, new_files = render(bundle, state['answers'], keep, temp)
        actions, files = plan_files(project, old_files, new_files)
        journal = state['migrations']
        downgrade = at_least_zero(new_version) < at_least_zero(old_version)
        steps = [] if downgrade else pending_steps(STEPS, journal, old_version, new_version)
        undo = [e for e in reversed(journal) if at_least_zero(e['version']) > at_least_zero(new_version)] if downgrade else []
        step_paths = {op[1] for s in steps for op in s.ops} | {op['path'] for e in undo for op in e['undo']}
        blocked = [rel for rel in sorted(step_paths) if local_hash(project, rel) == 'blocked']
        if blocked:
            raise ValueError('Paths blocked by a link, junction or non-file: ' + ', '.join(blocked))
        changes = any(actions.values()) or steps or undo or files != state['files']
        report = {
            'project': str(project), 'from': old_version, 'to': new_version,
            'direction': 'downgrade' if downgrade else 'upgrade' if at_least_zero(new_version) > at_least_zero(old_version) else 'same',
            'dry_run': not args.apply, 'up_to_date': not changes and old_version == new_version,
            'files': actions, 'steps': {'apply': [s.id for s in steps], 'undo': [e['id'] for e in undo]}, 'verify': None,
        }
        if warning:
            report['warning'] = warning
        if not args.apply or report['up_to_date']:
            return report
        write_files(project, rendered, actions)
    journal = undo_steps(project, journal, new_version) if downgrade else apply_steps(project, steps, journal)
    history = state['history'] + [{'from': old_version, 'to': new_version, 'on': datetime.date.today().isoformat(), 'generator_version': __version__}]
    source = {k: v for k, v in bundle['source'].items() if k != 'template_version'}
    state.update(schema=SCHEMA, template_version=new_version, source=source, generator_version=__version__,
                 files=files, migrations=journal, history=history)
    target = project / STATE_FILE
    target.parent.mkdir(parents=True, exist_ok=True)
    staged = target.with_name(target.name + '.tmp')
    staged.write_text(json.dumps(state, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    os.replace(staged, target)
    verifier = project / 'scripts/verify-project.py'
    if actions['conflict']:
        report['verify'] = {'status': 'skipped', 'output': 'Merge each *.harness-new into its file, delete it, then run scripts/verify-project.py.'}
    elif verifier.is_file():
        code, output = run([sys.executable, '-B', str(verifier)], project)
        report['verify'] = {'status': 'failed' if code else 'passed', 'output': output[-2000:]}
    return report


def add_parser(commands):
    parser = commands.add_parser('migrate', help="Move a project to this CLI's template version (dry run unless --apply)")
    parser.add_argument('directory')
    parser.add_argument('--source', help='Explicit local uninitialized template source; otherwise use the bundled version')
    parser.add_argument('--adopt', action='store_true', help='Start tracking a project created before migrate existed')
    parser.add_argument('--baseline-source', help='With --adopt: local uninitialized template the project was created from')
    parser.add_argument('--name', help='With --adopt: the project name given at creation')
    parser.add_argument('--one-liner', help='With --adopt: the one-liner given at creation')
    parser.add_argument('--date', help='With --adopt: the creation date (YYYY-MM-DD)')
    for flag in ('apply', 'json', 'allow-no-git'):
        parser.add_argument('--' + flag, action='store_true')
    return parser


def print_report(report):
    print(f"{'Plan' if report['dry_run'] else 'Migrated'}: {report['project']} {report['from']} -> {report['to']}")
    if report.get('warning'):
        print('Warning: ' + report['warning'])
    if report['up_to_date']:
        print('Already up to date.')
        return
    for category, paths in report['files'].items():
        for rel in paths:
            print(f'  {category:<15} {rel}')
    for key in ('apply', 'undo'):
        for step in report['steps'][key]:
            print(f'  step {key:<10} {step}')
    if report['dry_run']:
        print('Nothing written. Re-run with --apply.')
    elif report['verify']:
        print(f"Verify {report['verify']['status']}: {report['verify']['output']}")
