---
title: "Task slicing heuristics: one Acceptance Criterion per task, test-driven"
timestamp: "2026-07-04"
updated: "2026-08-07"
category: workflow
domain: task-management
tags: [task-slicing, tdd, acceptance-criteria, decomposition, work-breakdown, implementation-units]
severity: recommended
source: commit 3c17d20
revised_in: commit 40b4808
---

# Task Slicing Heuristics (Acceptance-Criterion-driven, Test-Driven)

> Revised 2026-08-07 (commit `40b4808`). The original heuristic — "one unit → one task, merge trivial units, split by files/effort/scenario" — is superseded by an Acceptance-Criterion-driven, test-driven model.

## Problem

Implementation units from the Design phase are coarse chunks of work. The prior model sliced by files/effort/scenario-count, which produced tasks of variable size and intent, and its "merge adjacent trivial units" rule bundled unrelated outcomes into one task. There was no guaranteed invariant between what a task tests and what it delivers.

## Solution

A fixed invariant plus a small set of heuristics.

### Invariant (always)

- **One task per Acceptance Criterion.** Each criterion on an implementation unit becomes exactly one task.
- **One test per task.** The task's `files.test` holds exactly one test file asserting that single criterion.
- **Test-Driven Steps** — Red → Green → Refactor:
  1. Red — write the failing test for this AC; run it and confirm it fails for the right reason.
  2. Green — implement the minimum code to pass.
  3. Refactor — clean up naming/duplication with the test green.

### Slicing rules

- Never split within an Acceptance Criterion. If a criterion would need > 5 files or > 1 day, split the **criterion** into finer sub-criteria first, then one task each.
- Never merge across criteria. A task always carries exactly one AC (+ its one test). (Adjacent units that genuinely share a single criterion are already one criterion — hence one task.)
- Never renumber units or criteria. Sub-IDs use letters: `U2a`, `U2b`.

### What changed from the prior model

- Removed the "merge adjacent trivial units" rule — it bundled multiple outcomes into one task, breaking the one-AC invariant.
- Split triggers are now AC-anchored (split the criterion, not the task).
- Files / effort / scenario thresholds became tier-sizing guidance, not slicing triggers.

## Application

- Run during the Tasks phase after reading implementation units. Implementation Units now carry Acceptance Criteria (authored in the Design phase, carried by the design and final-plan templates).
- Reference: `skills/plan/references/task-slicing-rules.md`, `skills/plan/references/templates/artifacts/task.md`

## Source

- Original heuristic: commit `3c17d20`
- Revised to AC-driven TDD: commit `40b4808`