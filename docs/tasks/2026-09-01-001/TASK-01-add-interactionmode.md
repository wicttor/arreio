---
id: TASK-01
plan-id: 2026-09-01-001-fix-end-session-gaps
type: task
title: Add interactionMode support and frontmatter alignment
status: completed
files:
  modify:
    - skills/end-session/SKILL.md
---

# TASK-01: Add interactionMode support and frontmatter alignment

## Description

Align `end-session/SKILL.md` frontmatter with core skill conventions and add interactionMode selection.

## Acceptance Criterion

- [x] `skills/end-session/SKILL.md` frontmatter includes `disable-model-invocation: true`, `version: 1.1.0`, and `timestamp: "2026-09-01"`
- [x] An **Interaction Method** section exists that asks the user to choose **Detailed**, **Smart**, or **Autopilot**
- [x] `interactionMode` is stored in the context object and propagated to each phase
- [x] Phase behavior is described per mode (Detailed = confirm each phase; Smart = pause only on ambiguous attribution / declined completion; Autopilot = run all, always approve the final commit message)

## Steps

1. Red: Verify current SKILL.md lacks these fields
2. Green: Add frontmatter fields and Interaction Method section
3. Refactor: Ensure mode descriptions are concise and consistent with plan/work/review/learn
