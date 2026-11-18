"""Claude and Codex skill trees are independent copies with checked shared invariants."""
import importlib.util
import json
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
        ignore = shutil.ignore_patterns('.git', '__pycache__', 'node_modules', 'dist', '.venv', '.DS_Store', '.codegraph', '.codegraph-*')
        shutil.copytree(ROOT, self.root, ignore=ignore)
        self.claude = self.root / '.claude/skills'
        self.codex = self.root / '.agents/skills'

    def errors(self):
        return verifier.verify(self.root)[1]

    def test_template_passes_and_runtime_content_may_diverge(self):
        self.assertEqual(self.errors(), [])
        (self.claude / 'research/SKILL.md').write_text('---\nname: research\ndescription: Claude-tuned.\n---\n')
        self.assertEqual(self.errors(), [])

    def test_unresolved_migration_sidecars_fail(self):
        state = {'schema': 2, 'files': {'docs/agents/workflow.md': 'sha256:0'}}
        (self.root / 'docs/agents/template-source.json').write_text(json.dumps(state))
        (self.root / 'docs/agents/workflow.md.harness-new').write_text('new rules\n')
        self.assertTrue(any('harness-new' in error and 'docs/agents/workflow.md' in error for error in self.errors()), self.errors())

    def test_drift_skill_is_required_in_both_runtime_trees(self):
        for tree in (self.claude, self.codex):
            with self.subTest(runtime=tree.parent.name):
                skill = tree / 'egm-drift-report'
                detached = self.root / 'detached-skill'
                skill.rename(detached)
                try:
                    self.assertTrue(any('egm-drift-report' in error and 'missing' in error
                                        for error in self.errors()), self.errors())
                finally:
                    detached.rename(skill)

    def test_drift_skill_stays_manual_when_both_policies_regress(self):
        entry = self.claude / 'egm-drift-report/SKILL.md'
        entry.write_text(entry.read_text().replace('disable-model-invocation: true',
                                                  'disable-model-invocation: false'))
        metadata = self.codex / 'egm-drift-report/agents/openai.yaml'
        metadata.write_text('policy:\n  allow_implicit_invocation: true\n')
        self.assertTrue(any('egm-drift-report must be explicitly invoked' in error
                            for error in self.errors()), self.errors())

    def test_handoff_directory_must_stay_ignored(self):
        ignore = self.root / '.gitignore'
        ignore.write_text(ignore.read_text().replace('/.proj.handoffs/\n', ''))
        self.assertIn('.gitignore must exclude /.proj.handoffs/', self.errors())

    def pin(self, name, lines):
        role = self.root / f'.codex/agents/{name}.toml'
        role.write_text(lines + role.read_text())

    def pin_claude(self, name, lines):
        role = self.root / f'.claude/agents/{name}.md'
        role.write_text(role.read_text().replace('model: inherit\n', lines, 1))

    def unregister_codex_codegraph(self):
        # Cut at the table header: a regex stopping at the next '[' would split `args = [...]`.
        config = self.root / '.codex/config.toml'
        text = config.read_text()
        config.write_text(text[:text.index('[mcp_servers.codegraph]')])

    def test_researcher_must_inherit_the_session_model(self):
        self.pin('harness-researcher', 'model = "gpt-5.5"\n')
        self.assertIn('Codex harness-researcher must inherit the session model', self.errors())

    def test_claude_researcher_must_inherit_model_and_effort(self):
        self.pin_claude('harness-researcher', 'model: opus\n')
        self.assertIn('Claude harness-researcher must inherit the session model', self.errors())
        self.pin_claude('harness-researcher', 'model: inherit\n')
        researcher = self.root / '.claude/agents/harness-researcher.md'
        researcher.write_text(researcher.read_text().replace('model: opus\n', 'model: inherit\neffort: high\n', 1))
        self.assertEqual(self.errors(), ['Claude harness-researcher must inherit the session effort'])

    def test_executor_and_verifier_may_pin_model_and_effort(self):
        for name in ('harness-executor', 'harness-reviewer', 'harness-challenger'):
            self.pin(name, 'model = "gpt-5.5"\nmodel_reasoning_effort = "high"\n')
        self.assertEqual(self.errors(), [])

    def test_claude_roles_may_pin_and_record_the_choice(self):
        for name in ('harness-executor', 'harness-reviewer', 'harness-challenger'):
            self.pin_claude(name, 'model: sonnet\neffort: high\n')
        record = self.root / 'docs/agents/template-source.json'
        choice = {'model': 'sonnet', 'effort': 'high'}
        state = {'schema': 2, 'files': {}, 'roles': {'claude': {'configured_on': '2026-11-19', 'executor': choice, 'verifier': choice}}}
        record.write_text(json.dumps(state, ensure_ascii=False, indent=2) + '\n')
        self.assertEqual(self.errors(), [])

    def test_codegraph_index_must_stay_ignored_while_registered(self):
        ignore = self.root / '.gitignore'
        ignore.write_text(ignore.read_text().replace('/.codegraph/\n', ''))
        message = '.gitignore must exclude /.codegraph/ while CodeGraph is registered'
        self.assertIn(message, self.errors())
        # Either runtime's registration alone requires the ignore line.
        (self.root / '.mcp.json').unlink()
        self.assertIn(message, self.errors())

    def test_claude_only_codegraph_registration_needs_the_ignore_line(self):
        self.unregister_codex_codegraph()
        ignore = self.root / '.gitignore'
        ignore.write_text(ignore.read_text().replace('/.codegraph/\n', ''))
        self.assertEqual(self.errors(), ['.gitignore must exclude /.codegraph/ while CodeGraph is registered'])

    def test_project_without_codegraph_passes(self):
        # The opt-out in docs/agents/codegraph.md, "Remove CodeGraph".
        (self.root / '.mcp.json').unlink()
        self.unregister_codex_codegraph()
        ignore = self.root / '.gitignore'
        ignore.write_text(ignore.read_text().replace('/.codegraph/\n', ''))
        self.assertEqual(self.errors(), [])

    def test_malformed_mcp_config_fails(self):
        (self.root / '.mcp.json').write_text('{"mcpServers": ')
        self.assertTrue(any(e.startswith('.mcp.json cannot be parsed') for e in self.errors()), self.errors())

    def test_misshapen_mcp_configs_fail_without_a_traceback(self):
        for body in ('[1]', '{"mcpServers": []}'):
            with self.subTest(body=body):
                (self.root / '.mcp.json').write_text(body)
                self.assertIn('.mcp.json must be a JSON object whose mcpServers is an object', self.errors())
        config = self.root / '.codex/config.toml'
        self.unregister_codex_codegraph()
        config.write_text('mcp_servers = 1\n' + config.read_text())
        self.assertIn('.codex/config.toml mcp_servers must be a table', self.errors())

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
