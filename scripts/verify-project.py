#!/usr/bin/env python3
"""Check portable project instructions, skill links/assets and native role configs.

Python 3.11+. Read-only and offline; run from any working directory.
This checks configuration structure, not model-backed workflow behavior.
"""

import hashlib
import json
from pathlib import Path
import re
import sys
import tomllib


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from skill_links import matches


def verify(root):
    root = root.resolve()
    errors = []

    def check(condition, message):
        if not condition:
            errors.append(message)

    shared = root / "AGENTS.md"
    claude = root / "CLAUDE.md"
    check(shared.is_file(), "AGENTS.md is missing")
    check(claude.is_file() and "@AGENTS.md" in claude.read_text(encoding="utf-8"), "CLAUDE.md must import @AGENTS.md")
    skills_root = root / ".agents/skills"
    skills = sorted(p for p in skills_root.iterdir() if p.is_dir()) if skills_root.exists() else []
    names = {p.name for p in skills}
    for name in ("research", "security-review", "tw-emoji-commit", "tw-emoji-pr-note", "tw-emoji-release-note", "evidence-report", "agent-browser", "i-have-adhd"):
        check(name in names, f"Required project skill is missing: {name}")
    if shared.exists() and ("{{" + "PROJECT_NAME}}") in shared.read_text(encoding="utf-8"):
        check("init-template" in names, "Uninitialized template is missing init-template")

    for skill in skills:
        check(not skill.is_symlink(), f"Shared skill must be a real directory: {skill.name}")
        entry = skill / "SKILL.md"
        check(entry.is_file(), f"Missing SKILL.md: {skill.name}")
        if not entry.is_file():
            continue
        parts = entry.read_text(encoding="utf-8").split("---", 2)
        header = parts[1] if len(parts) == 3 and not parts[0].strip() else ""
        match = re.search(r"^name:\s*([^\n]+)", header, re.M)
        check(bool(match) and match[1].strip().strip("\"'") == skill.name, f"Skill name/frontmatter mismatch: {skill.name}")
        check(bool(re.search(r"^description:\s*\S", header, re.M)), f"Missing description: {skill.name}")
        manual = bool(re.search(r"^disable-model-invocation:\s*true\s*$", header, re.M))
        metadata = skill / "agents/openai.yaml"
        check(metadata.is_file(), f"Missing Codex metadata: {skill.name}")
        if metadata.is_file():
            explicit_only = bool(re.search(r"^\s+allow_implicit_invocation:\s*false\s*$", metadata.read_text(encoding="utf-8"), re.M))
            check(manual == explicit_only, f"Claude/Codex invocation policy differs: {skill.name}")
        link = root / ".claude/skills" / skill.name
        check(matches(link, skill), f"Claude entry must link to or exactly copy the project skill: {skill.name}")

    links_root = root / ".claude/skills"
    if links_root.exists():
        for link in links_root.iterdir():
            check(link.name in names and link.exists(), f"Stale or non-shared Claude skill entry: {link.name}")

    for directory in (skills_root, links_root):
        if not directory.exists():
            continue
        for path in directory.rglob("*"):
            if path.is_symlink():
                target = path.readlink()
                check(not target.is_absolute() and path.resolve().is_relative_to(root) and path.exists(), f"Non-portable or broken link: {path.relative_to(root)}")
            check(path.name not in {".DS_Store", "__pycache__"} and not path.name.endswith((".pyc", ".bak")), f"Local cache/backup was bundled: {path.relative_to(root)}")

    for name, helper in (("tw-emoji-commit", "sanitize_commit.py"), ("tw-emoji-pr-note", "sanitize_pr_note.py"), ("tw-emoji-release-note", "sanitize_release_note.py")):
        check((skills_root / name / "scripts" / helper).is_file(), f"Missing sanitizer: {name}")

    try:
        sources = json.loads((root / "docs/agents/skill-sources.json").read_text(encoding="utf-8"))
        upstream = skills_root / "security-review/references/upstream-security-review.md"
        check(hashlib.sha256(upstream.read_bytes()).hexdigest() == sources["skills"]["security-review"]["upstream_sha256"], "Security-review upstream snapshot differs from its recorded checksum")
        license_body = (skills_root / "security-review/LICENSE").read_text(encoding="utf-8")
        check("MIT License" in license_body, "Security-review MIT license is missing")
    except (OSError, ValueError, KeyError) as error:
        errors.append(f"Skill provenance cannot be checked: {error}")

    try:
        config = tomllib.loads((root / ".codex/config.toml").read_text(encoding="utf-8"))
        check(config.get("sandbox_mode") == "workspace-write", "Unexpected Codex project sandbox default")
        for name in ("harness-reviewer", "harness-researcher"):
            role = tomllib.loads((root / f".codex/agents/{name}.toml").read_text(encoding="utf-8"))
            check(role.get("name") == name and bool(role.get("description")) and bool(role.get("developer_instructions")), f"Incomplete Codex role: {name}")
            check("model" not in role, f"Codex role unexpectedly pins a model: {name}")
            native = root / f".claude/agents/{name}.md"
            check(native.is_file() and f"name: {name}" in native.read_text(encoding="utf-8"), f"Missing Claude role: {name}")
    except (OSError, ValueError) as error:
        errors.append(f"Runtime configuration cannot be checked: {error}")

    return names, errors


def main():
    names, errors = verify(ROOT)
    for error in errors:
        print(f"FAIL: {error}", file=sys.stderr)
    if errors:
        return 1
    print(f"PASS: shared instructions, {len(names)} portable skills, invocation policies, helper assets and native role configs")
    print("Static/offline checks only; confirm discovery in fresh Claude Code and Codex sessions.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
