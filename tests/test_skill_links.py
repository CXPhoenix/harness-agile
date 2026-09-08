"""Skill copies are a supported transport with checked canonical content."""
import importlib.util
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from skill_links import sync

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('project_verify', ROOT / 'scripts/verify-project.py')
verifier = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verifier)


class SkillCopyTests(unittest.TestCase):
    def test_identical_skill_copies_pass_and_drift_fails(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / 'project'
            shutil.copytree(ROOT, root, symlinks=True, ignore=shutil.ignore_patterns('.git', '__pycache__', 'node_modules', 'dist'))
            links = root / '.claude/skills'
            shutil.rmtree(links)
            shutil.copytree(root / '.agents/skills', links)
            _, errors = verifier.verify(root)
            self.assertEqual(errors, [])
            (links / 'research/SKILL.md').write_text('changed')
            _, errors = verifier.verify(root)
            self.assertTrue(any('research' in e for e in errors), errors)

    def test_auto_falls_back_when_symlinks_are_unavailable(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            skill = root / '.agents/skills/example'
            skill.mkdir(parents=True)
            (skill / 'SKILL.md').write_text('canonical')
            with patch.object(Path, 'symlink_to', side_effect=OSError('not permitted')):
                self.assertEqual(sync(root), 'copy')
            self.assertEqual((root / '.claude/skills/example/SKILL.md').read_text(), 'canonical')

    def test_failed_explicit_symlink_conversion_preserves_existing_copy(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            skill = root / '.agents/skills/example'
            skill.mkdir(parents=True)
            (skill / 'SKILL.md').write_text('canonical')
            sync(root, 'copy')
            with patch.object(Path, 'symlink_to', side_effect=OSError('not permitted')):
                with self.assertRaises(OSError):
                    sync(root, 'symlink')
            self.assertEqual((root / '.claude/skills/example/SKILL.md').read_text(), 'canonical')

    def test_repairs_flattened_git_links_and_requires_review_for_drift(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            skill = root / '.agents/skills/example'
            skill.mkdir(parents=True)
            (skill / 'SKILL.md').write_text('canonical')
            entry = root / '.claude/skills/example'
            entry.parent.mkdir(parents=True)
            entry.write_text('../../.agents/skills/example')
            sync(root, 'copy')
            (entry / 'SKILL.md').write_text('local edit')
            with self.assertRaises(ValueError):
                sync(root)
            self.assertEqual((entry / 'SKILL.md').read_text(), 'local edit')
            sync(root, 'copy', refresh=True)
            self.assertEqual((entry / 'SKILL.md').read_text(), 'canonical')
