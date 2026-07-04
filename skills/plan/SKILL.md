---
name: plan
description: "Create durable implementation plans that can be handed off for execution. Orchestrates a deterministic pipeline of micro-skills: Scope -> Research -> Design -> Generate -> Tasks. No agent dependency, no fallback paths."
title: Plan
type: Skill
version: 1.2
timestamp: "2026-07-04"
user-invocable: true
disable-model-invocation: true
---

# Plan

Orchestrates a deterministic pipeline of micro-skills: `Scope -> Research -> Design -> Generate -> Tasks`. No agent dependency, no fallback paths.

## Interaction Method

- Use the platform's `ask_user_question` extension for all user-facing decisions; ask one question at a time.
- If input is empty, ask: "What would you like to plan? Describe the task or project."

Before starting the workflow, ask the user to choose an interaction mode:

- **Detailed** — Confirm at each phase transition; inspect artifacts; maximum control. Best for complex/unfamiliar work.
- **Autopilot** — All phases run automatically; only final outcome reported. Fastest. Best for straightforward work.
- **Smart** — Phases run automatically; pause only on HIGH-risk operations.

Store in the context object:

```yaml
interactionMode: detailed | smart | autopilot
```

**Propagation:** `interactionMode` flows into `research`, `design`, and `generate` artifacts; each downstream phase reads it to adjust confirmation behaviour (detailed = pause every transition; autopilot = run all; smart = pause only on HIGH-risk).

## Orchestration Implementation

Each phase runs sequentially: the orchestrator calls the module, receives the output artifact, validates it with a quality gate, and passes it to the next phase.

### INPUT

- Receives a context object (task description, goals, constraints, references, previous plans) from the user, a saved prompt, a document, or a combination.
- **If no context is provided**, ask: "What would you like to plan? Describe the task or project."
- Output: [User Input Artifact](references/templates/artifacts/user-input.md)

### Phases

| Phase | Module                                 | Output Artifact                                                                    |
| ----- | -------------------------------------- | ---------------------------------------------------------------------------------- |
| 1     | [Scope](modules/scope.md)              | [Scoped context](references/templates/artifacts/scoped-context.md)                 |
| 2     | [Research](modules/research.md)        | [Research findings](references/templates/artifacts/research-findings.md)           |
| 3     | [Design](modules/design.md)            | [Design with unit decomposition](references/templates/artifacts/design.md)         |
| 4     | [Generate](modules/generate.md)        | [Final plan](references/templates/artifacts/final-plan.md) saved to `docs/plans/`  |
| 5     | [Tasks](modules/tasks.md) _(optional)_ | [Task list](references/templates/artifacts/task.md) saved to `docs/tasks/PLAN_ID/` |

**Phase 5** is optional; ask the user before continuing even in Autopilot mode (they may prefer to slice tasks manually).

### Quality Gates

Between phases, the orchestrator validates the output artifact before passing it to the next phase:

1. **Schema validation** — required fields present and well-formed (see [error-handling.md](references/error-handling.md) for the per-type field list).
2. **Cross-phase consistency** — IDs (`scope-id`, `research-id`, `design-id`, `plan-id`) match the upstream artifacts; `interactionMode` is identical across artifacts.
3. **Status check** — the artifact's `status` is `complete` (not `pending` or `failed`).
4. **Tier/complexity coherence** (after Design) — the `tier_recommendation` is consistent with `complexity` and `risk_level` per [plan-tier-selection.md](references/plan-tier-selection.md).

If a gate fails, the orchestrator returns to the producing phase with the error context (per the recovery workflow in [error-handling.md](references/error-handling.md)).

### FINAL OUTPUT

- Plan file saved to `docs/plans/YYYY-MM-DD-NNN-<kebab-case-name>.md` and registered in `docs/plans/index.md`.
- (Optional) Task files saved to `docs/tasks/<plan-id>/` and registered in `docs/tasks/index.md`, ready for the Work skill.

## References

The orchestrator and modules share these reference files:

| Reference                                                                     | Used By                          |
| ----------------------------------------------------------------------------- | -------------------------------- |
| [error-handling.md](references/error-handling.md)                             | All phases (Step 0 verification) |
| [interaction-mode-propagation.md](references/interaction-mode-propagation.md) | All phases (Step N confirmation) |
| [learnings-gate-logic.md](references/learnings-gate-logic.md)                 | Scope (Step 4)                   |
| [high-risk-detection.md](references/high-risk-detection.md)                   | Research (Step 2)                |
| [external-research-guidance.md](references/external-research-guidance.md)     | Research (Step 4)                |
| [design-complexity-assessment.md](references/design-complexity-assessment.md) | Design (Step 4)                  |
| [plan-tier-selection.md](references/plan-tier-selection.md)                   | Generate (Step 1)                |
| [task-slicing-rules.md](references/task-slicing-rules.md)                     | Tasks (Steps 2–3)                |

Artifact templates live in [references/templates/artifacts/](references/templates/artifacts/).

## Core Principles

- **Deterministic Pipeline:** Phases always execute in sequence (no agent switching, no fallback paths).
- **Error Handling:** Fail explicitly, not silently; each phase has clear error handling with recovery suggestions.
- **Focus on Decisions:** Capture approach, structure, risks, and sequencing (not code simulation).
- **Right-Size:** Small tasks → short plans; complex work → more structure.
- **Separate Planning from Execution:** NEVER simulate implementation during planning.
- **Be Concrete:** Use specific files, components, and dependencies.
- **Stay Portable:** Use repository-relative paths only.
- **Transparent Artifacts:** Each phase produces an explicit output artifact for the next phase.
- **Interaction Mode Propagation:** `interactionMode` is read at the start of each subsequent phase and determines whether confirmation steps execute.
