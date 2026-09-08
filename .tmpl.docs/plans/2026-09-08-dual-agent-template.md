# Dual-agent template implementation plan

**Goal:** Make this template portable between Claude Code and Codex, including security review and Taiwan Traditional Chinese Git-writing skills.

**Authorization:** The user requested full configuration, copying three local skills, finding and carrying security-review, and preserving their newly installed research skill. This is template maintenance, not initialization of a product. Keep project placeholders and the user's research installation. Work in the current checkout so their uncommitted installation remains available. No commit or global configuration change is needed.

**Architecture:** Keep shared instructions in AGENTS.md, imported by CLAUDE.md. Keep skill contents in .agents/skills with relative Claude links. Use each runtime's native agent format without pinning a model across providers. Preserve original security-review source and license, then adapt invocation and Git scope for both runtimes.

**Tools:** Python standard library, Markdown, YAML metadata, TOML runtime configuration, installed CLI parsers, official documentation.

## Tasks and acceptance

1. Research official runtime differences in `.tmpl.docs/research/2026-09-08-claude-code-codex.md`; locate security-review and copy its public source at a pinned revision with its license.
2. Centralize all project skills; copy complete runtime assets for the three `tw-emoji-*` skills; preserve the user-installed `research`. Add both runtimes' manual-invocation metadata and portable sanitizer lookup.
3. Create `AGENTS.md`, thin `CLAUDE.md`, runtime roles and `docs/agents/runtime.md`; update workflow, review, tracker, language, README and TEMPLATE instructions. Retain the template's charter and existing delivery rules.
4. First add a CLI regression test in `tests/test_init_project.py` for shared instructions and skill cleanup. Observe failure with the old initializer, then update `scripts/init-project.py`. Add edge cases one at a time for preview, repeat execution, and retained template files.
5. Add `scripts/verify-project.py` to check instructions, internal links, invocation policy, required skill assets, and config structure without invoking models. Exercise failure cases in temporary copies.
6. Validate clean-copy portability, initialization, sanitizer behavior, CLI configuration loading and independent review. Record verification evidence and any limits in the research report. Leave user account trust and credentials to the host.

## Verification table

| Surface | Check | Expected result |
| --- | --- | --- |
| Init CLI | `python3 -m unittest discover -s tests -v` | Shared charter filled, template links removed safely, preview/repeat safe |
| Repository | `python3 scripts/verify-project.py` | All runtime entries resolve within the repo; skill policy agrees |
| Skill scripts | Pipe text with an IDE link into each sanitizer | Link removed, ordinary Markdown retained |
| Codex CLI | Isolated `--strict-config app-server`, `config/read` and `skills/list` | Native loader accepts project config and all skills |
| Claude Code | Native agent/config inspection without a model call where supported | Project definitions parse and are discoverable |
| Diff | `git diff --check` and independent review | No whitespace errors; scope matches this request |

Configuration files are checked directly, without tests mirroring every literal. Tests target initialization and portability behavior. Model-backed execution is reported separately from static and CLI-loading checks.

## Completion evidence

All six tasks are complete. The research report records native Codex config/skill
discovery, Claude initialization discovery, portable-copy checks, sanitizer results
and the independent review. Four initializer tests pass. The source template stays
uninitialized and all changes remain available for review in the working tree.
No commit, account change or model-backed product run was performed.
