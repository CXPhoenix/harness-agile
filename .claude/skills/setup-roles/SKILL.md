---
name: setup-roles
description: Set or change the model and effort of this project's executor and verifier roles for Claude Code. Offered at project start by the AGENTS.md role setup reminder.
disable-model-invocation: true
---

# Set up the Claude roles

This skill sets two tiers for Claude Code only: the executor
(`.claude/agents/harness-executor.md`) and the verifier (`harness-reviewer.md` and
`harness-challenger.md`, which share one setting). Leave `harness-researcher.md`
and every Codex file untouched.

**Done means**: the user chose an executor and a verifier setting (`inherit` is
allowed), the three role files carry it, the role record is written (in the
template source, the user was told there is none), and the user knows how to
confirm it; or, in the template source without the user's go-ahead, step 1
stopped and said why.

## 1. Read and explain

When `docs/agents/template-source.json` is absent, this is the template source
checkout: stop before editing any role file and tell the user the template ships
these roles as `inherit` for every adopter. Go on only if the user explicitly says
they are changing the template's shipped defaults; then skip the record in step 4.

Read the `model:` and `effort:` lines of the three role files and the tiers in
`docs/agents/orchestration.md`. Explain in two sentences: the decider is this
session, whose model and effort the user picks in Claude Code and this skill
leaves alone; the executor applies approved changes and runs verification
commands, and the verifier reviews and challenges read-only.

## 2. Ask

Ask for four values: executor model and effort, verifier model and effort. Always
ask for effort, which a session cannot see. Offer `inherit` for each and say what
it means: a model `inherit` runs the session's model; an effort `inherit` (the
`effort:` line removed) gets the session's effort only when the role also runs the
session's model, otherwise that model's default effort. When the user pairs a
different model with effort `inherit`, say so and ask whether to set an effort.
Use only values the user gives; ask again for a missing one. When the user wants a
recommendation, point to `docs/agents/claude-orchestration.md`; the choice stays
theirs. The role files and the record are committed and shared, so suggest models
every teammate can use.

Accept as a model an alias or full model ID that Claude Code's `/model` accepts,
or `inherit`, without checking what the account can run: a bad value surfaces
when the role is delegated to. Accept an effort of `low`, `medium`, `high`,
`xhigh`, `max` or `inherit`; ask again for any other effort.

## 3. Write the role files

Executor values go to `harness-executor.md`; verifier values go to both
`harness-reviewer.md` and `harness-challenger.md`. In each frontmatter, replace an
existing `model:` or `effort:` line in place; otherwise put `effort: <value>` on
the line after `model:`. For effort `inherit`, remove the `effort:` line. Never
leave a duplicate key, and change no other line.

## 4. Record and check

When `docs/agents/template-source.json` exists, set its `roles.claude` key to
`{"configured_on": "<today, YYYY-MM-DD>", "executor": {"model": ..., "effort": ...},
"verifier": {"model": ..., "effort": ...}}`, writing the string `"inherit"` where
chosen. Load the JSON, change only that key (keep `roles.codex` and every other
key), and write it back with `json.dumps(state, ensure_ascii=False, indent=2)`
plus a trailing newline. In the template source, skip the record and say so.

Run `python3 scripts/verify-project.py` and report its result line.

## 5. Hand over

Tell the user:

- Start a new session, then confirm each role's model in `/agents`. A value
  Claude Code does not recognize fails delegation; rerun with another value.
- `CLAUDE_CODE_SUBAGENT_MODEL_FORCE=1` or `CLAUDE_CODE_EFFORT_LEVEL` in their
  environment overrides these files; an effort a model lacks is lowered.
- Template updates to these role files arrive as `*.harness-new` sidecars; keep
  their own `model:` and `effort:` lines when merging.

Leave the files uncommitted; when the user asks, commit through the commit skill
(AGENTS.md hard rule 5).
