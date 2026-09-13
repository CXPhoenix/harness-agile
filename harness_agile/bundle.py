"""Build a symlink-free template snapshot; runtime consumes only regular files."""
import base64
import hashlib
import json
from pathlib import Path, PurePosixPath
import subprocess

SOURCE_URL = 'https://github.com/CXPhoenix/harness-agile'
PATHS = (
    'AGENTS.md', 'CLAUDE.md', 'README.md', 'README.en.md', 'INSTALL.md', 'bootstrap', '.gitignore', '.gitattributes', 'skills-lock.json',
    '.agents/skills', '.claude/agents', '.codex/agents', '.codex/config.toml',
    'docs', '.tmpl.docs', 'scripts/init-project.py', 'scripts/verify-project.py',
    'scripts/skill_links.py', 'scripts/sync-skills.py', 'scripts/project-readme.md', 'tests/test_init_project.py',
)


def digest(files):
    return hashlib.sha256(json.dumps(files, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def snapshot(root):
    root = Path(root).resolve()
    if not (root / 'scripts/init-project.py').is_file():
        raise ValueError('Source must be an uninitialized harness-agile template')
    files = {}
    for rel in PATHS:
        selected = root / rel
        # npm's installer renames the explicitly packed .gitignore to .npmignore.
        if rel == '.gitignore' and not selected.exists():
            selected = root / '.npmignore'
        if not selected.exists():
            continue
        for path in ([selected] if selected.is_file() else sorted(selected.rglob('*'))):
            parts = path.relative_to(root).parts
            if any(p in {'.git', '__pycache__', '.DS_Store'} for p in parts) or path.suffix in {'.pyc', '.bak'}:
                continue
            if path.is_symlink() or not path.resolve().is_relative_to(root):
                raise ValueError(f'Template source contains an unsupported link: {path}')
            if path.is_file():
                name = rel if selected.is_file() else path.relative_to(root).as_posix()
                files[name] = base64.b64encode(path.read_bytes()).decode('ascii')
    commit = None
    dirty = None
    if (root / '.git').exists():
        commit = subprocess.check_output(['git', '-C', str(root), 'rev-parse', 'HEAD'], text=True).strip()
        dirty = bool(subprocess.check_output(['git', '-C', str(root), 'status', '--porcelain'], text=True).strip())
    return {'schema': 1, 'files': files, 'source': {'repository': SOURCE_URL, 'commit': commit, 'dirty': dirty, 'content_sha256': digest(files)}}


def unpack(bundle, target):
    if bundle.get('schema') != 1 or digest(bundle['files']) != bundle['source']['content_sha256']:
        raise ValueError('Template bundle schema or content checksum mismatch')
    decoded = {}
    for name, content in bundle['files'].items():
        path = PurePosixPath(name)
        reserved = {'CON', 'PRN', 'AUX', 'NUL', *(f'COM{i}' for i in range(1, 10)), *(f'LPT{i}' for i in range(1, 10))}
        if path.is_absolute() or not path.parts or any(p in {'.', '..', '.git'} or ':' in p or '\\' in p or p.endswith((' ', '.')) or p.split('.')[0].upper() in reserved for p in path.parts):
            raise ValueError(f'Unsafe template path: {name}')
        decoded[name] = base64.b64decode(content, validate=True)
    for name, content in decoded.items():
        path = target / name
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open('xb') as handle:
            handle.write(content)


def build(root):
    bundle = snapshot(root)
    output = Path(root) / 'harness_agile/data/template.json'
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(bundle, sort_keys=True) + '\n', encoding='utf-8')
    return output
