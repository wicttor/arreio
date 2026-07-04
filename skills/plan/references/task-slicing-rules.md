---
title: Task Slicing Rules
description: Reference for the Tasks phase. Defines how to decompose a plan's implementation units into granular, executable task files, including sizing heuristics, dependency ordering, and file-naming conventions.
type: reference
version: 1.0
timestamp: "2026-07-03"
---

# Task Slicing Rules

This file documents the rules for decomposing a finalized plan into individual task files during the **Tasks** phase (Phase 5). It defines the slicing heuristics, dependency ordering, sizing limits, file-naming conventions, and index registration rules.

## When to Apply

Task slicing runs after the Generate phase has produced a validated Final Plan. The Tasks phase reads the plan's Implementation Units and produces one task file per slice, saved to `docs/tasks/<plan-id>/` and registered in `docs/tasks/<plan-id>/index.md`.

## Core Slicing Heuristics

### Rule 1: One Task Per Unit (Default)

Each Implementation Unit (`U1`, `U2`, ...) in the plan becomes **one task** by default. The task inherits the unit's goal, dependencies, files, and test scenarios.

### Rule 2: Split a Unit When It Exceeds Sizing Limits

A single unit should be split into multiple tasks if it exceeds any of these limits:

| Limit                    | Threshold                           | Action                    |
| ------------------------ | ----------------------------------- | ------------------------- |
| Files touched            | > 5 files                           | Split by file grouping    |
| Estimated effort         | > 1 day of work                     | Split by sub-goal         |
| Test scenarios           | > 5 distinct scenarios              | Split by scenario cluster |
| Independent sub-outcomes | Unit delivers 2+ separable outcomes | Split by outcome          |

### Rule 3: Merge Units When They Are Too Small

Adjacent units that are trivially small should be merged into a single task if **all** of these are true:

- Each unit touches only 1 file
- Combined files touched ≤ 3
- The units share a dependency
- No unit has its own test scenario

### Rule 4: Preserve Dependency Order

Tasks must be ordered so that a task's dependencies are fully satisfied by earlier tasks. Never produce a task that depends on a later task.

```
valid ordering:
  T1 (no deps) → T2 (deps: T1) → T3 (deps: T1, T2)

invalid ordering:
  T2 (deps: T3) → T1 (no deps) → T3 (deps: T1)
```

### Rule 5: Never Renumber Units

When slicing, preserve the original `U#` identifiers from the plan. If a unit is split, use sub-identifiers (e.g., `U2a`, `U2b`). Never renumber the original units — they are referenced by the plan and downstream execution.

## Sizing Targets by Plan Tier

| Tier     | Target Tasks | Max Files Per Task | Max Effort Per Task |
| -------- | ------------ | ------------------ | ------------------- |
| Fast     | 1–3          | 3                  | Half day            |
| Standard | 4–8          | 5                  | 1 day               |
| Deep     | 8–15         | 5                  | 1 day               |

If a tier's task count would exceed the target, prefer splitting by sub-goal first, then by file grouping. If it would fall short, prefer merging trivially small units.

## Task File Schema

Each task file is saved as markdown with this schema (see [task.md template](templates/artifacts/task.md)):

```yaml
---
id: <plan-id>-T<NN>
title: "[Task title]"
plan-id: <plan-id>
unit: U<NN> | U<NN><letter>
tier: fast | standard | deep
status: not-started
priority: P0 | P1 | P2
dependencies: [<task-id>, ...]
files:
  create: [path/to/file, ...]
  modify: [path/to/file, ...]
  test: [path/to/test, ...]
estimated-effort: "<hours or days>"
---

# [Task Title]

## Goal
[What this task accomplishes, inherited from the unit]

## Steps
1. [Concrete step]
2. [Concrete step]

## Test Scenarios
- [Scenario]: [Input -> Expected Outcome]

## Acceptance Criteria
- [ ] [Criterion 1]
- [ ] [Criterion 2]

## Notes
[Any context, gotchas, or references]
```

## File-Naming Convention

Task files are named:

