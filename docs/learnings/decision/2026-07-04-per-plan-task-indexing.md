---
slug: per-plan-task-indexing
type: decision
domain: task-management
priority: important
applicability:
  current_project: 10
  general: 7
tags: [task-organization, file-structure, co-location, indexing]
created_at: "2026-07-04T00:00:00Z"
updated_at: "2026-07-04T00:00:00Z"
source:
  type: commit
  reference: aa21a87
  extracted_at: "2026-07-04T00:00:00Z"
confidence: high
---

# Use Per-Plan Task Indexes Co-Located with Plans

## Problem

Task files were registered in a single global `docs/tasks/index.md` that mixed tasks from all plans together. This created several issues:

- Finding tasks for a specific plan required scanning the entire index
- Plan isolation was broken — deleting a plan's directory left dangling index entries
- The global index became a bottleneck when multiple plans were active in parallel
- Tooling had to parse the full index to extract plan-specific task lists

## Solution

Move task indexes from a single global file to per-plan directories:

```
Before:                          After:
docs/tasks/index.md              docs/tasks/2026-07-04-001/index.md
                                 docs/tasks/2026-07-04-002/index.md
                                 docs/tasks/2026-07-04-003/index.md
```

Each plan's task files live at `docs/tasks/<plan-id>/T<NN>-<name>.md` with their index at `docs/tasks/<plan-id>/index.md`.

## Decision Rationale

- **Co-location:** Tasks live next to their index, mirroring how plan artifacts live next to their metadata. This is the same principle as `docs/plans/YYYY-MM-DD-NNN-name.md` — each plan is a self-contained unit.
- **Isolation:** Deleting a plan directory removes all its tasks and index cleanly, with no orphaned references.
- **Parallelism:** Multiple plans can have their task indexes created/updated independently without merge conflicts on a shared file.
- **Discoverability:** A developer working on a specific plan only needs to look at one directory.

## Application

- `skills/plan/modules/tasks.md` — Step 7 writes to `docs/tasks/<plan-id>/index.md`
- `skills/arreio-init/SKILL.md` — Step 4 initializes `docs/tasks/<plan-id>/index.md`
- `skills/plan/SKILL.md` — Phase 5 documentation references per-plan indexes
- Work skill reads `docs/tasks/<plan-id>/index.md` for task discovery

## Related Learnings

- [Task slicing heuristics for decomposing implementation units](../workflow/task-slicing-heuristics-2026-07-04.md) — task files live in the per-plan directory this decision creates
