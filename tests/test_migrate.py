"""Move generated projects between template versions built from disposable source copies."""
from pathlib import Path
import hashlib
import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import unittest

from harness_agile import migrate
from harness_agile.bundle import snapshot, unpack

ROOT = Path(__file__).resolve().parents[1]
STATE = 'docs/agents/template-source.json'
CHANGED = 'docs/agents/workflow.md'
ADDED = 'docs/agents/new-doc.md'
DROPPED = ('.claude/skills/prototype', '.agents/skills/prototype')


def legacy(root):
    """Turn a source copy's initializer into one that predates migrate (0.4.0 and earlier)."""
    script = root / 'scripts/init-project.py'
    body = script.read_text(encoding='utf-8')
    for old, new in (
        ('    ap.add_argument("--template-version"', '    if False: ap.add_argument("--template-version"'),
        ('args.template_version or checkout_version(root)', 'checkout_version(root)'),
        ('    (root / STATE_FILE).write_text(', '    if False: (root / STATE_FILE).write_text('),
    ):
        assert old in body, old
        body = body.replace(old, new)
    script.write_text(body, encoding='utf-8')


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class MigrateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bundle = snapshot(ROOT)

    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix='harness-migrate-')
        self.addCleanup(temp.cleanup)
        self.temp = Path(temp.name)
        self.old = self.source('0.4.0')
        self.new = self.source('0.5.0', self.next_version)
        self.project = self.temp / '專案 project'
        self.create(self.old)

    def source(self, version, mutate=None):
        root = self.temp / ('source-' + version)
        root.mkdir()
        unpack(self.bundle, root)
        (root / 'pyproject.toml').write_text(f'[project]\nname = "harness-agile"\nversion = "{version}"\n', encoding='utf-8')
        if mutate:
            mutate(root)
        return root

    @staticmethod
    def next_version(root):
        with (root / CHANGED).open('a', encoding='utf-8') as handle:
            handle.write('\nNew guidance.\n')
        (root / ADDED).write_text('new\n', encoding='utf-8')
        for rel in DROPPED:
            shutil.rmtree(root / rel)

    def create(self, source, project=None):
        result = subprocess.run([sys.executable, '-m', 'harness_agile', 'init', str(project or self.project), '--source', str(source),
                                 '--name', '遷移專案', '--one-liner', '保留 $() 與 `literal`。', '--date', '2026-11-02',
                                 '--no-input', '--json'], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def migrate(self, source, *extra, git=False):
        args = [sys.executable, '-m', 'harness_agile', 'migrate', str(self.project), '--source', str(source), '--json', *extra]
        if not git:
            args.append('--allow-no-git')
        result = subprocess.run(args, cwd=ROOT, capture_output=True, text=True)
        return result, json.loads(result.stdout.strip().splitlines()[-1]) if result.stdout.strip() else {}

    def applied(self, source, *extra):
        result, report = self.migrate(source, '--apply', *extra)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return report

    def hashes(self):
        return {p.relative_to(self.project).as_posix(): digest(p) for p in self.project.rglob('*')
                if p.is_file() and '.git' not in p.relative_to(self.project).parts}

    def state(self):
        return json.loads((self.project / STATE).read_text(encoding='utf-8'))

    def write_state(self, state):
        (self.project / STATE).write_text(json.dumps(state, ensure_ascii=False), encoding='utf-8')

    def assert_refused(self, *extra, text, git=False):
        before = self.hashes()
        result, report = self.migrate(self.new, '--apply', *extra, git=git)
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn(text, report.get('error', ''))
        self.assertEqual(self.hashes(), before)

    # T3
    def test_upgrade_updates_adds_and_removes_unmodified_files(self):
        report = self.applied(self.new)
        self.assertEqual((report['from'], report['to'], report['direction']), ('0.4.0', '0.5.0', 'upgrade'))
        self.assertEqual((self.project / CHANGED).read_bytes(), (self.new / CHANGED).read_bytes())
        self.assertEqual((self.project / ADDED).read_text(encoding='utf-8'), 'new\n')
        for rel in DROPPED:
            self.assertFalse((self.project / rel).exists(), rel)
        self.assertIn(CHANGED, report['files']['updated'])
        self.assertEqual(report['files']['added'], [ADDED])
        self.assertIn('.claude/skills/prototype/SKILL.md', report['files']['removed'])
        self.assertEqual(report['verify']['status'], 'passed')
        state = self.state()
        self.assertEqual(state['template_version'], '0.5.0')
        self.assertEqual(state['history'][-1]['from'], '0.4.0')
        self.assertEqual(state['answers']['name'], '遷移專案')
        self.assertNotIn('.claude/skills/prototype/SKILL.md', state['files'])
        self.assertEqual(state['files'][ADDED], 'sha256:' + digest(self.project / ADDED))

    # T4
    def test_local_edits_survive_and_new_content_goes_to_sidecars(self):
        (self.project / CHANGED).write_text('local rules\n', encoding='utf-8')
        (self.project / ADDED).write_text('mine\n', encoding='utf-8')
        report = self.applied(self.new)
        self.assertEqual(sorted(report['files']['conflict']), sorted([CHANGED, ADDED]))
        self.assertEqual((self.project / CHANGED).read_text(encoding='utf-8'), 'local rules\n')
        self.assertEqual((self.project / ADDED).read_text(encoding='utf-8'), 'mine\n')
        self.assertEqual((self.project / (CHANGED + '.harness-new')).read_bytes(), (self.new / CHANGED).read_bytes())
        self.assertEqual((self.project / (ADDED + '.harness-new')).read_text(encoding='utf-8'), 'new\n')
        self.assertEqual(report['verify']['status'], 'skipped')
        self.assertEqual(self.state()['files'][CHANGED], 'sha256:' + digest(self.new / CHANGED))

    # T5
    def test_orphaned_edits_stay_and_local_deletions_are_respected(self):
        skill = self.project / '.claude/skills/prototype/SKILL.md'
        tuned = '---\nname: prototype\ndescription: Tuned locally.\n---\n'
        skill.write_text(tuned, encoding='utf-8')
        (self.project / 'docs/guide.md').unlink()
        report = self.applied(self.new)
        self.assertEqual(skill.read_text(encoding='utf-8'), tuned)
        self.assertEqual(report['files']['orphaned'], ['.claude/skills/prototype/SKILL.md'])
        self.assertNotIn('.claude/skills/prototype/SKILL.md', self.state()['files'])
        self.assertFalse((self.project / 'docs/guide.md').exists())
        self.assertEqual(report['files']['skipped_deleted'], ['docs/guide.md'])
        self.assertIn('docs/guide.md', self.state()['files'])

    # T6
    def test_converged_and_matching_files_need_no_writes(self):
        _, report = self.migrate(self.old)
        self.assertTrue(report['up_to_date'])
        (self.project / CHANGED).write_bytes((self.new / CHANGED).read_bytes())
        shutil.copyfile(self.new / ADDED, self.project / ADDED)
        report = self.applied(self.new)
        self.assertNotIn(CHANGED, report['files']['updated'] + report['files']['conflict'])
        self.assertEqual(report['files']['adopted'], [ADDED])
        self.assertFalse(list(self.project.rglob('*.harness-new')))

    # T7
    def test_preflight_failures_write_nothing(self):
        self.assert_refused(text='Git', git=True)
        subprocess.run(['git', 'init', '-q', str(self.project)], check=True)
        self.assert_refused(text='uncommitted', git=True)
        (self.project / '.git/info/exclude').write_text('*\n', encoding='utf-8')
        sidecar = self.project / 'docs/x.md.harness-new'
        sidecar.write_text('old\n', encoding='utf-8')
        self.assert_refused(text='.harness-new', git=True)
        sidecar.unlink()
        state = self.state()
        self.write_state({**state, 'schema': 99})
        self.assert_refused(text='newer')
        self.write_state({**state, 'files': {**state['files'], '../outside': 'sha256:0'}})
        self.assert_refused(text='Unsafe')
        self.write_state({k: v for k, v in state.items() if k != 'schema'})
        self.assert_refused(text='--adopt')
        (self.project / STATE).unlink()
        self.assert_refused(text='--adopt')
        self.write_state(state)
        target = self.project / CHANGED
        target.unlink()
        try:
            target.symlink_to(self.project / 'docs/guide.md')
        except OSError:
            self.skipTest('symlinks unavailable')
        self.assert_refused(text='blocked')

    def test_clean_git_worktree_is_accepted(self):
        subprocess.run(['git', 'init', '-q', str(self.project)], check=True)
        (self.project / '.git/info/exclude').write_text('*\n', encoding='utf-8')
        result, report = self.migrate(self.new, '--apply', git=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(report['direction'], 'upgrade')

    # T8
    def test_dry_run_plan_matches_the_applied_result(self):
        (self.project / CHANGED).write_text('local rules\n', encoding='utf-8')
        before = self.hashes()
        result, preview = self.migrate(self.new)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue(preview['dry_run'])
        self.assertEqual(self.hashes(), before)
        applied = self.applied(self.new)
        self.assertEqual((preview['files'], preview['steps']), (applied['files'], applied['steps']))

    # T10
    def test_upgrade_then_downgrade_restores_every_byte(self):
        before = self.hashes()
        state = self.state()
        self.applied(self.new)
        report = self.applied(self.old)
        self.assertEqual(report['direction'], 'downgrade')
        after = self.hashes()
        before.pop(STATE)
        after.pop(STATE)
        self.assertEqual(after, before)
        restored = self.state()
        for key in ('files', 'migrations', 'template_version', 'answers', 'options'):
            self.assertEqual(restored[key], state[key], key)

    # T9 end to end: the real registry restores what an adoption added.
    def test_adopted_gitignore_step_is_undone_on_downgrade(self):
        ignore = self.project / '.gitignore'
        original = ignore.read_bytes()
        ignore.write_bytes(original.replace(b'/.proj.handoffs/\n', b''))
        stripped = ignore.read_bytes()
        (self.project / STATE).unlink()
        report = self.applied(self.old, '--adopt', '--name', '遷移專案', '--one-liner', '保留 $() 與 `literal`。')
        self.assertIn('handoffs-gitignore', report['steps']['apply'])
        self.assertIn(b'/.proj.handoffs/\n', ignore.read_bytes())
        result, report = self.migrate(self.source('0.2.1'), '--apply')
        self.assertEqual(report['steps']['undo'], ['handoffs-gitignore'])
        self.assertEqual(ignore.read_bytes(), stripped)
        self.assertEqual(report['verify']['status'], 'failed')
        self.assertEqual(result.returncode, 1)

    # T11
    def test_adopt_without_baseline_never_overwrites(self):
        (self.project / CHANGED).write_text('local rules\n', encoding='utf-8')
        # ADR dates come from this answer, so a legacy record must supply the original date.
        legacy = {'repository': 'x', 'initialized_on': '2026-11-02'}
        self.write_state(legacy)
        report = self.applied(self.new, '--adopt', '--name', '遷移專案', '--one-liner', '保留 $() 與 `literal`。')
        self.assertEqual(report['files']['conflict'], [CHANGED])
        self.assertEqual(report['files']['added'], [ADDED])
        self.assertTrue((self.project / DROPPED[0]).exists())
        state = self.state()
        self.assertEqual((state['schema'], state['answers']['date']), (2, '2026-11-02'))

    def test_adopt_with_baseline_updates_unmodified_files(self):
        (self.project / CHANGED).write_text('local rules\n', encoding='utf-8')
        (self.project / STATE).unlink()
        report = self.applied(self.new, '--adopt', '--baseline-source', str(self.old), '--date', '2026-11-02',
                              '--name', '遷移專案', '--one-liner', '保留 $() 與 `literal`。')
        self.assertEqual(report['files']['conflict'], [CHANGED])
        self.assertIn('.claude/skills/prototype/SKILL.md', report['files']['removed'])
        self.assertFalse((self.project / DROPPED[0]).exists())

    def test_adopt_refuses_tracked_projects_and_missing_answers(self):
        self.assert_refused('--adopt', '--name', 'x', '--one-liner', 'y', text='already')
        (self.project / STATE).unlink()
        self.assert_refused('--adopt', text='--name')

    # F14
    def test_same_version_rerun_keeps_local_edits_without_sidecars(self):
        with (self.project / 'AGENTS.md').open('a', encoding='utf-8') as handle:
            handle.write('\nOur charter.\n')
        result, report = self.migrate(self.old)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue(report['up_to_date'], report)
        report = self.applied(self.new)
        self.assertNotIn('AGENTS.md', report['files']['conflict'])
        self.assertFalse(list(self.project.rglob('*.harness-new')))

    # F15
    def test_case_only_rename_keeps_the_file(self):
        renamed = 'docs/agents/Workflow.md'
        def rename(root):
            (root / CHANGED).rename(root / 'docs/agents/tmp.md')
            (root / 'docs/agents/tmp.md').rename(root / renamed)
        target = self.source('0.6.0', rename)
        self.applied(target)
        self.assertEqual((self.project / renamed).read_bytes(), (target / renamed).read_bytes())

    # P13
    def test_initializers_that_predate_migrate_still_render(self):
        old = self.source('0.3.0', legacy)
        other = self.temp / 'legacy project'
        self.create(old, other)
        self.assertNotIn('schema', json.loads((other / STATE).read_text(encoding='utf-8')))
        (self.project / CHANGED).write_text('local rules\n', encoding='utf-8')
        (self.project / STATE).unlink()
        report = self.applied(self.new, '--adopt', '--baseline-source', str(old), '--date', '2026-11-02',
                              '--name', '遷移專案', '--one-liner', '保留 $() 與 `literal`。')
        self.assertEqual(report['files']['conflict'], [CHANGED])
        (self.project / CHANGED).write_bytes((self.project / (CHANGED + '.harness-new')).read_bytes())
        (self.project / (CHANGED + '.harness-new')).unlink()
        report = self.applied(old)
        self.assertEqual(report['direction'], 'downgrade')
        self.assertEqual((self.project / CHANGED).read_bytes(), (old / CHANGED).read_bytes())

    def test_more_preflight_failures_write_nothing(self):
        unknown = self.source('0.9.9')
        (unknown / 'pyproject.toml').unlink()
        result, report = self.migrate(unknown, '--apply')
        self.assertIn('version', report.get('error', ''))
        self.assert_refused('--name', 'x', text='--adopt')
        sidecar_dir = self.project / 'docs/x.md.harness-new'
        sidecar_dir.mkdir()
        self.assert_refused(text='.harness-new')
        sidecar_dir.rmdir()
        state = self.state()
        self.write_state({**state, 'files': list(state['files'])})
        self.assert_refused(text='files')
        self.write_state({**state, 'files': {**state['files'], '.GIT/config': 'sha256:0'}})
        self.assert_refused(text='Unsafe')
        self.write_state({**state, 'files': {**state['files'], 'README.md': 'sha256:' + digest(self.project / 'README.md')}})
        self.applied(self.new)
        self.assertTrue((self.project / 'README.md').is_file())

    def test_step_paths_behind_links_are_blocked(self):
        ignore = self.project / '.gitignore'
        outside = self.temp / 'outside-ignore'
        outside.write_bytes(ignore.read_bytes().replace(b'/.proj.handoffs/\n', b''))
        ignore.unlink()
        try:
            ignore.symlink_to(outside)
        except OSError:
            self.skipTest('symlinks unavailable')
        (self.project / STATE).unlink()
        before = outside.read_bytes()
        self.assert_refused('--adopt', '--name', 'x', '--one-liner', 'y', '--date', '2026-11-02', text='blocked')
        self.assertEqual(outside.read_bytes(), before)

    def test_ownership_rules_match_the_initializer(self):
        spec = importlib.util.spec_from_file_location('init_project', ROOT / 'scripts/init-project.py')
        initializer = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(initializer)
        for name in ('SEEDED', 'PROJECT_DIRS', 'CHECKOUT_ONLY', 'NOISE_DIRS'):
            self.assertEqual(getattr(initializer, name), getattr(migrate, name), name)

    def test_render_fallback_matches_initializer_manifest(self):
        self.assertEqual(migrate.manifest(self.project), self.state()['files'])


class VersionTests(unittest.TestCase):
    def test_prereleases_sort_before_finals_and_tags_parse(self):
        self.assertLess(migrate.version_key('0.5.0rc1'), migrate.version_key('0.5.0'))
        self.assertEqual(migrate.version_key('v0.5.0'), migrate.version_key('0.5.0'))
        self.assertIsNone(migrate.version_key('unknown'))


class StepTests(unittest.TestCase):
    """T9: declarative steps record only what they changed, so undo never removes user lines."""

    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.steps = (migrate.Step('extra-ignore', '0.5.0', (('ensure_line', '.gitignore', '/extra/'),)),
                      migrate.Step('more-ignore', '0.6.0', (('ensure_line', 'other.txt', 'x'),)))

    def run_steps(self, journal, old, new):
        return migrate.apply_steps(self.root, migrate.pending_steps(self.steps, journal, old, new), journal)

    def test_existing_line_records_no_undo(self):
        (self.root / '.gitignore').write_bytes(b'/extra/\n')
        journal = self.run_steps([], '0.4.0', '0.5.0')
        self.assertEqual(journal, [{'id': 'extra-ignore', 'version': '0.5.0', 'undo': []}])
        migrate.undo_steps(self.root, journal, '0.4.0')
        self.assertEqual((self.root / '.gitignore').read_bytes(), b'/extra/\n')

    def test_undo_restores_bytes_and_created_files_in_reverse(self):
        (self.root / '.gitignore').write_bytes(b'a\r\nb')
        journal = self.run_steps([], '0.4.0', '0.6.0')
        self.assertEqual((self.root / '.gitignore').read_bytes(), b'a\r\nb\r\n/extra/\r\n')
        self.assertEqual((self.root / 'other.txt').read_bytes(), b'x\n')
        self.assertEqual(self.run_steps(journal, '0.4.0', '0.6.0'), journal)
        kept = migrate.undo_steps(self.root, journal, '0.5.0')
        self.assertEqual([entry['id'] for entry in kept], ['extra-ignore'])
        self.assertFalse((self.root / 'other.txt').exists())
        self.assertEqual(migrate.undo_steps(self.root, kept, '0.4.0'), [])
        self.assertEqual((self.root / '.gitignore').read_bytes(), b'a\r\nb')

    def test_appended_line_follows_crlf_files(self):
        (self.root / '.gitignore').write_bytes(b'a\r\n')
        journal = self.run_steps([], '0.4.0', '0.5.0')
        self.assertEqual((self.root / '.gitignore').read_bytes(), b'a\r\n/extra/\r\n')
        migrate.undo_steps(self.root, journal, '0.4.0')
        self.assertEqual((self.root / '.gitignore').read_bytes(), b'a\r\n')

    def test_unknown_operations_are_rejected_before_any_change(self):
        (self.root / '.gitignore').write_bytes(b'/extra/\n')
        journal = [{'id': 'a', 'version': '0.5.0', 'undo': [{'op': 'remove_line', 'path': '.gitignore', 'line': '/extra/'}]},
                   {'id': 'b', 'version': '0.6.0', 'undo': [{'op': 'rewrite', 'path': '.gitignore'}]}]
        with self.assertRaisesRegex(ValueError, 'rewrite'):
            migrate.undo_steps(self.root, journal, '0.4.0')
        self.assertEqual((self.root / '.gitignore').read_bytes(), b'/extra/\n')


if __name__ == '__main__':
    unittest.main()
