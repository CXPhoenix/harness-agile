#!/usr/bin/env python3
"""Fill this template's placeholders and remove the template-only files.

Run once, right after copying or cloning harness-agile-template into a new project:

    python3 scripts/init-project.py --name "My Project" --one-liner "What it does, in one line."

Add --dry-run to see the plan without touching anything. The script refuses to run twice: once the
tokens are gone there is nothing to fill, and a second run would only delete files.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import re
import shutil
import sys
from pathlib import Path

TOKENS = ("{{PROJECT_NAME}}", "{{PROJECT_ONE_LINER}}", "{{INIT_DATE}}")

# Directories never walked: vendored upstream skills, git internals, caches.
SKIP_DIRS = {".git", ".agents", "__pycache__", "node_modules", ".venv"}

# Text extensions worth scanning. Anything else is left alone.
TEXT_SUFFIXES = {".md", ".txt", ".json", ".toml", ".yaml", ".yml", ".html", ".py", ".sh"}

# Removed after a successful run unless --keep-template-files is given.
TEMPLATE_ONLY = (
    ".tmpl.docs", "TEMPLATE.md", "scripts/init-project.py", "tests/test_init_project.py",
    ".claude/skills/init-template", ".agents/skills/init-template",
)

# The banner in shared instructions that only makes sense before initialisation.
BANNER = re.compile(
    r"\n\n<!-- TEMPLATE:.*?-->\n",
    re.DOTALL,
)
TEMPLATE_DOC_LINK = re.compile(
    r"<!-- TEMPLATE-DOCS:START -->.*?<!-- TEMPLATE-DOCS:END -->\n?",
    re.DOTALL,
)


def project_root() -> Path:
    return Path(__file__).resolve().parent.parent


def is_template_only(rel: Path) -> bool:
    """The template's own scaffolding. It documents the tokens rather than carrying them, so
    filling it would corrupt this script and its skill under --keep-template-files."""
    posix = rel.as_posix()
    return any(posix == t or posix.startswith(t + "/") for t in TEMPLATE_ONLY)


def text_files(root: Path):
    for path in sorted(root.rglob("*")):
        rel = path.relative_to(root)
        if any(part in SKIP_DIRS for part in rel.parts):
            continue
        if is_template_only(rel):
            continue
        if path.is_symlink() or not path.is_file():
            continue
        if path.suffix.lower() in TEXT_SUFFIXES:
            yield path


def find_tokens(root: Path) -> dict[Path, list[str]]:
    hits: dict[Path, list[str]] = {}
    for path in text_files(root):
        try:
            body = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        present = [t for t in TOKENS if t in body]
        if present:
            hits[path] = present
    return hits


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--name", help="Human-readable project name, e.g. 'Acme Scheduler'")
    ap.add_argument("--one-liner", help="One sentence saying what the project does")
    ap.add_argument("--date", default=_dt.date.today().isoformat(), help="ADR adoption date (default: today)")
    ap.add_argument("--dry-run", action="store_true", help="Print the plan and change nothing")
    ap.add_argument("--keep-template-files", action="store_true", help="Keep template documentation, its README link, initializer, test, and init skill entries")
    args = ap.parse_args()

    root = project_root()
    hits = find_tokens(root)

    if not hits:
        print("Nothing to do: no template tokens found. This project is already initialised.", file=sys.stderr)
        print("If you meant to remove the template-only files, delete them by hand.", file=sys.stderr)
        return 1

    missing = [flag for flag, val in (("--name", args.name), ("--one-liner", args.one_liner)) if not val]
    if missing:
        print(f"Missing required argument(s): {', '.join(missing)}", file=sys.stderr)
        print("\nTokens still to fill:", file=sys.stderr)
        for path, toks in hits.items():
            print(f"  {path.relative_to(root)}: {', '.join(toks)}", file=sys.stderr)
        return 2

    try:
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", args.date):
            raise ValueError("Expected YYYY-MM-DD")
        _dt.date.fromisoformat(args.date)
    except ValueError:
        print(f"--date must be a valid YYYY-MM-DD date, got {args.date!r}", file=sys.stderr)
        return 2

    replacements = {
        "{{PROJECT_NAME}}": args.name,
        "{{PROJECT_ONE_LINER}}": args.one_liner,
        "{{INIT_DATE}}": args.date,
    }

    prefix = "[dry-run] " if args.dry_run else ""
    for path in sorted(hits):
        body = path.read_text(encoding="utf-8")
        for token, value in replacements.items():
            body = body.replace(token, value)
        if path.name in {"AGENTS.md", "CLAUDE.md"}:
            body = BANNER.sub("\n", body, count=1)
        print(f"{prefix}fill {path.relative_to(root)} ({', '.join(hits[path])})")
        if not args.dry_run:
            path.write_text(body, encoding="utf-8")

    if not args.keep_template_files:
        readme = root / "README.md"
        if readme.is_file() and not readme.is_symlink():
            body = readme.read_text(encoding="utf-8")
            cleaned = TEMPLATE_DOC_LINK.sub("", body)
            if cleaned != body:
                print(f"{prefix}remove template documentation link from README.md")
                if not args.dry_run:
                    readme.write_text(cleaned, encoding="utf-8")
        for rel in TEMPLATE_ONLY:
            target = root / rel
            if not target.exists() and not target.is_symlink():
                continue
            print(f"{prefix}remove {rel}")
            if not args.dry_run:
                if target.is_symlink():
                    target.unlink()
                elif target.is_dir():
                    shutil.rmtree(target)
                else:
                    target.unlink()
        scripts_dir = root / "scripts"
        if scripts_dir.is_dir() and not args.dry_run and not any(scripts_dir.iterdir()):
            scripts_dir.rmdir()
            print("remove scripts/ (now empty)")

    if args.dry_run:
        print("\n[dry-run] nothing was written.")
        return 0

    leftover = find_tokens(root)
    if leftover:
        print("\nWARNING: tokens still present after the run:", file=sys.stderr)
        for path, toks in leftover.items():
            print(f"  {path.relative_to(root)}: {', '.join(toks)}", file=sys.stderr)
        return 3

    print(
        "\nDone. Next: use grill-with-docs to fill the Project Charter in AGENTS.md.\n"
        "Claude Code: /grill-with-docs; Codex: $grill-with-docs.\n"
        "Until that section is written, AGENTS.md's gate blocks specs, tickets, and implementation."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
