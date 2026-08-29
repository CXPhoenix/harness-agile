# Review

Two review mechanisms with different scopes: adversarial review reads the **spec** before any code
exists (pipeline stage 3); security review reads the **code** after it does (stage 7, plus a
chain analysis at epic close-out).

## Adversarial review

Four Opus subagents, one per axis, at most two rounds.

### The four axes

Each subagent gets exactly one axis. Fixed axes are what make the review reproducible across rounds
— a reviewer told to "find problems" applies a different standard every time it runs.

1. **Completeness.** Does `traceability.md` have holes? Every `{type × field × boundary}` combination
   must reach an acceptance criterion. Report each combination that does not.
2. **Verifiability.** Can each acceptance criterion be judged pass or fail without interpretation?
   Words like "appropriately", "reasonably", "as needed", "where possible" make a criterion
   unjudgeable: grade those P0.
3. **Contract conflict.** Does the spec contradict `CONTEXT.md` vocabulary, an existing ADR, or an
   established seam? Name the conflicting document and line. A spec that overrides an ADR is
   allowed, but it must say so explicitly rather than silently.
4. **Red team.** Once this spec is built, what behaviour or attack surface exists that the spec did
   not intend? Distinguish intended consequences from accidental ones.

### Grading

| Grade | Meaning | Effect |
|---|---|---|
| **P0** | The spec cannot be implemented correctly as written | Blocks ticket creation |
| **P1** | Real problem, resolvable inside a ticket | Tickets may open; the ticket carries the finding |
| **P2** | Worth recording | Recorded, blocks nothing |

### The frozen prompt

Write the reviewer prompt to `.proj.specs/<epic>/review/prompt.md` before round 1. Round 2 replays
that file verbatim; only the spec version it points at changes.

This is the mechanism that keeps the ruler still. Without it a second round applies a stricter
standard than the first, and a review that would have converged reports fresh findings indefinitely
— the failure is in the moving threshold, not in the spec.

### Two rounds, then split

Two rounds is the ceiling. P0 findings surviving round 2 mean the epic's surface is too large to
converge on, so split the epic and restart at pipeline stage 1.

Watch the reverse failure too: revisions that add new specification surface must be self-checked
before round 2, or the review is chasing a target that moves as fast as it advances. Before adding
any rule or acceptance criterion mid-review, check it against the existing ones for mutual
exclusion — a guarantee added to close one hole routinely opens another.

### Adjudication

Reviewers will disagree. The **user** adjudicates. Do not resolve a disagreement by majority vote
among subagents, and do not have a fifth agent arbitrate: present both positions and their evidence,
then wait.

## Security review

### Stage 7: per-ticket, diff-scoped

Run `/security-review` on the branch diff, then fix what it finds.

If this project's domain makes some findings expected rather than defects — a security-training
range, a deliberately vulnerable fixture, a red-team target — define that distinction here before
the first security review runs, and record it as an ADR. Without a written rule, every intentional
finding blocks its own ticket.

### Epic close-out: chain analysis

`/security-review` reads pending changes on the current branch, so it cannot see a chain that spans
tickets. Run a separate analysis after the epic's last ticket lands.

**Input:** every finding from the epic's tickets, whatever their grade, plus the trust boundaries the
spec describes.

**Question:** can defects that are individually low-severity be composed into a chain that crosses a
trust boundary?

**Output:** written to `.proj.specs/<epic>/review/chain-analysis.md`. A chain that crosses a trust
boundary opens a ticket before the epic is called done.
