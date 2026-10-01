---
name: plan
description: "Create durable implementation plans that can be handed off for execution. Orchestrates a deterministic pipeline of micro-skills: Scope -> Research -> Design -> Generate -> Tasks. No agent dependency, no fallback paths."
disable-model-invocation: true
---

# Plan

Orchestrates a deterministic pipeline of micro-skills: `Scope -> Research -> Design -> Generate -> Tasks`. No agent dependency, no fallback paths.

## Skill Invocation

This skill is invoked by prompting `/plan [--deep] <task description>`. This skill will run the planning pipeline, producing a final plan artifact and optionally a set of task artifacts, acting as the Orchestrator.

**`--deep` flag (optional):** forces the **Deep** plan tier in any interaction mode, including Autopilot, bypassing the tier question and the complexity-based choice.

- **Parsing:** `--deep` counts only as a standalone token at the **start or end** of the input. Remove it from the task description, then set `force_deep: true` in the context object. Anywhere else (e.g., inside a sentence or quoted text) it is plain text and `force_deep` stays `false`.
- If nothing remains after removing the flag, ask: "What would you like to plan? Describe the task or project."
- The flag does not change the interaction-mode question, `complexity`, or `tier_recommended`; it only sets `tier: deep`. The override stays auditable (`tier_recommended` keeps the algorithm's result).
- Other `--word` tokens are not flags of this skill; leave them in the description.

## Interaction Method

- Ask the user one structured question at a time (2–4 concrete options) using the agent's interactive question capability; never hardcode a specific tool name.
- If input is empty, ask: "What would you like to plan? Describe the task or project."

Before starting the workflow, ask the user to choose an interaction mode:

- **Detailed** — Confirm at each phase transition; inspect artifacts; maximum control. Best for complex/unfamiliar work.
- **Autopilot** — All phases run automatically; only final outcome reported. Fastest. Best for straightforward work.
- **Smart** — Phases run automatically; pause only on HIGH-risk operations.

Store in the context object:

```yaml
interactionMode: detailed | smart | autopilot
force_deep: true | false   # true only when `--deep` was passed; default false
```

`force_deep` lives in the Orchestrator context (not in artifact files). Pass it to **Design** (to produce the material a Deep plan needs) and **Generate** (to select the tier).

**Artifact persistence:** intermediate phase artifacts are written to disk **only in `detailed` mode**. In `smart`/`autopilot` they are passed between phases in context and never written (see `references/interaction-mode-propagation.md#artifact-persistence`). Final deliverables are always written.

**Propagation:** `interactionMode` flows into `research`, `design`, and `generate` artifacts; each downstream phase reads it to adjust confirmation behaviour (detailed = pause every transition; autopilot = run all; smart = pause only on HIGH-risk).

## Orchestration Implementation

Each phase runs sequentially: the orchestrator calls the module, receives the output artifact, validates it with a quality gate, and passes it to the next phase.

### INPUT

- Receives a context object (task description, goals, constraints, references, previous plans) from the user, a saved prompt, a document, or a combination.
- **If no context is provided**, ask: "What would you like to plan? Describe the task or project."
- Output: [User Input Artifact](references/templates/artifacts/user-input.md)

### Pre-Flight Check

Before starting the planning pipeline, the orchestrator verifies that required folders exist:

- `docs/plans/` — must exist for saving final plan
- `docs/tasks/` — must exist if task generation is enabled
- `docs/plans/.scope/`, `.research/`, `.design/` — **`detailed` mode only**, for saving the intermediate phase artifacts; do not create them in `smart`/`autopilot`

**Self-Healing:** If missing, the orchestrator automatically creates these folders. This allows the plan skill to run even if `arreio-init` wasn't explicitly run.

### Phases

| Phase | Module                                 | Output Artifact                                                                    |
| ----- | -------------------------------------- | ---------------------------------------------------------------------------------- |
| 1     | [Scope](modules/scope.md)              | [Scoped context](references/templates/artifacts/scoped-context.md)                 |
| 2     | [Research](modules/research.md)        | [Research findings](references/templates/artifacts/research-findings.md)           |
| 3     | [Design](modules/design.md)            | [Design with unit decomposition](references/templates/artifacts/design.md)         |
| 4     | [Generate](modules/generate.md)        | [Final plan](references/templates/artifacts/final-plan.md) saved to `docs/plans/`  |
| 5     | [Tasks](modules/tasks.md) _(optional)_ | [Task list](references/templates/artifacts/task.md) saved to `docs/tasks/plan-id/` |

**Phase 5** is optional; ask the user 'Generate individual task files?' before running, even in Autopilot. If user declines, planning is complete.

### Quality Gates

Between phases, the orchestrator validates the output artifact before passing it to the next phase:

1. **Schema validation** — required fields present and well-formed (see [error-handling.md](references/error-handling.md) for the per-type field list).
2. **Cross-phase consistency** — IDs (`scope-id`, `research-id`, `design-id`, `plan-id`) match the upstream artifacts; `interactionMode` is identical across artifacts.
3. **Status check** — the artifact's `status` is `complete` (not `pending` or `failed`).
4. **Tier/complexity coherence** (after Design) — `tier_recommended` equals `recommend_tier(complexity, risk_level)` per [plan-tier-selection.md](references/plan-tier-selection.md). Recompute it; do not trust the value blindly. A `HIGH`/`VERY_HIGH` complexity must yield `deep`.

If a gate fails, the orchestrator returns to the producing phase with the error context (per the recovery workflow in [error-handling.md](references/error-handling.md)).

### Index Registration

Each skill module is responsible for registering its own outputs:

| Module   | Registers To                    | Artifact Format                                  |
| -------- | ------------------------------- | ------------------------------------------------ |
| Generate | `docs/plans/index.md`           | Link + brief summary to final plan file          |
| Tasks    | `docs/tasks/<plan-id>/index.md` | Folder creation + task links (created on-demand) |

**Who updates what:**

- **Generate phase:** Creates `docs/plans/index.md` if missing; inserts the new plan row (or replaces the row with the same `plan-id`)
- **Tasks phase:** Creates `docs/tasks/<plan-id>/` folder and `docs/tasks/<plan-id>/index.md` if missing; populates with task file links and metadata

### FINAL OUTPUT

- **Plan file:** Saved to `docs/plans/YYYY-MM-DD-NNN-<kebab-case-name>.md`
  - **Registration:** Generate phase inserts or replaces the row in `docs/plans/index.md` linking the new plan
- **Task files (optional):** Saved to `docs/tasks/<plan-id>/TASK-NNN-<kebab-case-name>.md`
  - **Registration:** Tasks phase creates `docs/tasks/<plan-id>/index.md` and registers task file links there
  - Ready for the Work skill to consume via `docs/tasks/<plan-id>/index.md`

## References

The orchestrator and modules share these reference files:

| Reference                                                                     | Used By                          |
| ----------------------------------------------------------------------------- | -------------------------------- |
| [error-handling.md](references/error-handling.md)                             | All phases (Step 0 verification) |
| [id-generation.md](references/id-generation.md)                             | Scope, Research, Design, Generate (ID assignment) |
| [interaction-mode-propagation.md](references/interaction-mode-propagation.md) | All phases (Step N confirmation) |
| [learnings-gate-logic.md](references/learnings-gate-logic.md)                 | Scope (Step 4)                   |
| [high-risk-detection.md](references/high-risk-detection.md)                   | Research (Step 2)                |
| [external-research-guidance.md](references/external-research-guidance.md)     | Research (Step 4)                |
| [design-complexity-assessment.md](references/design-complexity-assessment.md) | Design (Step 4)                  |
| [plan-tier-selection.md](references/plan-tier-selection.md)                   | Generate (Step 1)                |
| [task-slicing-rules.md](references/task-slicing-rules.md)                     | Tasks (Steps 2–3)                |

Artifact templates live in [references/templates/artifacts/](references/templates/artifacts/).

## Execution Rules

Follow these literally; they exist to keep runs consistent across agents.

1. **Run each module's steps in order**, starting with its Step 0 verification. Do not skip, merge, or reorder steps.
2. **Never invent values.** If a required input is missing, apply the recovery in [error-handling.md](references/error-handling.md) or ask the user; do not fill it with a plausible guess.
3. **Compute, don't copy.** Values defined by an algorithm (`complexity`, `tier_recommended`, `tier`) must be evaluated with the real inputs. Example values in references are illustrations, never defaults.
4. **One question at a time**, with 2–4 concrete options; build the question text from the current values.
5. **Announce phase transitions in one line** (e.g., "Phase 3/5 Design complete: complexity HIGH, tier_recommended deep") so the user can follow progress, even in Autopilot.
6. **Honor write rules:** hidden phase artifacts only in `detailed` mode; the final plan, index row, and (if accepted) task files always.

## Core Principles

- **Deterministic Pipeline:** Phases always execute in sequence (no agent switching, no fallback paths).
- **Error Handling:** Fail explicitly, not silently; each phase has clear error handling with recovery suggestions.
- **Focus on Decisions:** Capture approach, structure, risks, and sequencing (not code simulation).
- **Right-Size:** Small tasks → short plans; complex work → more structure.
- **Separate Planning from Execution:** NEVER simulate implementation during planning.
- **Be Concrete:** Use specific files, components, and dependencies.
- **Stay Portable:** Use repository-relative paths only.
- **Lean Persistence:** Phase artifacts hit disk only in `detailed` mode; `smart`/`autopilot` pass them in context to save tokens and time.
- **Transparent Artifacts:** Each phase produces an explicit output artifact for the next phase.
- **Interaction Mode Propagation:** `interactionMode` is read at the start of each subsequent phase and determines whether confirmation steps execute.
- **Single Source of Truth:** This skill defines all its own rules; it does not depend on any external agent rule file.
- **Behavior-Described, Tool-Agnostic:** Steps describe required capabilities ("search the codebase", "ask the user one question"), not specific tool names; each agent maps to its native tools.
- **Test-Driven Tasks:** One Acceptance Criterion per task; one test per AC; each task's Steps follow Red → Green → Refactor (write the failing test first and confirm it fails, implement the minimum code to pass, then refactor with the test green).
