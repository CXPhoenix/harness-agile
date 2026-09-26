# Claude Code entrypoint

@AGENTS.md

Use the shared rules above. Before using runtime-specific tools, read
`docs/agents/runtime.md` (Claude Code section). Claude's project skills live in
`.claude/skills/`, a Claude-tuned copy; `.agents/skills/` belongs to Codex.

Use the native `Agent` tool with `harness-reviewer` or `harness-researcher` for
bounded independent work. The parent captures Git diffs and saves reports; these
roles return evidence without changing the reviewed checkout. Model selection
inherits this session and may be overridden by the user in Claude's own controls.

For pipeline stage 7, read `.claude/skills/security-review/SKILL.md` explicitly:
Claude's built-in `/security-review` can have the same command name.
