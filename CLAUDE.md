# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

<!-- TEMPLATE: while {{PROJECT_NAME}} is still an unfilled token, this repository is an
     uninitialised copy of harness-agile-template. Run `/init-template` before anything else. -->

## Project Charter

**{{PROJECT_NAME}}** — {{PROJECT_ONE_LINER}}

<!-- PLACEHOLDER — the user has not written this yet. -->

_What this project is for, who it serves, and what it must do._

**Gate:** while this section is a placeholder, the only permitted work is the walking skeleton
(below) and the conversation that defines it. Before writing a spec, opening a ticket, or writing
implementation code, ask the user to run `/grill-with-docs` and fill this section in.

## Delivery model

Work ships as **epics**. One epic = one spec = one pass through the pipeline = one demoable
increment. Finish an epic, then return to stage 1 for the next one.

Round 0 is the **walking skeleton**: the thinnest path that runs end to end, built so that real
**seams** exist. It carries no spec and no adversarial review, because both take seams as input and
a new repository has none yet. That exemption expires the moment the skeleton merges to `main`;
every ticket after that has a spec behind it.
See [ADR-0001](docs/adr/0001-walking-skeleton-then-epic-loop.md).

## Pipeline

| # | Stage | Skill | Gate before moving on |
|---|---|---|---|
| 1 | Converge the requirement | `/grill-with-docs` | user confirms shared understanding |
| 2 | Write the spec | `/to-spec` | spec **and** traceability matrix exist |
| 3 | Adversarial review | 4 subagents, ≤2 rounds | zero P0 findings |
| 4 | Break into tickets | `/to-tickets` | user approves the breakdown |
| 5 | Implement | `/implement` + `/tdd` | test plan table approved, then red → green |
| 6 | Review the change | `/code-review` | direction and requirement confirmed |
| 7 | Security review | `/security-review` | findings triaged and resolved |
| 8 | End-to-end | see workflow doc | behaviour verified against the real surface |
| 9 | Land it | PR, or `--no-ff` merge with no remote | on `main` |

Stage detail, gates, exceptions, and the epic close-out: **[docs/agents/workflow.md](docs/agents/workflow.md)**.

`/to-spec` and `/to-tickets` ask for a tracker configuration and fall back to `.scratch/` paths
without one. **[docs/agents/issue-tracker.md](docs/agents/issue-tracker.md) is that configuration** —
read it before either skill writes a file.

## Hard rules

1. **One branch per ticket:** `tickets/<ticket-id>/<ticket-slug>` (e.g. `tickets/T-0007/session-store`).
   Ticket ids are global, sequential, and permanent — branch names depend on them never changing.
2. **Two tables gate a ticket's tests.** A **test plan table** before the first test is written, which
   the user approves; a **coverage report table** when the ticket closes. Between them, `/tdd` governs
   the loop: one seam, one test, one minimal implementation per cycle.
3. **Adversarial review runs a frozen prompt.** Round 2 replays round 1's prompt verbatim; only the
   spec version changes. Two rounds is the ceiling. P0 findings surviving round 2 mean the epic is
   too large: split it and restart at stage 1.
4. **Verify against the surface that actually runs the behaviour.** `/agent-browser` drives
   Chrome/Chromium and Electron over CDP, so it verifies browser-reachable surfaces only. Any other
   surface — a native client, a daemon, a CLI, a game server — needs a harness this project supplies.
   State which surface a verification covers whenever you report one.
5. **Skills own their output.** Commits use `/tw-emoji-commit`, PR descriptions use
   `/tw-emoji-pr-note`, release notes use `/tw-emoji-release-note`. If one is unavailable, stop and
   report rather than writing the text yourself.

## Repository layout

```
.proj.specs/
  OPEN-QUESTIONS.md               deferred architecture-level decisions
  NNNN-<epic-slug>/
    spec.en.md                    source of truth
    spec.zh-TW.md                 audit translation for the user
    traceability.md               {type x field x boundary} -> acceptance criteria
    review/prompt.md              the frozen adversarial-review prompt
    review/round-N.md             findings, graded P0 / P1 / P2
    reports/*.html                standalone evidence reports
  _reports/*.html                 project-level reports
.proj.tickets/
  NNNN-<epic-slug>/
    T-NNNN-<slug>.md              status lives in frontmatter, not in the path
docs/adr/                         architecture decisions
docs/agents/                      the docs this file points at
```

Both `.proj.specs/` and `.proj.tickets/` are committed: they are the evidence chain behind every
review and every deferral.

## Build and test commands

No build tooling exists yet — the repository holds no source code. The walking skeleton establishes
the toolchain; fill this section in when it lands, and keep it to the commands an agent cannot
discover from `package.json`, `Makefile`, or `--help`.

## Reference

- **[docs/agents/workflow.md](docs/agents/workflow.md)** — the nine stages in full: entry conditions, gates, the walking-skeleton exemption, epic close-out, branching and landing.
- **[docs/agents/issue-tracker.md](docs/agents/issue-tracker.md)** — where specs and tickets live, ticket frontmatter, the six status views, how blocking is derived.
- **[docs/agents/review.md](docs/agents/review.md)** — the four adversarial-review axes, P0/P1/P2 grading, and the two-stage security review.
- **[docs/agents/language.md](docs/agents/language.md)** — which documents are English, which are Traditional Chinese, and how the bilingual spec stays in sync.
- **[docs/agents/domain.md](docs/agents/domain.md)** — how to consume `CONTEXT.md` and ADRs while exploring.
