---
title: Tasks
description: Slice the finalized plan into granular, executable task files saved to docs/tasks/. Decomposes implementation units per sizing rules, orders by dependencies, and registers tasks in the index. Optional Phase 5 of the Plan pipeline.
type: module
version: 1.0
timestamp: "2026-07-03"
---

# Phase 5 - Tasks

**Purpose:** Fifth and final (optional) step in the planning workflow. Reads the Final Plan's Implementation Units, slices them into granular, executable task files per the [task-slicing rules](../references/task-slicing-rules.md), orders them by dependency, and saves them to `docs/tasks/<plan-id>/`. Produces a set of [Task Artifacts](../references/templates/artifacts/task.md) that the Work skill (`work/SKILL.md`) consumes for execution.

> **Optional phase.** The Orchestrator must ask the user before continuing to this phase, even in Autopilot mode — the user may prefer to slice tasks manually or defer task generation.

## Workflow

This is the Phase 5 pipeline for the Plan Skill. It orchestrates the following steps:

### Step 0: Verification

Before starting the **Tasks** phase, verify that the Orchestrator skill has provided a valid **Final Plan Artifact** from the Generate phase. If the artifact is missing or invalid, use the **[Error Handling & Recovery workflow](../references/error-handling.md)** to recover or terminate.

Specifically verify:

1. The Final Plan exists at `docs/plans/YYYY-MM-DD-NNN-<kebab-case-name>.md` and is non-empty.
2. The plan frontmatter contains `plan-id`, `tier`, `complexity`, `risk`, and `interactionMode`.
3. The plan body contains an `## Implementation Units (Phased)` section with at least one unit (`U1`).
4. If the plan has no Implementation Units, abort and ask the user to re-run the Generate phase — the plan is incomplete.

### Step 1: Read and Normalize Units

1. **Read the Implementation Units** from the Final Plan. Parse each unit into a normalized record:

   ```yaml
   - id: U1
     name: "[Unit Name]"
     goal: "[What this unit accomplishes]"
     phase: 1 | 2 | 3
     dependencies: [U<id>, ...] # Unit IDs this depends on
     files:
       create: [path, ...]
       modify: [path, ...]
       test: [path, ...]
     test_scenarios:
       - "[Scenario]: [Input -> Expected Outcome]"
   ```

2. **Extract the plan's `Related Learnings`** to carry into task files that touch the relevant domains.

3. **Extract the plan's `tier`** to determine sizing targets (see Step 3).

### Step 2: Apply Slicing Heuristics

Apply the slicing rules from **[task-slicing-rules.md](../references/task-slicing-rules.md)** to each unit:

1. **Default: one task per unit.** Each unit becomes one task, inheriting its goal, dependencies, files, and test scenarios.

2. **Split a unit** if it exceeds any sizing limit:
   - > 5 files touched → split by file grouping
   - > 1 day of estimated effort → split by sub-goal
   - > 5 distinct test scenarios → split by scenario cluster
   - 2+ separable outcomes → split by outcome

   When splitting, use sub-identifiers: `U2` → `U2a`, `U2b` (letters, not extra digits). Never renumber the original units.

3. **Merge adjacent units** if all are true: each touches only 1 file, combined ≤ 3 files, shared dependency, and no unit has its own test scenario. The merged task lists all source units in the `unit` field (e.g., `U3, U4`).

4. **Record the slicing decisions** for traceability (which units were split or merged, and why).

### Step 3: Order by Dependencies

Order the tasks so each task's dependencies are satisfied by earlier tasks. Apply the topological ordering algorithm from [task-slicing-rules.md](../references/task-slicing-rules.md):

```
1. Start with all tasks as "remaining"
2. Find tasks whose dependencies are all already ordered → "ready"
3. If no task is ready: a cycle exists → surface to user, ask to break or abort
4. Sort ready tasks by original unit number (stable ordering)
5. Append ready tasks to "ordered"; remove from "remaining"
6. Repeat until all tasks are ordered
```

**Cycle handling:** If a dependency cycle is detected, log the error, list the involved units, and ask the user via `ask_user_question` whether to break the cycle manually (by removing a dependency) or abort the Tasks phase.

### Step 4: Assign Priorities

Assign a priority to each ordered task:

| Priority | Criteria                                           |
| -------- | -------------------------------------------------- |
| P0       | Blocks all other tasks (foundation, infra, schema) |
| P1       | On the critical path but not blocking              |
| P2       | Can be deferred or parallelized                    |

Default mapping:

- Phase 1 (Foundation) units → `P0`
- Phase 2 (Integration) units → `P1`
- Phase 3 (Rollout) units → `P2`

Adjust based on the plan's risk analysis — e.g., a rollout unit that mitigates a HIGH risk may be `P1`.

### Step 5: Generate Task Files

For each ordered task, generate a task file using the [Task Artifact template](../references/templates/artifacts/task.md).

