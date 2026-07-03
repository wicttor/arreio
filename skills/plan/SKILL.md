---
name: plan
description: Create durable implementation plans that can be handed off for execution. Orchestrates a deterministic pipeline of micro-skills: Scope -> Research -> Design -> Generate -> Tasks. No agent dependency, no fallback paths.
title: Plan
type: Skill
version: 1.0
timestamp: "2026-07-01"
---

# Plan

Create durable implementation plans that can be handed off for execution. Orchestrates a deterministic pipeline of micro-skills:

> Scope -> Research -> Design -> Generate -> Tasks

No agent dependency, no fallback paths.

## Interaction Method

- Use the platform's `ask_user_question` extension for all user-facing decisions.
- Ask one question at a time. Use follow-up questions to refine scope.
- Use multiple-choice questions when possible (e.g., "Is this a new feature, a bug fix, or a refactor?").
- If the input is empty, ask: "What would you like to plan? Describe the task or project."

## Select Interaction Mode

Before starting the **Core Workflow** below, ask the user to choose their engagement level.
Use the platform's `ask_user_question` extension (or equivalent to generate questions) to present the following three options:

> **Question:** "How would you like to proceed with this workflow?"
>
> **Options:**
>
> - **Detailed** — Review and confirm at each phase transition; inspect generated artifact before proceeding; maximum control. Best for complex work, unfamiliar codebases, and learning.
> - **Autopilot** — Every phase runs automatically; only the final outcome is reported. Fastest. Best for straightforward, well-understood work and time-sensitive hotfixes.
> - **Smart** — Phases run automatically; pause only when the next phase produces a HIGH-risk operation.

Store the selection in the context object (replacing the placeholder in the schema below):

```yaml
interactionMode: detailed | smart | autopilot
```

**Propagation:** The `interactionMode` value flows into `research`, `design`, and `generate` artifacts. Each downstream phase reads the value and adjusts its confirmation behaviour:

- **Detailed:** Pause at every phase transition; show generated artifacts; require explicit approval.
- **Autopilot:** Run every phase automatically; report only the final outcome.
- **Smart:** Run phases automatically; pause only at HIGH-risk operations.

## Core Workflow: Four-Phase Pipeline

Each phase is orchestrated sequentially: the orchestrator (this skill) calls the correspondent module, receives the output artifact, validates it with a quality gate, and passes it to the next phase.

### INPUT

- Receives the context object from the user, a saved prompt, a document, a previous plan, or a combination of these. The context object is a structured representation of the task, its requirements, and any relevant constraints. It may include:
  - Task description
  - Goals and objectives
  - Constraints and limitations
  - Relevant documents or references
  - Previous plans or related work
- **If no context is provided, ask the user for input**:
  "What would you like to plan? Describe the task or project."
- Output: [User Input Artifact](references/templates/artifacts/user-input.md)

### Phase 1: [Scope](modules/scope.md)

- Gather context, validate domain, bootstrap requirements
- Output: [Scoped context artifact](references/templates/artifacts/scoped-context.md)

### Phase 2: [Research](modules/research.md)

- Discover patterns, identify risks, recommend external research
- Output: [Research findings artifact](references/templates/artifacts/research-findings.md)

### Phase 3: [Design](modules/design.md)

- Decompose into units, map dependencies, assess complexity
- Output: [Design artifact with unit decomposition](references/templates/artifacts/design.md)

### Phase 4: [Generate](modules/generate.md)

- Select tier, render plan, embed learnings, save to docs/plans/
- Output: [Final plan document](references/templates/artifacts/final-plan.md) saved to a file

### Phase 5: [Tasks](modules/tasks.md) (optional phase)

- This phase is optional and can be skipped if the user prefers to slice tasks manually, ask it before continuing even in Autopilot mode.
- Slice plan into executable tasks from the Unit Task List generated in the previous phases, and save to docs/tasks/PLAN_ID/
- Output: [Task list artifact](references/templates/artifacts/task.md)

### FINAL OUTPUT

Plan file ready for execution.

## Modules References

- [Scope](modules/scope.md) — Context & scope gathering
- [Research](modules/research.md) — Pattern discovery & risk identification
- [Design](modules/design.md) — Unit decomposition & dependency mapping
- [Generate](modules/generate.md) — Plan rendering & file generation
- [Tasks](modules/tasks.md) — Task slicing & execution planning

## Core Principles

- **Deterministic Pipeline:** Phases always execute in sequence: scope → research → design → generate → tasks (no agent switching, no fallback paths).
- **Error Handling:** Fail explicitly, not silently. Each phase has clear error handling with recovery suggestions.
- **Focus on Decisions:** Capture approach, structure, risks, and sequencing (not code simulation)
- **Right-Size:** Small tasks → short plans; complex work → more structure
- **Separate Planning from Execution:** NEVER simulate implementation during planning
- **Be Concrete:** Use specific files, components, and dependencies
- **Stay Portable:** Use repository-relative paths only
- **Transparent Artifacts:** Each phase PRODUCES EXPLICIT OUTPUT artifact for next phase
- **Interaction Mode Propagation:** Once set, interaction_mode (detailed, smart, or autopilot) is read at the start of each subsequent phase and step and determines whether confirmation steps execute.
