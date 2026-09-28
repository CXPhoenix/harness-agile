"""Claude and Codex skill trees are independent copies with checked shared invariants."""
import importlib.util
from pathlib import Path
import shutil
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('project_verify', ROOT / 'scripts/verify-project.py')
verifier = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verifier)


class RuntimeSkillTreeTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name) / 'project'
        ignore = shutil.ignore_patterns('.git', '__pycache__', 'node_modules', 'dist', '.venv', '.DS_Store')
        shutil.copytree(ROOT, self.root, ignore=ignore)
        self.claude = self.root / '.claude/skills'
        self.codex = self.root / '.agents/skills'

    def errors(self):
        return verifier.verify(self.root)[1]

    def test_template_passes_and_runtime_content_may_diverge(self):
        self.assertEqual(self.errors(), [])
        (self.claude / 'research/SKILL.md').write_text('---\nname: research\ndescription: Claude-tuned.\n---\n')
        self.assertEqual(self.errors(), [])

    def test_handoff_directory_must_stay_ignored(self):
        ignore = self.root / '.gitignore'
        ignore.write_text(ignore.read_text().replace('/.proj.handoffs/\n', ''))
        self.assertIn('.gitignore must exclude /.proj.handoffs/', self.errors())

    def test_runtime_exclusive_skill_is_allowed_but_required_skills_are_not(self):
        shutil.copytree(self.claude / 'research', self.claude / 'claude-only')
        (self.claude / 'claude-only/SKILL.md').write_text('---\nname: claude-only\ndescription: Claude only.\n---\n')
        self.assertEqual(self.errors(), [])
        shutil.rmtree(self.codex / 'research')
        self.assertTrue(any('Required Codex skill is missing: research' in e for e in self.errors()))

    def test_links_and_foreign_metadata_fail(self):
        shutil.rmtree(self.claude / 'research')
        (self.claude / 'research').symlink_to('../../.agents/skills/research', target_is_directory=True)
        (self.claude / 'grilling/agents').mkdir()
        (self.claude / 'grilling/agents/openai.yaml').write_text('policy: {}\n')
        errors = self.errors()
        self.assertTrue(any('real directory: research' in e for e in errors), errors)
        self.assertTrue(any('Codex-only metadata: grilling' in e for e in errors), errors)

    def test_invocation_policy_must_match_for_shared_names(self):
        path = self.claude / 'grilling/SKILL.md'
        path.write_text(path.read_text().replace('\n---', '\ndisable-model-invocation: true\n---', 1))
        self.assertTrue(any('invocation policy differs: grilling' in e for e in self.errors()))


if __name__ == '__main__':
    unittest.main()
