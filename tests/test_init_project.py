"""Exercise the initializer through its public CLI in disposable project copies."""

from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
import hashlib


SOURCE = Path(__file__).resolve().parents[1]


class InitializeProjectTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="harness-init-test-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "scripts").mkdir()
        shutil.copy2(SOURCE / "scripts/init-project.py", self.root / "scripts/init-project.py")
        (self.root / "AGENTS.md").write_text(
            "# Instructions\n\n<!-- TEMPLATE: {{PROJECT_NAME}} -->\n"
            "\n## Project Charter\n**{{PROJECT_NAME}}** — {{PROJECT_ONE_LINER}}\n"
            "<!-- PLACEHOLDER -->\n", encoding="utf-8"
        )
        (self.root / "CLAUDE.md").write_text("@AGENTS.md\n", encoding="utf-8")
        (self.root / "TEMPLATE.md").write_text("Template instructions", encoding="utf-8")
        (self.root / ".tmpl.docs/research").mkdir(parents=True)
        (self.root / ".tmpl.docs/research/history.md").write_text(
            "Historical examples: {{PROJECT_NAME}} / {{INIT_DATE}}\n", encoding="utf-8"
        )
        (self.root / "README.md").write_text(
            "# Project\n\n<!-- TEMPLATE-DOCS:START -->\n"
            "[Template history](.tmpl.docs/research/history.md)\n"
            "<!-- TEMPLATE-DOCS:END -->\n\nUsage stays here.\n", encoding="utf-8"
        )
        (self.root / "docs/adr").mkdir(parents=True)
        (self.root / "docs/adr/0001-test.md").write_text("date: {{INIT_DATE}}\n", encoding="utf-8")
        for name in ("init-template", "research", "tw-emoji-commit"):
            skill = self.root / ".agents/skills" / name
            skill.mkdir(parents=True)
            (skill / "SKILL.md").write_text(f"# {name}\n", encoding="utf-8")
            link = self.root / ".claude/skills" / name
            link.parent.mkdir(parents=True, exist_ok=True)
            link.symlink_to(f"../../.agents/skills/{name}", target_is_directory=True)

    def run_init(self, *extra):
        return subprocess.run(
            [sys.executable, str(self.root / "scripts/init-project.py"),
             "--name", "驗證專案", "--one-liner", "驗證兩套工具共用初始化。",
             "--date", "2026-09-08", *extra],
            cwd=self.root, capture_output=True, text=True,
        )

    def snapshot(self):
        return {
            str(p.relative_to(self.root)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in self.root.rglob("*") if p.is_file()
        }

    def test_initialization_fills_shared_charter_and_removes_both_skill_entries(self):
        result = self.run_init()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        charter = (self.root / "AGENTS.md").read_text()
        self.assertIn("**驗證專案** — 驗證兩套工具共用初始化。", charter)
        self.assertNotIn("<!-- TEMPLATE:", charter)
        self.assertIn("<!-- PLACEHOLDER -->", charter)
        self.assertEqual((self.root / "CLAUDE.md").read_text(), "@AGENTS.md\n")
        self.assertEqual((self.root / "docs/adr/0001-test.md").read_text(), "date: 2026-09-08\n")
        for rel in (".agents/skills/init-template", ".claude/skills/init-template", "TEMPLATE.md", "scripts/init-project.py"):
            path = self.root / rel
            self.assertFalse(path.exists() or path.is_symlink(), rel)
        for name in ("research", "tw-emoji-commit"):
            self.assertTrue((self.root / ".claude/skills" / name / "SKILL.md").is_file())

    def test_preview_changes_nothing(self):
        before = self.snapshot()
        result = self.run_init("--dry-run")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.snapshot(), before)
        self.assertIn("remove .agents/skills/init-template", result.stdout)

    def test_retained_template_can_be_inspected_but_not_initialized_twice(self):
        result = self.run_init("--keep-template-files")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((self.root / ".claude/skills/init-template/SKILL.md").is_file())
        before = self.snapshot()
        repeated = self.run_init()
        self.assertEqual(repeated.returncode, 1)
        self.assertIn("already initialised", repeated.stderr)
        self.assertEqual(self.snapshot(), before)

    def test_invalid_calendar_date_fails_before_writing(self):
        before = self.snapshot()
        result = self.run_init("--date", "2026-02-30")
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertEqual(self.snapshot(), before)

    def test_default_init_removes_template_history_and_its_readme_link(self):
        result = self.run_init()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertFalse((self.root / ".tmpl.docs").exists())
        readme = (self.root / "README.md").read_text()
        self.assertNotIn(".tmpl.docs/", readme)
        self.assertNotIn("TEMPLATE-DOCS:", readme)
        self.assertIn("Usage stays here.", readme)

    def test_keep_preserves_history_tokens_and_readme_link_verbatim(self):
        history = self.root / ".tmpl.docs/research/history.md"
        readme = self.root / "README.md"
        before = (history.read_bytes(), readme.read_bytes())
        result = self.run_init("--keep-template-files")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual((history.read_bytes(), readme.read_bytes()), before)
        self.assertEqual(self.run_init().returncode, 1)


if __name__ == "__main__":
    unittest.main()