```
docs/tasks/<plan-id>/T<NN>-<kebab-case-name>.md
```

Where:

- `<plan-id>` — The plan's ID (e.g., `2026-07-03-001`)
- `<NN>` — Zero-padded 2-digit task number, matching dependency order (01, 02, ..., 10)
- `<kebab-case-name>` — Short descriptive name (e.g., `redis-client-setup`)

**Example:**

```
docs/tasks/2026-07-03-001/
  T01-redis-client-setup.md
  T02-session-store-interface.md
  T03-session-middleware-refactor.md
```

## Task ID Generation

```
1. Read the plan-id from the Final Plan artifact
2. Tasks are numbered NN in dependency order (01, 02, ...)
3. If a unit is split: U2 → T02a, T02b (use letters, not extra digits)
4. If units are merged: T03 covers U3 + U4 (note both in the `unit` field)
```

## Dependency Ordering Algorithm

```
function order_tasks(units):
  # units is a list of {id, dependencies, ...}
  ordered = []
  remaining = copy(units)
  while remaining:
    ready = [u for u in remaining if all(d in ordered for d in u.dependencies)]
    if not ready:
      raise CycleError("Dependency cycle detected among: " + remaining)
    # Sort ready units by original unit number for stable ordering
    ready.sort(by: unit_number)
    ordered.extend(ready)
    remaining.remove(ready)
  return ordered
```

**Cycle handling:** If no unit is ready (all have unsatisfied dependencies), a cycle exists. Log the error, surface the involved units to the user, and ask whether to break the cycle manually or abort.

## Priority Assignment

| Priority | Criteria                                           |
| -------- | -------------------------------------------------- |
| P0       | Blocks all other tasks (foundation, infra, schema) |
| P1       | On the critical path but not blocking              |
| P2       | Can be deferred or parallelized                    |

Default: foundation phase units → P0; integration phase units → P1; rollout/optional units → P2.

## Index Registration

After saving all task files, update `docs/tasks/<plan-id>/index.md`:

```markdown
## <plan-id> — [Plan Title]

- [ ] T01 — [Task title] — `docs/tasks/<plan-id>/T01-<name>.md`
- [ ] T02 — [Task title] — `docs/tasks/<plan-id>/T02-<name>.md`
```

Mark each task with `- [ ]` (unchecked). The Work skill will check them off as tasks complete.

## Error Handling

| Scenario                                | Recovery                                        |
| --------------------------------------- | ----------------------------------------------- |
| `docs/tasks/` directory missing         | Create it; create `<plan-id>/` subdirectory     |
| `docs/tasks/<plan-id>/index.md` missing | Create empty index; append the plan's section   |
| Dependency cycle detected among units   | Surface cycle to user; ask to break or abort    |
| Unit has no `Files` field               | Log warning; produce task with empty file lists |
| Plan has no Implementation Units        | Abort; ask user to re-run Generate phase        |
| Task count exceeds tier target          | Log warning; proceed (targets are guidance)     |

## Interaction Mode Behavior

Per [interaction-mode-propagation.md](interaction-mode-propagation.md), the Tasks phase **always asks the user**, even in Autopilot mode:

| Mode      | Behavior                                         |
| --------- | ------------------------------------------------ |
| Detailed  | Show full task list; ask to save files           |
| Smart     | Show task list summary; ask to save files        |
| Autopilot | Show task count; ask to save files (always asks) |

The question asked:

```
The plan has been sliced into <N> tasks (T01–T<NN>).
Would you like me to create the task files in docs/tasks/<plan-id>/?
  - Yes: Create all task files and update the index
  - Review: Show the task list first, then ask again
  - No: Skip task creation (plan is still saved for manual slicing)
```

## Notes

- Tasks are the handoff point to the Work skill (`work/SKILL.md`); they must be self-contained enough to execute without re-reading the full plan
- Each task's `Acceptance Criteria` should be verifiable without subjective judgment
- Preserve the plan's `Related Learnings` in task files that touch the relevant domain, so the Work phase has context
- If the user declines task creation, the plan remains the unit of work — the user can slice manually later
