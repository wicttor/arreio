---
id: TASK-06
plan-id: 2026-09-01-001-fix-end-session-gaps
type: task
title: Update arreio-init for end-session directories
status: completed
files:
  modify:
    - skills/arreio-init/SKILL.md
---

# TASK-06: Update arreio-init for end-session directories

## Description

Add `docs/plans/.end-session/` directory creation to `arreio-init` so the end-session skill has a pre-initialized artifact home.

## Acceptance Criterion

- [x] `skills/arreio-init/SKILL.md` includes a new **Step 11** to create `docs/plans/.end-session/` (learn category folders renumbered to Step 12)
- [x] The **Success Criteria** section lists `docs/plans/.end-session/` as a required directory
- [x] The **Self-Healing Behavior** section notes that end-session creates the directory and index section on first use if missing

## Steps

1. Red: Verify arreio-init does not mention end-session directories
2. Green: Add step and update Success Criteria / Self-Healing
3. Refactor: Ensure numbering and formatting remain consistent
