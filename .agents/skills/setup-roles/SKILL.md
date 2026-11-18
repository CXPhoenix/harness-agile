---
name: setup-roles
description: Set or change the model and reasoning effort of this project's Codex executor and verifier roles. Offered at project start by the AGENTS.md role setup reminder.
---

# Set up the Codex roles

You configure two tiers for Codex only: the executor
(`.codex/agents/harness-executor.toml`) and the verifier
(`harness-reviewer.toml` and `harness-challenger.toml`, one shared setting).
Leave `harness-researcher.toml` and every Claude file untouched.

**Done means**: the user chose an executor and a verifier setting (`inherit` is
allowed), the three role files carry it, the role record is written (in the
template source, the user was told there is none), and the user knows how to
confirm it. The only stop is waiting for the user's values, or step 1 stopping in
the template source without the user's explicit go-ahead.

## Work

1. **Read and explain.** When `docs/agents/template-source.json` is absent, this
   is the template source checkout: stop before editing any role file and tell the
   user the template ships these roles without `model` or
   `model_reasoning_effort` (inherit) for every adopter. Go on only if the user
   explicitly says they are changing the template's shipped defaults; then skip
   step 5. Otherwise read the `model` and `model_reasoning_effort` keys of the
   three role files and the tiers in `docs/agents/orchestration.md`. Explain in two
   sentences: the decider is this thread, whose model and effort the user picks in
   Codex and this skill leaves alone; the executor applies approved changes and
   runs verification commands, and the verifier reviews and challenges read-only.
2. **Ask** for executor model and effort, and verifier model and effort. Always
   ask for effort, which a thread cannot see. Offer `inherit` for each and say
   what it means: the key is omitted, so the child takes a model or effort passed
   at spawn, else `agents.default_subagent_model` or
   `agents.default_subagent_reasoning_effort` from `config.toml`, else the
   thread's value. When the user pins a model, ask for an effort that model
   supports too: an omitted effort carries the thread's effort to the pinned
   model, and the spawn fails if the model lacks it. Omitting both keys is the
   safe fallback. The role files and the record are committed and shared, so
   suggest models every teammate's account can use.
3. **Validate.** Accept any non-empty model string or `inherit`, and any
   non-empty effort string (common values: `low`, `medium`, `high`, `xhigh`; the
   model decides which are valid) or `inherit`; ask again only for a missing
   value. Do not try to check what the account or model supports; a bad value
   fails when the role is spawned. Fallbacks are in `docs/agents/orchestration.md`.
4. **Write the role files.** Executor values go to `harness-executor.toml`;
   verifier values go to both `harness-reviewer.toml` and
   `harness-challenger.toml`. Replace an existing `model` or
   `model_reasoning_effort` key in place; otherwise insert it at top level right
   after `description`, before `developer_instructions`. For `inherit`, remove
   the key; never write the string `"inherit"` into TOML. Never leave a duplicate
   key, and change no other line; `developer_instructions` stays as is.
5. **Record.** When `docs/agents/template-source.json` exists, set its
   `roles.codex` key to `{"configured_on": "<today, YYYY-MM-DD>", "executor":
   {"model": ..., "effort": ...}, "verifier": {"model": ..., "effort": ...}}`,
   writing the string `"inherit"` where chosen. Load the JSON, change only that
   key (keep `roles.claude` and every other key), and write it back with
   `json.dumps(state, ensure_ascii=False, indent=2)` plus a trailing newline. In
   the template source, skip the record and say so.
6. **Check.** Run `python3 scripts/verify-project.py` and report its result line.

## Hand over

Tell the user:

- Start a new thread so Codex loads the changed role files, then spawn each
  changed role once with a trivial task; a spawn error names an unsupported model
  or effort. Rerun `$setup-roles` with another value or `inherit`.
- Template updates to these role files arrive as `*.harness-new` sidecars; keep
  their own `model` and `model_reasoning_effort` lines when merging.

Leave the files uncommitted; when the user asks, commit through the commit skill
(AGENTS.md hard rule 5).
