#!/usr/bin/env python3
"""Rebuild Claude skill links or copies from .agents/skills after reviewed edits."""
import argparse
from pathlib import Path
from skill_links import sync


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mode', choices=['auto', 'symlink', 'copy'], default='auto')
    parser.add_argument('--refresh', action='store_true', help='Replace reviewed, divergent Claude copies with canonical content')
    args = parser.parse_args()
    try:
        mode = sync(Path(__file__).resolve().parents[1], args.mode, args.refresh)
    except (OSError, ValueError) as error:
        parser.exit(1, f'Skill sync failed: {error}\n')
    print(f'Skills synchronized ({mode}). Run python3 scripts/verify-project.py next.')


if __name__ == '__main__':
    main()
