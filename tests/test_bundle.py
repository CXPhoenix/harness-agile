"""Validate package snapshot boundaries before writing a generated project."""
import base64
from pathlib import Path
import tempfile
import unittest
from harness_agile.bundle import unpack, digest


class BundleTests(unittest.TestCase):
    def test_rejects_unsafe_paths_before_any_writes(self):
        for bad in ('../outside', '/absolute', 'C:/drive', '.git/config', 'a\\b', 'CON', 'folder/../outside'):
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
