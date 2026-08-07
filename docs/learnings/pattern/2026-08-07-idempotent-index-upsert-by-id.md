---
title: "Idempotent index registration by upserting on a stable id"
timestamp: "2026-08-07"
category: pattern
domain: skill-design
tags: [indexes, idempotency, registration, retry, id-generation]
severity: important
source: commit 40b4808
applicability:
  current_project: 9
  general: 8
related:
  - confirm-before-persist-ordering-2026-08-07
  - per-plan-task-indexing-2026-07-04
  - daily-counter-artifact-naming-2026-07-02
---

# Idempotent Index Registration by Upserting on a Stable id

## Problem

Phase indexes (`docs/plans/index.md`, `docs/tasks/<plan-id>/index.md`) were updated by **blind append** — each phase run added a row. When a phase lets the user "Edit & Retry" (or re-runs after an error), the same plan gets multiple rows, corrupting the index the next consumer reads.

## Solution

Make index registration **idempotent**: upsert (insert-or-replace) keyed on the artifact's stable id:

- `docs/plans/index.md` → keyed on `plan-id`.
- `docs/tasks/<plan-id>/index.md` → keyed on task id (`<plan-id>-T<NN>`).

On "Edit & Retry," the phase reuses the same id (see daily-counter artifact naming, recycle-on-edit) and the upsert overwrites the existing row instead of adding a duplicate. Insert only if no row with that id exists.

## Application

- Use wherever a phase can run more than once for the same artifact; an unconditional `append` is wrong the moment retry exists.
- The stable id is the key; the filename/template is the value. Keep the row format the contract between producers and consumers.
- This complements confirm-before-persist ordering; it is the secondary defense that keeps the index clean even if ordering is ever violated.

## Source

- `skills/plan/modules/generate.md` (Step 5 — insert-or-replace by `plan-id`)
- Commit `40b4808`