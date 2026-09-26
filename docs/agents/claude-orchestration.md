# Claude model orchestration

This project assigns Claude models by role. The main session decides; critics on
other models challenge; an executor applies approved changes. Codex has its own
settings in [codex.md](codex.md); nothing here applies to it.

| Role | Where | Model | Used for |
|---|---|---|---|
| Main session | the conversation | the user's selection (usually Claude Opus 5.5) | understanding, planning, decisions, synthesis, user communication; loads the project skills |
| `harness-reviewer` | `.claude/agents/` | `claude-opus-5` | red teaming: spec-review axes (stage 3), code-review axes (stage 6), security candidate and false-positive passes (stage 7) |
| `harness-challenger` | `.claude/agents/` | `claude-opus-4-8` | devil's advocacy, alternative analysis and reasoning checks on plans, decisions and findings |
| `harness-executor` | `.claude/agents/` | `claude-sonnet-5` | applying an approved, fully specified change and running the named checks |
| `harness-researcher` | `.claude/agents/` | inherit | primary-source research that feeds the main session |

This split is the user's choice for this project. It has not been measured
against alternatives here; revisit it with evidence from real runs.

## Delegating

- **Critics.** Use `harness-reviewer` where a stage prescribes independent review.
  Use `harness-challenger` when a plan or decision is expensive to reverse, or when
  the user asks for devil's advocacy. Resolve small questions in the main session.
- **Stage 3 stays four axes.** The challenger is not a fifth reviewer and does not
  arbitrate. Review disagreements go to the user with both positions and their
  evidence, as [review.md](review.md) requires.
- **Findings reach the user unfiltered.** Critics report every finding with
  confidence and severity. The main session may deduplicate, rank and annotate
  them, but it shows the user any finding it proposes to drop, so no P0 can
  disappear before the gate.
- **Executor.** Hand over a change once its scope is decided and large enough that
  a separate context pays for itself; the main session may apply small edits
  directly. The executor cannot load skills: when the work falls under a skill
  (for example the `/tdd` loop required by hard rule 2), put that skill's steps
  and gates into the handoff. Commits stay with the main session and the commit
  skill.
- **Nesting.** Critics and the executor do not start subagents.

## Writing for the reader

Subagents do not load project skills. Skill text is read by the main session, so
tune `.claude/skills/` for the user's session model. The critic and executor
models read their role files in `.claude/agents/`, the documents those files tell
them to read, and the handoff the main session writes; tune those for the role's
model. Official prompting pages:

- Claude Opus 5.5: <https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5-5>
- Claude Opus 5: <https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5>
- Claude Opus 4.8: <https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-4-8>
- Claude Sonnet 5: <https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-sonnet-5>
- All current models: <https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices>

The differences that most often change the text:

- **Findings stages:** ask for every finding with confidence and severity, and
  say the stage is about coverage. Opus 5, Opus 4.8 and Sonnet 5 apply "only
  report high-severity" or "be conservative" literally and report less.
- **Literal readers** (Opus 4.8, Sonnet 5): state scope explicitly ("every
  section, not just the first"); they do not generalize an instruction.
- **Verification:** Opus 5 verifies its own work unprompted, so skip
  "double-check" steps in text it reads. The Opus 5.5 page treats Opus 5
  patterns as a starting point, so test the same removal there.
- **Frontend direction:** for Opus 5.5, name the default styles to avoid. For
  Opus 4.8 and Sonnet 5, give a concrete alternative spec or ask for several
  directions for the user to choose from.
- **Delegation** matters only for a model that can delegate. The main session
  on Opus 5 delegates readily and needs damping; on Opus 4.8 it delegates rarely.

## Changing the assignment

Model IDs live in each role's `model:` frontmatter; Claude Code accepts an alias,
a full model ID or `inherit`. After adding or renaming a role, start a new
session and confirm it in `/agents`: a running session may not see new role
files. If an account lacks a pinned model, or the model is retired, set that role
to `inherit` or a current model and update the table above. Effort for the
pinned roles follows Claude Code's defaults; this project has not set it.
