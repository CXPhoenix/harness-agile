#!/usr/bin/env python3
"""Check portable project instructions, per-runtime skill trees, native role configs and CodeGraph wiring.

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
REQUIRED = ("research", "security-review", "tw-emoji-commit", "tw-emoji-pr-note", "tw-emoji-release-note", "evidence-report", "agent-browser", "i-have-adhd", "tune-skills", "egm-drift-report", "setup-roles")
SANITIZERS = (("tw-emoji-commit", "sanitize_commit.py"), ("tw-emoji-pr-note", "sanitize_pr_note.py"), ("tw-emoji-release-note", "sanitize_release_note.py"))


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
    uninitialized = shared.exists() and ("{{" + "PROJECT_NAME}}") in shared.read_text(encoding="utf-8")
    ignore = root / ".gitignore"
    ignored = ignore.read_text(encoding="utf-8").splitlines() if ignore.is_file() else []
    check(any(line.strip() in {"/.proj.handoffs/", ".proj.handoffs/"} for line in ignored), ".gitignore must exclude /.proj.handoffs/")

    # Each runtime owns an independent skill tree; contents may diverge.
    trees = {"Codex": root / ".agents/skills", "Claude": root / ".claude/skills"}
    policies = {}
    for runtime, skills_root in trees.items():
        check(not skills_root.is_symlink() and not skills_root.parent.is_symlink(), f"{runtime} skill root must be a real directory")
        # is_symlink: on Windows a directory link may not report is_dir.
        skills = sorted(p for p in skills_root.iterdir() if p.is_dir() or p.is_symlink()) if skills_root.exists() else []
        names = {p.name for p in skills}
        for name in REQUIRED:
            check(name in names, f"Required {runtime} skill is missing: {name}")
        if uninitialized:
            check("init-template" in names, f"Uninitialized template is missing {runtime} init-template")
        for name, helper in SANITIZERS:
            check((skills_root / name / "scripts" / helper).is_file(), f"Missing {runtime} sanitizer: {name}")
        policies[runtime] = {}
        for skill in skills:
            check(not skill.is_symlink(), f"{runtime} skill must be a real directory: {skill.name}")
            entry = skill / "SKILL.md"
            check(entry.is_file(), f"Missing {runtime} SKILL.md: {skill.name}")
            if not entry.is_file():
                continue
            parts = entry.read_text(encoding="utf-8").split("---", 2)
            header = parts[1] if len(parts) == 3 and not parts[0].strip() else ""
            match = re.search(r"^name:\s*([^\n]+)", header, re.M)
            check(bool(match) and match[1].strip().strip("\"'") == skill.name, f"{runtime} skill name/frontmatter mismatch: {skill.name}")
            check(bool(re.search(r"^description:\s*\S", header, re.M)), f"Missing {runtime} description: {skill.name}")
            claude_manual = bool(re.search(r"^disable-model-invocation:", header, re.M))
            metadata = skill / "agents/openai.yaml"
            if runtime == "Codex":
                check(not claude_manual, f"Codex skill carries Claude-only frontmatter: {skill.name}")
                check(metadata.is_file(), f"Missing Codex metadata: {skill.name}")
                if metadata.is_file():
                    policies[runtime][skill.name] = bool(re.search(r"^\s+allow_implicit_invocation:\s*false\s*$", metadata.read_text(encoding="utf-8"), re.M))
            else:
                check(not metadata.exists(), f"Claude skill carries Codex-only metadata: {skill.name}")
                policies[runtime][skill.name] = bool(re.search(r"^disable-model-invocation:\s*true\s*$", header, re.M))
        for path in skills_root.rglob("*") if skills_root.exists() else ():
            check(not path.is_symlink(), f"Skill trees must not contain links: {path.relative_to(root)}")
            check(path.name not in {".DS_Store", "__pycache__"} and not path.name.endswith((".pyc", ".bak")), f"Local cache/backup was bundled: {path.relative_to(root)}")

    for name in policies["Codex"].keys() & policies["Claude"].keys():
        check(policies["Codex"][name] == policies["Claude"][name], f"Claude/Codex invocation policy differs: {name}")
    for runtime, policy in policies.items():
        if "egm-drift-report" in policy:
            check(policy["egm-drift-report"], f"{runtime} egm-drift-report must be explicitly invoked")
    names = policies["Codex"].keys() | policies["Claude"].keys()

    # harness-agile migrate leaves new template content beside locally edited template files.
    try:
        state = json.loads((root / "docs/agents/template-source.json").read_text(encoding="utf-8"))
        recorded = state.get("files", {}) if isinstance(state, dict) and state.get("schema") == 2 else {}
    except (OSError, ValueError):
        recorded = {}
    for rel in recorded if isinstance(recorded, dict) else ():
        if (root / (rel + ".harness-new")).exists():
            errors.append(f"Unresolved migration sidecar: merge {rel}.harness-new into {rel}, then delete it")

    try:
        sources = json.loads((root / "docs/agents/skill-sources.json").read_text(encoding="utf-8"))
        for runtime, skills_root in trees.items():
            upstream = skills_root / "security-review/references/upstream-security-review.md"
            check(hashlib.sha256(upstream.read_bytes()).hexdigest() == sources["skills"]["security-review"]["upstream_sha256"], f"{runtime} security-review upstream snapshot differs from its recorded checksum")
            license_body = (skills_root / "security-review/LICENSE").read_text(encoding="utf-8")
            check("MIT License" in license_body, f"{runtime} security-review MIT license is missing")
    except (OSError, ValueError, KeyError) as error:
        errors.append(f"Skill provenance cannot be checked: {error}")

    config = {}
    try:
        config = tomllib.loads((root / ".codex/config.toml").read_text(encoding="utf-8"))
        check(config.get("sandbox_mode") == "workspace-write", "Unexpected Codex project sandbox default")
        # Executor and verifier roles may pin a model (setup-roles); the researcher
        # extends the decider and always inherits the session model.
        for name in ("harness-executor", "harness-reviewer", "harness-challenger", "harness-researcher"):
            role = tomllib.loads((root / f".codex/agents/{name}.toml").read_text(encoding="utf-8"))
            check(role.get("name") == name and bool(role.get("description")) and bool(role.get("developer_instructions")), f"Incomplete Codex role: {name}")
            native = root / f".claude/agents/{name}.md"
            text = native.read_text(encoding="utf-8") if native.is_file() else ""
            check(f"name: {name}" in text, f"Missing Claude role: {name}")
            parts = text.split("---", 2)
            header = parts[1] if len(parts) == 3 and not parts[0].strip() else ""
            if name == "harness-researcher":
                check(not {"model", "model_reasoning_effort"} & role.keys(), f"Codex {name} must inherit the session model")
                check(bool(re.search(r"^model:\s*inherit\s*$", header, re.M)), f"Claude {name} must inherit the session model")
                check(not re.search(r"^effort:", header, re.M), f"Claude {name} must inherit the session effort")
    except (OSError, ValueError) as error:
        errors.append(f"Runtime configuration cannot be checked: {error}")

    # A registered CodeGraph server builds .codegraph/, a local index kept out of Git.
    servers = config.get("mcp_servers", {})
    check(isinstance(servers, dict), ".codex/config.toml mcp_servers must be a table")
    registered = isinstance(servers, dict) and "codegraph" in servers
    mcp = root / ".mcp.json"
    if mcp.exists():
        try:
            data = json.loads(mcp.read_text(encoding="utf-8"))
        except (OSError, ValueError) as error:
            errors.append(f".mcp.json cannot be parsed: {error}")
        else:
            servers = data.get("mcpServers", {}) if isinstance(data, dict) else None
            check(isinstance(servers, dict), ".mcp.json must be a JSON object whose mcpServers is an object")
            registered = registered or isinstance(servers, dict) and "codegraph" in servers
    if registered:
        check(any(line.strip() in {"/.codegraph/", ".codegraph/"} for line in ignored), ".gitignore must exclude /.codegraph/ while CodeGraph is registered")

    return names, errors, registered


def main():
    names, errors, registered = verify(ROOT)
    for error in errors:
        print(f"FAIL: {error}", file=sys.stderr)
    if errors:
        return 1
    codegraph = " and the CodeGraph index ignore rule" if registered else "; CodeGraph is not registered, so its ignore rule was not checked"
    print(f"PASS: shared instructions, {len(names)} skills across Claude/Codex trees, invocation policies, helper assets, native role configs{codegraph}")
    print("Static/offline checks only; confirm discovery in fresh Claude Code and Codex sessions.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
