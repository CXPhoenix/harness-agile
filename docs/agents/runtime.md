# Runtime adapters

Use the shared contract and active-runtime section for skills, delegation and tools;
read the handoff section when transferring work. Reuse unchanged context already loaded.
The shared rules live in `AGENTS.md`. This document contains the operational rules
needed by an adopted project and is independent of removable template history.

## Shared skill contract

`.agents/skills/<name>/` is the complete project copy. `.claude/skills/<name>` is a
relative symlink or verified byte-identical copy of it. Read the canonical project copy when a user-level skill has the same
name; helper paths resolve relative to that loaded SKILL.md. Keep reference files
and scripts with their skill. Provenance: [skill-sources.json](skill-sources.json).
`skills-lock.json` records the upstream installer snapshot; local adaptations are
listed in the provenance file and must be preserved or reapplied during updates.

| Upstream wording | Claude Code | Codex |
| --- | --- | --- |
| Invoke `/name` | Use `/name` or native Skill tool | Explicit `$name` or `/skills`; read SKILL.md when instructed by path |
| Call Skill tool | Native Skill tool | Load and follow the named project skill with available tools |
| Task / sub-task / background agent | Native Agent tool | Native spawn/collaboration tools |
| Read / Glob / Grep / Bash | Native tools | File/shell tools; prefer `rg` for search |
| WebSearch / WebFetch | Native web tools | Native search/browser tools, with primary sources |
| AskUserQuestion | Native question tool | Available question tool or ordinary conversation |

Manual-only skills retain both `disable-model-invocation: true` and
`agents/openai.yaml` with `policy.allow_implicit_invocation: false`. Ask for the
user's explicit invocation when required; an existing explicit instruction carries
forward. Other skills remain discoverable. Do not interpret Claude-specific shell
injection syntax or frontmatter as a Codex permission grant.

Shared product state belongs in AGENTS.md. If an older skill calls the Charter or
build commands "CLAUDE.md", read or edit the corresponding section in AGENTS.md;
keep CLAUDE.md as the import adapter. Tracker conventions override upstream `.scratch/`
examples. Skills that explicitly require a particular output destination retain it
unless a project adapter or the user states otherwise.

## Claude Code

`CLAUDE.md` imports `@AGENTS.md`; use `/memory` to inspect loaded instructions.
Use `/skills` and `/agents` to inspect discovery after a fresh session. Project
skills use relative links or synchronized real directories. After reviewing canonical
skill edits, run `python3 scripts/sync-skills.py --refresh`; verification rejects divergent
copies. `--mode copy` avoids filesystem symlink requirements. Git checkouts may contain
flattened link text files; `sync-skills.py` repairs those before verification. Existing user or managed
permissions continue to apply; the template does not enable permission bypass.

Project roles in `.claude/agents/`:

- `harness-reviewer`: file-reading tools; the parent supplies the exact Git diff,
  base, HEAD, uncommitted changes and untracked inventory. One axis per invocation.
- `harness-researcher`: primary-source research with native web and file tools;
  returns citations so the parent can save the research artifact.

Both inherit the current model. The user can select Opus or another available
Claude model through native controls. Model brands are not cross-runtime workflow
requirements. Native plan mode and interactive requirement interviews fit stage 1;
native agents can independently review the resulting evidence.

For security review, explicitly read `.agents/skills/security-review/SKILL.md`.
The built-in `/security-review` remains a host capability, not proof that this
project's adapted skill was loaded. Optional built-ins and installed MCP tools can
supplement the shared workflow; record what they actually verified.

## Codex

For Codex prompt and skill execution boundaries, use [codex.md](codex.md).

Codex reads `AGENTS.md` and discovers project skills in `.agents/skills/`.
`.codex/config.toml` supplies project defaults only after the user trusts this
checkout in their Codex environment. Keep trust decisions and account credentials
local. CLI overrides, managed policy and the active host's permissions take priority.

`.codex/agents/*.toml` defines the Codex Agent roles `harness-reviewer` and `harness-researcher`. Models
and reasoning effort inherit the session. Read-only sandbox defaults express their
role, but the active runtime may override them; check effective permissions and keep
the assignment read-only. The parent captures Git context and writes final reports.
Use the available native agent API with these roles where supported; an API without
custom-role selection can receive the role instructions explicitly.

The configured four child slots are a preference, not a promise: use fewer or batch
when the host limits concurrency. If subagents are unavailable, perform isolated
passes and report that they lacked independent contexts. Keep all four spec-review
axes and the two-round ceiling.

Codex can use its terminal, patching tools, app worktrees and native `review` for
implementation and verification. Native `review` is a supplemental opinion; stage 6
still needs the standards/spec evidence required by the project `code-review` skill.
Either runtime can implement, research or review; task placement follows available
tools and observed results, not an assumed model ranking.

## Cross-runtime handoff and concurrent work

One writer owns a ticket checkout. Concurrent implementations use separate ticket
branches/worktrees. Independent readers may share a checkout only while the writer
keeps its captured review surface stable. Do not automatically create a reviewer
worktree: its default starting ref might omit the change being reviewed.

Use the project `handoff` skill to create the local transfer document. Its temporary
path is suitable for another session on the same machine; for another machine,
ask it to save to the user-selected project path (for example
`.proj.specs/<epic>/handoffs/<ticket-id>.md`). Link existing artifacts instead of
copying their contents. Include:

- Ticket, spec and traceability paths; intended outcome and approved decisions.
- Repository/worktree path, branch, base and HEAD; tracked and untracked changes.
- Checks actually run, results, unverified areas, remaining actions and blockers.
- Project skills needed next, using the receiving host's invocation syntax.

The receiving agent reads AGENTS.md, verifies `git status` and HEAD, then resumes.
Do not transfer credentials or assume conversation history crosses products.

## Verification and updates

Run `python3 scripts/verify-project.py` before handing a copy to another runtime.
It checks local structure and portability, not model quality or pipeline completion.
`python3 -m unittest discover -s tests -v` checks template initialization before the
initializer removes its own template-only test. Fresh sessions should confirm skills
and native roles in their actual host; a long-running session may have an old catalog.

External CLIs (Python 3.11+, Git, agent-browser, gh/glab when used) and MCP account
connections are installed per machine. No API key, browser profile, home path or
global skill symlink is copied into the project. Browser verification may use the
host's native browser tools when the documented surface and evidence are equivalent.
