# Claude Code entrypoint

@AGENTS.md

Use the shared rules above. Before using runtime-specific tools, read
`docs/agents/runtime.md` (Claude Code section). Claude's project skills live in
`.claude/skills/`, a Claude-tuned copy; `.agents/skills/` belongs to Codex.

Project roles in `.claude/agents/` map to the tiers in AGENTS.md: `harness-executor`
is the executor; `harness-reviewer` (red team) and `harness-challenger` (devil's
advocacy, alternatives) form the verifier tier; `harness-researcher` extends this
session and inherits its model. `/setup-roles` sets the executor and verifier models
(template default: inherit). Before delegating, read
`docs/agents/claude-orchestration.md` for when to use each role and how findings
reach the user. This session captures Git diffs, saves reports and commits. It hands
approved changes and every run whose output a gate or a verifier judges to the
executor, which also runs the transcribed `/tdd` loop when this session delegates a
ticket's implementation. This session makes a trivial edit itself, with the quick
checks that edit needs, only when delegating would cost more.

For pipeline stage 7, read `.claude/skills/security-review/SKILL.md` explicitly:
Claude's built-in `/security-review` can have the same command name.
