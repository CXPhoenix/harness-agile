# Workflow

The nine stages of the delivery pipeline, in order. `CLAUDE.md` carries the summary table and the
hard rules; this file carries the entry conditions, gates, and exceptions.

The unit of work is the **epic**: one spec, one pass through stages 1–9, one demoable increment.
Agile principle 7 is the yardstick — working software is the measure of progress, so every epic ends
with something that runs, not with a document.

## Round 0: the walking skeleton

A **walking skeleton** is the thinnest path that runs end to end. Every layer is the worst possible
version of itself, and every layer is genuinely connected — no mocks, no TODOs, no architecture
diagram standing in for a running process.

It exists to make **seams** real. `/to-spec` requires you to sketch the seams a feature will be
tested at, preferring existing seams; in an empty repository there are none to prefer, so a spec
written first can only describe imagined seams. The skeleton produces the real ones.

**The exemption:** round 0 skips stage 2 (spec) and stage 3 (adversarial review).

**Its expiry:** the exemption ends when the skeleton merges to `main`. From that merge onward every
ticket has a spec behind it. The merge is the terminating ritual, which is why the skeleton still
takes a branch — `tickets/T-0000/walking-skeleton` — rather than committing straight to `main`.

**Its output is the seams, not the code.** Expect most of the skeleton's implementation to be
replaced by the epics that follow. That is the plan working, not the plan failing.

## Stage 1 — Converge the requirement

Run `/grill-with-docs`. It is user-invoked; ask the user to run it rather than trying to invoke it
yourself.

Grilling produces decisions. When a decision is hard to reverse, surprising without context, and the
result of a real trade-off, record it as an ADR (`docs/adr/`) as it settles rather than batching them
at the end.

**Gate:** the user confirms shared understanding. Not "the agent stopped asking questions."

## Stage 2 — Write the spec

Run `/to-spec`. It publishes to `.proj.specs/NNNN-<epic-slug>/spec.en.md`.

Alongside the spec, write `traceability.md`: a single table mapping
`{type × field × boundary} → {expected behaviour → acceptance criterion}`. The spec's prose is
derived from this matrix, so a gap in the matrix is a gap in the spec. This is the single source of
truth that stops the "fix A, miss B" class of revision failure.

**Gate:** spec and traceability matrix both exist, and every row of the matrix reaches an acceptance
criterion.

## Stage 3 — Adversarial review

Four Opus subagents, four fixed axes, at most two rounds. Axes, grading, and the frozen-prompt
mechanism live in [review.md](review.md).

**Gate:** zero P0 findings.

**Escalation:** P0 findings surviving round 2 are a signal that the epic is too large, not a reason
to open round 3. Split the epic and restart at stage 1. Adding rounds is how a review stops
converging — the ruler drifts upward and "not converged" becomes an artefact of the moving
threshold rather than a property of the spec.

## Stage 4 — Break into tickets

Run `/to-tickets`. Tickets are **tracer bullets**: each one cuts a narrow but complete path through
every layer and is demoable on its own.

Ticket ids are allocated globally and sequentially (`T-0001`, `T-0002`, …) and never change, because
branch names embed them. Files live under `.proj.tickets/NNNN-<epic-slug>/`. Layout and frontmatter:
[issue-tracker.md](issue-tracker.md).

**Gate:** the user approves the breakdown — granularity, blocking edges, and what each ticket
delivers.

## Stage 5 — Implement

Branch first: `tickets/<ticket-id>/<ticket-slug>`.

Run `/implement`, which uses `/tdd`. Two tables bracket the loop:

**Before the first test — the test plan table.** The user approves it before any test is written.
This satisfies `/tdd`'s rule that no test is written at an unconfirmed seam.

| Seam | Test intent | Scope | Acceptance criterion | Boundary conditions |
|---|---|---|---|---|

**Between the tables — the red → green loop, governed by `/tdd`.** One seam, one failing test, one
minimal implementation, repeat. Writing every test up front is the horizontal-slicing anti-pattern:
bulk tests verify imagined behaviour. Coverage is not a meaningful number here, because the code
under test does not exist yet.

**When the ticket closes — the coverage report table.** Now the numbers are real.

| Seam | Tests | Measured coverage | Acceptance criterion | Uncovered, and why |
|---|---|---|---|---|

**Gate:** test plan table approved before the loop starts; coverage report table produced before
stage 6.

## Stage 6 — Review the change

Run `/code-review`. It reviews on two axes: does the code follow this repo's documented standards,
and does it match what the spec asked for. Direction and requirement are what matter here;
`/simplify` handles quality-only cleanups separately.

## Stage 7 — Security review

Run `/security-review` on the diff. The cross-cutting chain analysis is not part of this stage; it
runs at epic close-out. See [review.md](review.md).

## Stage 8 — End-to-end

Verify the behaviour against the surface that actually runs it.

- **Browser-reachable surface:** use `/agent-browser`. `/chrome-devtools-mcp:a11y-debugging` covers
  accessibility; if that MCP server is absent from a clone, ask the user to install it.
- **Any other surface** — a native client, a daemon, a CLI, a game server, a device: use a harness
  this project supplies. `/agent-browser` drives Chrome/Chromium and Electron over CDP, so anything
  outside that is outside its reach.

Report which surface a verification covered. A browser screenshot is evidence about a browser
surface, and saying so keeps it from being read as evidence about anything else.

Record the choice of non-browser harness as an ADR once it is made; until then it belongs in
`.proj.specs/OPEN-QUESTIONS.md`.

## Stage 9 — Land it

With a git remote: `gh pr create`, description from `/tw-emoji-pr-note`.

Without a remote: `git merge --no-ff` into `main`, with the `/tw-emoji-pr-note` output as the merge
commit message. Check with `git remote -v` rather than assuming.

## Epic close-out

After the last ticket of an epic lands:

1. **Vulnerability chain analysis.** Input: every security finding from the epic's tickets, plus the
   trust boundaries the spec describes. Question: can individually low-severity defects be composed
   into a chain? This is epic-scoped rather than ticket-scoped because a chain by definition spans
   units.
2. **Evidence report.** Run `/evidence-report` to produce a standalone HTML report of what the epic
   delivered and what the evidence for it is.
3. **Retrospective.** Agile principle 12 — what to change about how the next epic runs. Decisions
   worth keeping become ADRs; questions not yet answerable go to `.proj.specs/OPEN-QUESTIONS.md`.

## Deferred decisions

Two different things, kept apart:

- A **ticket with `status: pending`** exists and is deliberately paused. It lives in
  `.proj.tickets/` with its reason and evidence in frontmatter.
- An **open question** is not yet a ticket: an architecture-level decision that blocks work
  downstream of it. It lives in `.proj.specs/OPEN-QUESTIONS.md`.

Both record why they were deferred, the evidence behind that call, and the condition that should
bring them back.
