"""Build the same regular-file bundle for wheels and source distributions."""
from pathlib import Path
import sys
from hatchling.builders.hooks.plugin.interface import BuildHookInterface


class CustomBuildHook(BuildHookInterface):
    def initialize(self, version, build_data):
        root = Path(self.root)
        sys.path.insert(0, str(root))
        from harness_agile.bundle import build
        resource = root / 'harness_agile/data/template.json'
        if (root / 'scripts/init-project.py').is_file():
            build(root)
        elif not resource.is_file():
            raise RuntimeError('Source distribution is missing its template bundle')
        build_data.setdefault('artifacts', []).append('harness_agile/data/template.json')
