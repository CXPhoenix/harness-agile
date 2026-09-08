"""Exercise the public generator without installing or running a model."""
from pathlib import Path
import json
import os
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class BootstrapTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='harness-bootstrap-')
        self.addCleanup(self.temp.cleanup)
        self.target = Path(self.temp.name) / '專案 with spaces'

    def run_cli(self, *extra, values=True):
        args = [sys.executable, '-m', 'harness_agile', 'init', str(self.target), '--source', str(ROOT), '--no-input', '--json']
        if values:
            args += ['--name', '測試專案', '--one-liner', '保留 $() 與 `literal` 引數。']
        return subprocess.run([*args, *extra], cwd=ROOT, capture_output=True, text=True)

    def test_creates_verified_copy_mode_project(self):
        result = self.run_cli('--skill-mode', 'copy')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        output = json.loads(result.stdout)
        self.assertEqual(output['skills'], 30)
        self.assertEqual(output['skill_mode'], 'copy')
        self.assertFalse((self.target / '.git').exists())
        self.assertFalse((self.target / '.tmpl.docs').exists())
        self.assertIn('保留 $() 與 `literal` 引數。', (self.target / 'AGENTS.md').read_text())
        self.assertTrue((self.target / 'docs/agents/template-source.json').is_file())
        check = subprocess.run([sys.executable, 'scripts/verify-project.py'], cwd=self.target, capture_output=True, text=True)
        self.assertEqual(check.returncode, 0, check.stdout + check.stderr)

    def test_generated_readme_has_project_identity_and_no_deleted_initializer(self):
        result = self.run_cli()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        readme = (self.target / 'README.md').read_text()
        self.assertIn('# 測試專案', readme)
        self.assertNotIn('scripts/init-project.py', readme)
        self.assertNotIn('.tmpl.docs', readme)

    def test_dry_run_writes_nothing(self):
        result = self.run_cli('--dry-run')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue(json.loads(result.stdout)['dry_run'])
        self.assertEqual(list(self.target.parent.iterdir()), [])

    def test_python_entry_works_with_non_utf8_locale(self):
        target = Path(self.temp.name) / 'ascii-target'
        env = {**os.environ, 'LC_ALL': 'C', 'LANG': 'C', 'PYTHONUTF8': '0', 'PYTHONCOERCECLOCALE': '0'}
        result = subprocess.run([sys.executable, '-m', 'harness_agile', 'init', str(target), '--source', str(ROOT), '--name', 'Test', '--one-liner', 'Test', '--json', '--no-input'], cwd=ROOT, env=env, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(json.loads(result.stdout)['skills'], 30)

    def test_rejects_existing_content_without_modifying_it(self):
        self.target.mkdir()
        marker = self.target / 'keep.txt'
        marker.write_text('user content')
        result = self.run_cli()
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(marker.read_text(), 'user content')
        self.assertEqual(list(self.target.iterdir()), [marker])

    def test_missing_values_and_invalid_dates_leave_no_project(self):
        for extra, values in [((), False), (('--date', '2026-02-30'), True), (('--name', '{{PROJECT_NAME}}'), True)]:
            with self.subTest(extra=extra):
                result = self.run_cli(*extra, values=values)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn('error', json.loads(result.stdout))
                self.assertFalse(self.target.exists())

    def test_keep_retains_history_and_git_is_opt_in(self):
        result = self.run_cli('--keep-template-files', '--git')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(json.loads(result.stdout)['skills'], 31)
        self.assertTrue((self.target / '.tmpl.docs').is_dir())
        self.assertTrue((self.target / 'INSTALL.md').is_file())
        self.assertTrue((self.target / 'bootstrap/create-harness-project/SKILL.md').is_file())
        self.assertTrue((self.target / '.git').is_dir())
        remote = subprocess.check_output(['git', '-C', str(self.target), 'remote'], text=True)
        self.assertEqual(remote, '')
