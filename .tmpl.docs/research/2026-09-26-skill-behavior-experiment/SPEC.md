# Experiment harness spec (approved; build exactly this)

Root: `/private/tmp/claude-501/-Users-phoenix-dev-edu-projects-harness-agile-template/10458df1-fb73-44a4-804a-3b27b3c08dbf/scratchpad/exp` (call it EXP).

Skill sources:
- baseline: `/Users/phoenix/dev/edu-projects/harness-agile-template/.claude/skills/<skill>/SKILL.md` (repo HEAD, unpatched)
- patched: `/private/tmp/claude-501/-Users-phoenix-dev-edu-projects-harness-agile-template/10458df1-fb73-44a4-804a-3b27b3c08dbf/scratchpad/audit4/.claude/skills/<skill>/SKILL.md`
- role file for both conditions: `/Users/phoenix/dev/edu-projects/harness-agile-template/.claude/agents/harness-researcher.md`

## Files to create

### EXP/fixture/ (the neutral base repo, copied into every trial)

- `CLAUDE.md` with exactly:
  ```
  # Demo project

  A small command-line todo list used for experiments. Follow the user's request.
  ```
- `todo.py`: a working ~40-line Python 3 CLI storing todos in `todos.json` (commands: `add <text>`, `list`, `done <n>`), standard library only.
- `README.md`: two lines describing usage of todo.py.
- No AGENTS.md, no docs/, no .claude/ (the runner adds .claude per trial).

### EXP/prompts/s3.txt (exactly)

```
Read .claude/skills/research/SKILL.md and follow it for this request: what does the `disable-model-invocation` frontmatter field do for Claude Code skills? Use the official Claude Code documentation.
```

### EXP/prompts/s4.txt (exactly)

```
Read .claude/skills/grilling/SKILL.md and follow it. The grilling session below already happened; continue from its end.

<transcript>
Assistant: What should a due date look like on the command line?
User: `add "text" --due 2026-10-01`, ISO dates only.
Assistant: Where is it stored?
User: As a "due" string field in each todos.json entry; entries without it stay valid.
Assistant: What does `list` show?
User: The due date in brackets after the text, and overdue items marked with "!".
Assistant: What happens with an invalid date?
User: Print an error and exit with status 2; nothing is saved.
Assistant: Summary of our shared understanding: `add` accepts an optional `--due YYYY-MM-DD`; it is stored as an optional "due" field; `list` shows "[YYYY-MM-DD]" and a "!" for overdue items; an invalid date prints an error, exits 2 and saves nothing. Deferred: time zones and recurring tasks. Is this right?
User: 確認，這就是我們的共識。
</transcript>
```

### EXP/run_experiment.py

Python 3 standard library only. CLI: `python3 run_experiment.py [--dry-run] [--scenarios s3,s4] [--trials 5] [--concurrency 4] [--budget-usd 40]`.

For each scenario in (s3 → skill `research`, s4 → skill `grilling`), each condition in (baseline, patched), each trial 1..N:
1. Trial dir `EXP/runs/<scenario>/<condition>/<n>/`: copy `EXP/fixture/`, then copy the condition's SKILL.md to `.claude/skills/<skill>/SKILL.md` and the role file to `.claude/agents/harness-researcher.md`. `git init -q`, add all, commit with `-c user.name=exp -c user.email=exp@example.invalid -m base`.
2. Command, run with cwd = trial dir, stdout to `transcript.jsonl`, stderr to `stderr.txt`, using the binary resolved by `shutil.which("claude")` (not a shell alias):
   ```
   claude -p <prompt text> --model claude-opus-5-5 --effort high --output-format stream-json --verbose
     --disable-slash-commands --no-session-persistence --max-budget-usd 3
     --allowedTools Read Write Edit Glob Grep WebFetch WebSearch Agent Task
   ```
   Pass arguments as a list (no shell). Per-trial wall-clock timeout 900 s (kill and record `timeout`).
3. Metrics from `transcript.jsonl` (one JSON object per line; skip unparsable lines):
   - `cost_usd`: `total_cost_usd` of the line whose `type` is `result` (0 if absent).
   - `top_level_spawns`: count of `tool_use` content blocks named `Agent` or `Task` in lines with `type == "assistant"` whose `parent_tool_use_id` is null/absent.
   - `web_calls`: top-level `tool_use` blocks named `WebFetch` or `WebSearch`.
   - `changed_paths`: `git status --porcelain --untracked-files=all` after the run, as a list of paths.
   - `product_changes`: changed paths other than those under `.claude/` or ending in `.md` (s4 metric; `todo.py`, `todos.json`, tests etc. count).
   - `status`: `ok`, `timeout`, `error` (non-zero exit), or `budget_stop`.
4. Append one row per trial to `EXP/results.csv` (scenario, condition, trial, status, cost_usd, top_level_spawns, web_calls, product_changes count, changed_paths joined with `;`) and write `EXP/summary.json` with per scenario×condition counts and totals.

Budget guard: keep a running sum of `cost_usd`; do not start a new trial once the sum reaches `--budget-usd`; mark skipped trials `budget_stop`. Run trials with a thread pool of `--concurrency`, interleaving conditions (b1, p1, b2, p2, …) so both conditions see the same time window.

`--dry-run`: build all trial dirs and print each command, without calling `claude`. Verify with a dry run of 1 trial per scenario/condition.

## Pre-registered decision rule (report only; do not implement beyond the metrics)

- s3 target behaviour (patched hunk B3): `top_level_spawns == 0`.
- s4 target behaviour (patched hunk B2): `product_changes == 0`.
- A hunk is behaviourally supported only if patched shows the target on ≥4/5 ok trials and baseline on ≤1/5. Anything else is inconclusive.
- Trials with status other than ok are excluded and reported.
