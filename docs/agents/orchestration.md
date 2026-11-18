# Orchestration

Work runs in three tiers, defined in `AGENTS.md`. This file maps them to role files,
records how the executor and verifier are configured, and fixes the verification
hand-off. Runtime specifics: [claude-orchestration.md](claude-orchestration.md) for
Claude Code, [codex.md](codex.md) and [runtime.md](runtime.md) for Codex.

## Tiers

| Tier | Responsibility | Claude role file | Codex role file | Model source |
|---|---|---|---|---|
| Decider | understands the request, plans, delegates, makes the final call, talks to the user, loads skills, commits | main session | main session | the user's selection in the host; the template never sets it |
| Executor | applies approved changes; runs every command whose output a gate or a verifier judges and reports raw output and exit status | `.claude/agents/harness-executor.md` | `.codex/agents/harness-executor.toml` | executor tier setting (default inherit) |
| Verifier | reviews, challenges and confirms from evidence; inspects read-only (reading, listing and searching files, `git show`/`diff`/`log`/`status`, CodeGraph queries) and runs no checks, builds, tests, scripts or state-changing commands | `.claude/agents/harness-reviewer.md`, `harness-challenger.md` | `.codex/agents/harness-reviewer.toml`, `harness-challenger.toml` | verifier tier setting, shared by both roles (default inherit) |
| Decider extension | primary-source research that feeds the decider | `.claude/agents/harness-researcher.md` | `.codex/agents/harness-researcher.toml` | always inherits the main session |

A **tier setting** is the model and effort one runtime chooses for the executor or
the verifier. `inherit` is a valid value for either.

## Role setup

`/setup-roles` (Codex: `$setup-roles`) is user-invoked: the agent offers it as the
`AGENTS.md` role setup reminder describes and never runs it on its own. Each
runtime's copy edits only that runtime's role files and writes only its own key in
the role record.

The role record lives in `docs/agents/template-source.json`:

```json
"roles": {
  "claude": {
    "configured_on": "2026-11-18",
    "executor": {"model": "inherit", "effort": "inherit"},
    "verifier": {"model": "claude-opus-5-5", "effort": "high"}
  },
  "codex": { "...": "same shape, written by the Codex setup-roles" }
}
```

- A runtime is **configured** once `roles.<runtime>` exists. Choosing `inherit` for
  both tiers is a configured choice and stops the reminder. Only the active
  runtime's key counts: a Claude Code session ignores `roles.codex`, and the reverse.
- A runtime writes `roles.claude` or `roles.codex` only; every other key stays as it
  was.
- Without `template-source.json` (the template's own checkout) there is no record
  and no reminder: template maintenance is outside the product gates.
- The role record and the role files are committed, so a setting applies to everyone
  who works in the repository and stops the reminder for all of them. Choose `inherit`
  or a model every teammate's account can use.

## Verification hand-off

Running the evidence belongs to the executor; judging it belongs to the verifier. The
executor runs every command whose output a gate or a verifier judges: stage 5 gate
test and coverage runs, stage 7 fix verification, stage 8 end-to-end checks, and any
command a verifier asks for. Implementation is execution too: when the decider
delegates a ticket's implementation, the executor runs the transcribed `/tdd` loop,
red and green runs included.

1. The decider decides what to verify, or a verifier's report asks for specific
   evidence.
2. The decider hands the exact commands to the executor. The executor runs them as
   given and returns raw output and exit status; it may say whether a command
   passed and leaves interpretation to the verifier.
3. The decider passes that output to the verifier for judgement. The final call
   stays with the decider; disputes go to the user ([review.md](review.md)).
4. Exceptions: the decider may run read-only queries itself, and may make a trivial
   edit, with the quick checks that edit needs (for example `scripts/verify-project.py`
   after a one-line change, or the checks inside `/setup-roles` and `/tune-skills`),
   when delegating costs more than the work.
5. These constraints hold throughout:
   - Stage 3 stays four axes. The challenger is not a fifth reviewer, and no agent
     arbitrates; disagreements reach the user with both positions and evidence.
   - Findings reach the user unfiltered. The decider may deduplicate, rank and
     annotate, but shows the user any finding it proposes to drop.
   - Roles do not nest: the executor and verifier start no subagents.
   - Commits stay with the decider and the project commit skill.

## Template updates

Role files are template-managed. When a role file has been customized (including by
`/setup-roles`), a template update (migrate) writes the new version beside it as
`<file>.harness-new` instead of overwriting it. Merge the sidecar, keep your own
model and effort lines, then delete the sidecar. The role record survives updates:
`template-source.json` is seeded, and migrate merges into it while keeping unknown
keys.

## Fallbacks

- **Claude full model IDs** need a Claude Code version that recognizes them; an older
  version fails the delegation with an unrecognized-model error. Update Claude Code
  or set the role to `inherit`.
- **Claude environment overrides:** `CLAUDE_CODE_SUBAGENT_MODEL_FORCE=1` or
  `CLAUDE_CODE_EFFORT_LEVEL` silently override the role files, and so does
  `CLAUDE_CODE_SUBAGENT_MODEL` on older Claude Code versions. Check them when a role
  does not run on its configured model or effort.
- **Claude call-time parameters:** a `model` or `effort` passed in the Agent tool
  call outranks the role's frontmatter. Pass neither when delegating, so the tier
  setting applies.
- **Claude effort across models:** a role on a different model from the main
  session does not receive the session's effort; it gets that model's default. Set
  effort explicitly for such a role. An effort level the model lacks is downgraded.
- **Codex models** depend on the account, and an effort the model does not support
  fails the spawn. A role that pins `model` without `model_reasoning_effort` takes the
  session's current effort, which can fail the spawn on the pinned model: set both or
  omit both. Omitting both is the fallback that inherits the session.
- **Codex overrides:** when a role omits `model`, a model or effort passed at spawn
  time applies instead of the session's, and so do `default_subagent_model` and
  `default_subagent_reasoning_effort` under `[agents]` in a user or project
  `config.toml`. Check them when a role does not run on the session's model.
