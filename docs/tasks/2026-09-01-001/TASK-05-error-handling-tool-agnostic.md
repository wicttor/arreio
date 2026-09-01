---
id: TASK-05
plan-id: 2026-09-01-001-fix-end-session-gaps
type: task
title: Add error-handling reference and tool-agnostic rewrite
status: completed
files:
  modify:
    - skills/end-session/SKILL.md
  create:
    - skills/end-session/references/error-handling.md
---

# TASK-05: Add error-handling reference and tool-agnostic rewrite

## Description

Create a standard error-handling reference for end-session and rewrite all git CLI commands as tool-agnostic capability descriptions.

## Acceptance Criterion

- [x] `skills/end-session/references/error-handling.md` exists with:
  - Step 0 verification procedure
  - Error categories: Missing Changes, Invalid Input, Ambiguous Attribution, File System, Git/Commit, Interaction Mode
  - Recovery workflow and retry limits
  - Error reporting format
- [x] `skills/end-session/SKILL.md` no longer contains hardcoded commands (`git status`, `git add`, `git commit`, `git tag -a` all removed)
- [x] Capability descriptions replace commands (e.g., "inspect the working tree state")
- [x] Post-commit step references `docs/learn/index.md` (not `docs/learnings/INDEX.md`)
- [x] Post-commit step suggests `/learn maintain` (not `/update-learnings`), without direct skill-to-skill invocation

## Steps

1. Red: Confirm current file has hardcoded commands and wrong learn path
2. Green: Replace commands with descriptions; fix learn path and skill reference
3. Refactor: Write error-handling reference matching core skill structure