1. **Assign a task ID:** `<plan-id>-T<NN>` where `NN` is a zero-padded 2-digit number matching dependency order (01, 02, ..., 10).

2. **Derive the task filename:** `T<NN>-<kebab-case-name>.md` (e.g., `T01-redis-client-setup.md`).

3. **Fill the task schema:**
   - `id`: `<plan-id>-T<NN>`
   - `title`: Action-oriented, from the unit name
   - `plan-id`: From the Final Plan
   - `unit`: The originating unit ID(s) (e.g., `U1` or `U2a` or `U3, U4` if merged)
   - `tier`: Inherited from the Final Plan
   - `status`: `not-started`
   - `priority`: From Step 4
   - `dependencies`: Task IDs of the unit's dependencies (mapped through the ordering)
   - `files`: Inherited from the unit (create/modify/test)
   - `estimated-effort`: Rough estimate (hours or days); default by tier (Fast: ≤ half day; Standard: ≤ 1 day; Deep: ≤ 1 day)
   - `Goal`: Inherited from the unit (1–2 sentences)
   - `Steps`: Break the unit's goal into 3–7 concrete, actionable steps
   - `Test Scenarios`: Inherited from the unit (required for Phase 1–2 units)
   - `Acceptance Criteria`: Derived from test scenarios (at least 1 checkable item)
   - `Notes`: Carry relevant `Related Learnings` and any gotchas

4. **Validate each task file** against the schema validation rules (see [task.md template](../references/templates/artifacts/task.md)).

### Step 6: Save Task Files

1. **Create the task directory:** `docs/tasks/<plan-id>/` (create if it does not exist).
2. **Save each task file** to `docs/tasks/<plan-id>/T<NN>-<kebab-case-name>.md`.
3. **Verify** all files were written successfully.

### Step 7: Update Tasks Index

Append a section to `docs/tasks/<plan-id>/index.md`:

```markdown
## <plan-id> — [Plan Title]

- [ ] T01 — [Task title] — `docs/tasks/<plan-id>/T01-<name>.md`
- [ ] T02 — [Task title] — `docs/tasks/<plan-id>/T02-<name>.md`
- [ ] T03 — [Task title] — `docs/tasks/<plan-id>/T03-<name>.md`
```

Mark each task with `- [ ]` (unchecked). The Work skill will update these to `- [x]` as tasks complete.

If `docs/tasks/<plan-id>/index.md` does not exist, create it with a header and the new section. If it exists but is malformed, log a warning and append the section without reformatting existing content.

### Step 8: Present and Confirm

> **Always ask the user in this phase**, even in Autopilot mode (per [interaction-mode-propagation.md](../references/interaction-mode-propagation.md)).

1. Read the `interactionMode` value from the incoming Final Plan artifact.

2. **All modes (detailed, smart, autopilot):**
   - Present the task list summary to the user via `ask_user_question`:
     ```
     The plan has been sliced into <N> tasks (T01–T<NN>).
     Would you like me to create the task files in docs/tasks/<plan-id>/?
     ```
   - Options: (1) Yes — Create all task files and update the index, (2) Review — Show the task list first, then ask again, (3) No — Skip task creation
   - If user selects "Review," display the full task list (IDs, titles, dependencies, priorities) and re-prompt
   - If user selects "No," skip task creation; the plan remains the unit of work (the user can slice manually later). Inform the Orchestrator that the plan is complete without tasks.
   - If user selects "Yes," proceed to Step 9.

3. **Detailed mode only:** Before saving, also show the full content of each task file for review. Allow the user to request edits to individual tasks before saving.

### Step 9: Return to Orchestrator

1. **Return the task manifest** to the Orchestrator:

   ```yaml
   plan-id: YYYY-MM-DD-NNN
   task-count: <N>
   tasks:
     - id: <plan-id>-T01
       path: docs/tasks/<plan-id>/T01-<name>.md
       priority: P0
       dependencies: []
     - id: <plan-id>-T02
       path: docs/tasks/<plan-id>/T02-<name>.md
       priority: P1
       dependencies: [<plan-id>-T01]
   interactionMode: detailed | smart | autopilot
   ```

2. **Inform the Orchestrator** that the Plan workflow is complete. The task files are ready for the Work skill (`work/SKILL.md`) to execute in dependency order.

## Output: Task Artifacts

- Verify that one task file exists per slice, saved to `docs/tasks/<plan-id>/T<NN>-<name>.md`.
- Verify that each task file contains all required fields per the [task.md template](../references/templates/artifacts/task.md) validation rules.
- Verify that task IDs are zero-padded 2 digits matching dependency order, with no gaps.
- Verify that no task depends on a later task (dependency order is valid).
- Verify that `docs/tasks/<plan-id>/index.md` has been updated with an unchecked checklist for all tasks.
- Verify that the task manifest returned to the Orchestrator accurately reflects the saved files.

> The Task Artifacts are the handoff to the Work skill. Each task must be self-contained enough to execute without re-reading the full plan.
