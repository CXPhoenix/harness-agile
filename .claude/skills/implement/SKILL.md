---
name: implement
description: "Implement a piece of work based on a spec or set of tickets."
disable-model-invocation: true
---

If the user passes a ticket id or path, read it as `docs/agents/issue-tracker.md`
describes for fetching the relevant ticket and state its title before starting.
If the reference is ambiguous, ask.

Implement the approved spec or tickets on the branch required by AGENTS.md.
Use the existing approved test plan and seams; obtain approval only for missing or
materially changed ones before writing tests.

Call the Skill tool with "tdd" at those seams: one failing test, one minimal
implementation, then the next behavior. Continue until the approved acceptance
criteria are covered.

Run affected tests during the loop and the project's required checks at completion,
including the full existing test suite once. Run typechecking when the project has
it configured; do not add a toolchain merely to satisfy this instruction. After a
failure or further edit, rerun affected checks. Record the coverage report table
required by workflow.md, including unmeasured or uncovered areas.

Call the Skill tool with "code-review" on the actual change, including staged,
unstaged and relevant untracked files before committing. Resolve findings within the
approved scope; raise material scope changes. Follow workflow.md for security and
end-to-end gates.

For the workflow's commit, load the project /tw-emoji-commit skill and use its
sanitized UTF-8 message file. A commit is not evidence that later gates or landing
are complete. Report the completed deliverable, checks and remaining gates.
