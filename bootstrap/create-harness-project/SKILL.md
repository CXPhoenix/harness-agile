---
name: create-harness-project
description: Create a new local harness-agile project with Claude Code and Codex support.
disable-model-invocation: true
---

# Create a harness-agile project

Use the user's target, human-readable name and one-line description; ask only for
missing values. Read INSTALL.md from the approved version of
`https://github.com/CXPhoenix/harness-agile.git` using existing read access.
In the source checkout the guide is `../../INSTALL.md`; when this skill is installed
independently, retrieve the guide from an authenticated checkout instead.

Record the source commit. Follow that version's guide with explicit argv and
`--no-input`: inspect dry-run, create the authorized target, verify the generated
skills and report source, output directory and the Charter step. The package
generator owns file generation. Keep the source and global agent settings intact.
Nonempty targets require a separate adoption task.
