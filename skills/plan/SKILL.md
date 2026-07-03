---
name: plan
description: Create durable implementation plans that can be handed off for execution. Orchestrates a deterministic pipeline of micro-skills: Scope -> Research -> Design -> Generate -> Tasks. No agent dependency, no fallback paths.
title: Plan
type: Skill
version: 1.0
timestamp: "2026-07-01"
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

### FINAL OUTPUT

Plan file ready for execution.

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
