---
name: init-template
description: Initialize a new product copy of harness-agile-template when the user requests adoption or initialization. Template inspection and maintenance do not trigger initialization.
---

# Initialise the template

This repository is an uninitialised copy of harness-agile-template while `{{PROJECT_NAME}}` is still
present in `AGENTS.md`. Initialize only when the user requests a new project from the template. Template maintenance and inspection keep these tokens intact.

## 1. Confirm it needs initialising

Read `AGENTS.md` and inspect its Project Charter for the literal project-name
token. Check the charter itself, not this skill or other files documenting tokens.
If the charter is already filled, stop without deleting template files.

## 2. Ask the user for two things

- **Project name** — how a person refers to it. Not the directory name.
- **One-liner** — one sentence saying what the project does. This is not the Charter; it is the
  single line that sits above it.

Use values already supplied by the user; ask together only for missing values and wait.
Keep the human-readable name distinct from the directory name.

## 3. Run the script from the repository root

```bash
python3 scripts/init-project.py --dry-run --name "<name>" --one-liner "<one sentence>"
```

Read the plan, then drop `--dry-run` to apply it. `--skill-mode copy` avoids symlinks;
the default `auto` uses relative symlinks with a verified-copy fallback. For flattened
Git links, run `python3 scripts/sync-skills.py` before structural verification.
The script fills the three tokens, strips the
template banner from `AGENTS.md`, and removes `.tmpl.docs/`, its marked README entry,
the initializer, creator packaging and template tests, and both this shared skill directory and its Claude
entry. It writes a product README and synchronizes remaining skills.
`--keep-template-files` preserves template files and the original README; historical
tokens inside `.tmpl.docs/` are always left untouched. It exits non-zero and names
the files if any project token survives.

`--date YYYY-MM-DD` overrides the ADR adoption date, which defaults to today. The three shipped ADRs
are dated when this project adopts them, not when they were first written.

## 4. Hand over

Report what changed, then give the user the one next step: **use `grill-with-docs` (`/grill-with-docs` in Claude Code, `$grill-with-docs` in Codex) to write the
Project Charter.** Until that section of `AGENTS.md` is written, its gate blocks specs, tickets, and
implementation code — the walking skeleton is the only work it permits.

Two things worth telling the user in the same breath, because both are cheap now and awkward later:

- **`git remote`** — with a remote, pipeline stage 9 lands work through PRs; without one it falls
  back to `git merge --no-ff`. `git remote -v` says which mode this clone is in.
- **Vendored skills** — `.claude/skills/i-have-adhd` and `.claude/skills/agent-browser` shipped with
  the template and may be behind their upstream. Their provenance is recorded in `docs/agents/skill-sources.json`;
  external CLIs still need their own installation.
