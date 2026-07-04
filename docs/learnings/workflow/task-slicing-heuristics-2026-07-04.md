---
title: "Task slicing heuristics for decomposing implementation units into executable tasks"
timestamp: "2026-07-04"
category: workflow
domain: task-management
tags: [task-slicing, decomposition, estimation, work-breakdown, implementation-units]
severity: recommended
source: commit 3c17d20
---

# Task Slicing Heuristics

## Problem

Implementation units from the Design phase are coarse chunks of work. Turning them directly into task files results in oversized tasks that are hard to estimate, execute, and review. A systematic slicing approach is needed to break units into granular, executable tasks.

## Solution

A set of heuristics that transform implementation units into task files:

### Default Rule

**One unit → one task.** Each unit becomes a task file inheriting its goal, dependencies, files, and test scenarios. This is the starting point; slicing only happens when a unit exceeds thresholds.

### Split Triggers

Split a unit into sub-tasks (using letter suffixes: `U2a`, `U2b`) when:

| Trigger | Threshold | Split Method |
|---------|-----------|--------------|
| **File count** | > 5 files touched | Split by file grouping (e.g., models vs. routes) |
| **Effort** | > 1 day estimated | Split by sub-goal (milestone within the unit) |
| **Test scenarios** | > 5 distinct scenarios | Split by scenario cluster |
| **Separable outcomes** | 2+ independent deliverables | Split by outcome |

### Merge Rules

Merge adjacent units into one task when ALL of:
- Each unit touches only 1 file
- Combined files ≤ 3
- Shared dependency (or both have no dependencies)
- Neither unit has its own test scenario

The merged task lists all source units in the `unit` field (e.g., `U3, U4`).

### Ordering

After slicing, order tasks by dependency so the Work skill can execute them sequentially. Tasks with no dependencies go first; tasks depending on U1 go after U1, etc.

## Application

- Run during Tasks phase (Phase 5) after reading implementation units
- Never renumber original units — use letter suffixes for splits
- Record slicing decisions for traceability (which units were split/merged and why)
- Reference: `skills/plan/references/task-slicing-rules.md`

## Source

- `skills/plan/modules/tasks.md` — Step 2: Apply Slicing Heuristics
- `skills/plan/references/task-slicing-rules.md`
- Commit `3c17d20`
