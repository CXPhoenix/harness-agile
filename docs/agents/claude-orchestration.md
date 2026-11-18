# Claude model orchestration

Claude Code's mapping of the three tiers in [orchestration.md](orchestration.md):
the main session decides, the executor applies approved changes and runs checks,
the verifier challenges from evidence. Codex has its own settings in
[codex.md](codex.md); nothing here applies to it.

| Role | Tier | Where | Model | Used for |
|---|---|---|---|---|
| Main session | decider | the conversation | the user's selection | understanding, planning, decisions, synthesis, user communication, commits; loads the project skills |
| `harness-executor` | executor | `.claude/agents/` | executor setting from `/setup-roles` (template default `inherit`) | applying an approved, fully specified change and running every command whose output a gate or a verifier judges |
| `harness-reviewer` | verifier | `.claude/agents/` | verifier setting from `/setup-roles`, shared with the challenger (template default `inherit`) | red teaming: spec-review axes (stage 3), code-review axes (stage 6), security candidate and false-positive passes (stage 7) |
| `harness-challenger` | verifier | `.claude/agents/` | same verifier setting | devil's advocacy, alternative analysis and reasoning checks on plans, decisions and findings |
| `harness-researcher` | decider extension | `.claude/agents/` | `inherit`, always | primary-source research that feeds the main session |

When choosing settings in `/setup-roles`: a verifier on a different model from the
main session adds diversity between author and critic, and reviewer quality bounds
stages 3, 6 and 7. Revisit the choice with evidence from real runs.

## Delegating

- **Verifiers.** Use `harness-reviewer` where a stage prescribes independent review.
  Use `harness-challenger` when a plan or decision is expensive to reverse, or when
  the user asks for devil's advocacy. Resolve small questions in the main session.
- **Stage 3 stays four axes.** The challenger is not a fifth reviewer and does not
  arbitrate. Review disagreements go to the user with both positions and their
  evidence, as [review.md](review.md) requires.
- **Findings reach the user unfiltered.** Verifiers report every finding with
  confidence and severity. The main session may deduplicate, rank and annotate
  them, but it shows the user any finding it proposes to drop, so no P0 can
  disappear before the gate.
- **Executor.** Hand over a change once its scope is decided and large enough that
  a separate context pays for itself. The executor runs every command whose output
  a gate or a verifier judges and returns raw output for judgement
  ([orchestration.md](orchestration.md#verification-hand-off)). The main session may
  still make a trivial edit, with the quick checks that edit needs, when delegating
  would cost more. The executor cannot load skills: when the work falls under a
  skill (for example the `/tdd` loop required by hard rule 2), put that skill's
  steps and gates into the handoff, and the executor runs the loop's red and green
  tests. Commits stay with the main session and the commit skill.
- **Nesting.** Verifiers and the executor do not start subagents.

## Writing for the reader

The roles here have no Skill tool and no preloaded skills, so skill text reaches
them only when the main session copies it into a handoff. Tune `.claude/skills/`
for the main session's model (recorded as `runtime_trees.claude_tuned_for` in
`skill-sources.json`), and run `/tune-skills` when that model changes; adopters
of this template should do the same for their own model. Keep
model names out of skill text; model-specific guidance belongs in this file.
The verifier and executor models read their role files in `.claude/agents/`, the
documents those files tell them to read, and the handoff; write a handoff for
its reader, for example stating scope explicitly when it goes to the executor.
Official prompting pages:

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

`/setup-roles`, run by the user, changes the executor or verifier model and effort
and writes the `roles.claude` record. It sets each role's `model:` frontmatter (an
alias, a full model ID or `inherit`) and `effort:` frontmatter; a role without
`effort:` inherits the session's effort when it runs on the session's model. After
changing, adding or renaming a role, start a new session and confirm it in
`/agents`: a running session may not see the new role files. If an account lacks a
pinned model or the model is retired, offer `/setup-roles` again for a current model
or `inherit`. Version, override and effort pitfalls:
[orchestration.md](orchestration.md#fallbacks).
