"""Maintain project-local Claude entries from the canonical skill directories."""
from pathlib import Path
import shutil
import tempfile


def contents(directory):
    if not directory.is_dir() or directory.is_symlink():
        return None
    result = {}
    for path in directory.rglob('*'):
        if path.is_symlink():
            return None
        if path.is_file():
            result[path.relative_to(directory).as_posix()] = path.read_bytes()
    return result


def matches(entry, canonical):
    if entry.is_symlink():
        return not entry.readlink().is_absolute() and entry.resolve() == canonical.resolve()
    expected = contents(canonical)
    return expected is not None and contents(entry) == expected


def sync(root, mode='auto', refresh=False, dry_run=False):
    root = Path(root).resolve()
    canonical_root = root / '.agents/skills'
    entries = root / '.claude/skills'
    for path in (root / '.agents', canonical_root, root / '.claude', entries):
        if path.is_symlink():
            raise ValueError(f'Skill parent must be a real directory: {path}')
    skills = sorted(canonical_root.iterdir())
    if any(not p.is_dir() or contents(p) is None for p in skills):
        raise ValueError('Canonical skills must be real directories without symlinks')
    names = {p.name for p in skills}
    if entries.exists() and any(p.name not in names for p in entries.iterdir()):
        raise ValueError('Unmanaged Claude skill entries exist; review them before syncing')
    for skill in skills:
        entry = entries / skill.name
        expected_link = f'../../.agents/skills/{skill.name}'
        flattened = entry.is_file() and not entry.is_symlink() and entry.read_text(encoding='utf-8').strip() == expected_link
        if entry.exists() and not matches(entry, skill) and not flattened and not refresh:
            raise ValueError(f'Claude skill differs: {skill.name}; review and use --refresh to replace it')
        if entry.is_symlink() and entry.readlink().as_posix() != expected_link:
            raise ValueError(f'Unexpected Claude symlink: {skill.name}')
    if dry_run:
        return 'planned'
    entries.mkdir(parents=True, exist_ok=True)
    used = set()
    with tempfile.TemporaryDirectory(prefix='.skill-sync-', dir=entries.parent) as temp:
        temporary = Path(temp)
        replacements = []
        # Build every replacement before touching any existing entry.
        for skill in skills:
            entry = entries / skill.name
            if matches(entry, skill) and (mode == 'auto' or (mode == 'symlink') == entry.is_symlink()):
                used.add('symlink' if entry.is_symlink() else 'copy')
                continue
            staged = temporary / skill.name
            linked = False
            if mode != 'copy':
                try:
                    # Windows reparse points need native separators in their target.
                    staged.symlink_to(Path('../../.agents/skills') / skill.name, target_is_directory=True)
                    linked = True
                except OSError:
                    if mode == 'symlink':
                        raise
            if not linked:
                shutil.copytree(skill, staged)
            used.add('symlink' if linked else 'copy')
            replacements.append((entry, staged, temporary / (skill.name + '.backup')))
        installed = []
        try:
            for entry, staged, backup in replacements:
                had_entry = entry.exists() or entry.is_symlink()
                if had_entry:
                    entry.rename(backup)
                installed.append((entry, backup, had_entry))
                staged.rename(entry)
        except OSError:
            for entry, backup, had_entry in reversed(installed):
                if entry.is_symlink() or entry.is_file():
                    entry.unlink()
                elif entry.exists():
                    shutil.rmtree(entry)
                if had_entry:
                    backup.rename(entry)
            raise
    return '+'.join(sorted(used))
