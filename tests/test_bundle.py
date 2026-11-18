"""Validate package snapshot boundaries before writing a generated project."""
import base64
import json
from pathlib import Path
import re
import tempfile
import tomllib
import unittest
from harness_agile.bundle import unpack, digest, snapshot

ROOT = Path(__file__).resolve().parents[1]


class BundleTests(unittest.TestCase):
    def test_npm_renamed_gitignore_preserves_snapshot_content(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / 'scripts').mkdir()
            (root / 'scripts/init-project.py').write_text('# fixture')
            (root / '.gitignore').write_text('.env\n')
            expected = snapshot(root)
            (root / '.gitignore').rename(root / '.npmignore')
            self.assertEqual(snapshot(root)['files'], expected['files'])

    def test_ships_the_codegraph_registration(self):
        files = snapshot(ROOT)['files']
        claude = json.loads(base64.b64decode(files['.mcp.json']))['mcpServers']['codegraph']
        codex = tomllib.loads(base64.b64decode(files['.codex/config.toml']).decode('utf-8'))['mcp_servers']['codegraph']
        # Both runtimes start the same server with telemetry off; 1.6.2 rejects --no-telemetry on serve.
        for entry in (claude, codex):
            self.assertEqual((entry['command'], entry['args']), ('codegraph', ['serve', '--mcp']))
            self.assertEqual(entry['env'], {'DO_NOT_TRACK': '1', 'CODEGRAPH_TELEMETRY': '0'})
            self.assertNotIn('--no-telemetry', entry['args'])
        index = json.loads(base64.b64decode(files['codegraph.json']))
        self.assertEqual(index['exclude'], ['.claude/skills/', '.agents/skills/'])

    def test_template_roles_ship_inheriting_the_session(self):
        # Template-only: setup-roles may pin these in an adopted project, so verify-project.py cannot check this.
        for name in ('harness-executor', 'harness-reviewer', 'harness-challenger', 'harness-researcher'):
            with self.subTest(role=name):
                header = (ROOT / f'.claude/agents/{name}.md').read_text(encoding='utf-8').split('---', 2)[1]
                self.assertRegex(header, re.compile(r'^model:\s*inherit\s*$', re.M))
                self.assertNotRegex(header, re.compile(r'^effort:', re.M))
                role = tomllib.loads((ROOT / f'.codex/agents/{name}.toml').read_text(encoding='utf-8'))
                self.assertFalse({'model', 'model_reasoning_effort'} & role.keys(), role.keys())

    def test_rejects_unsafe_paths_before_any_writes(self):
        for bad in ('../outside', '/absolute', 'C:/drive', '.git/config', '.GIT/config', 'a\\b', 'CON', 'folder/../outside'):
            with self.subTest(path=bad), tempfile.TemporaryDirectory() as temp:
                files = {'safe': base64.b64encode(b'ok').decode(), bad: base64.b64encode(b'bad').decode()}
                bundle = {'schema': 1, 'files': files, 'source': {'content_sha256': digest(files)}}
                target = Path(temp)
                with self.assertRaises(ValueError):
                    unpack(bundle, target)
                self.assertEqual(list(target.iterdir()), [])

    def test_rejects_altered_payload(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(ValueError):
                unpack({'schema': 1, 'files': {'safe': 'b2s='}, 'source': {'content_sha256': 'incorrect'}}, Path(temp))
