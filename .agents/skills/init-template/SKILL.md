---
name: init-template
description: Initialise a fresh copy of harness-agile-template — collect the project name and one-liner, fill the placeholder tokens, and remove the template-only files. Use when AGENTS.md still contains {{PROJECT_NAME}}, when the user says the project is a new copy of the template, or when they ask to initialise or set up the template.
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

Ask for both in one turn and wait. Do not invent them from the directory name: the directory name is
what the user typed when cloning, and it is often not what they would call the project.

## 3. Run the script from the repository root

```bash
python3 scripts/init-project.py --dry-run --name "<name>" --one-liner "<one sentence>"
```

Read the plan, then drop `--dry-run` to apply it. The script fills the three tokens, strips the
template banner from `AGENTS.md`, and removes `.tmpl.docs/`, its marked README entry,
the initializer and its test, and both this shared skill directory and its Claude
link. `--keep-template-files` preserves these files and the README entry; historical
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
