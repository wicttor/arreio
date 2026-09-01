---
id: TASK-04
plan-id: 2026-09-01-001-fix-end-session-gaps
type: task
title: Implement session-based agent attribution
status: completed
files:
  modify:
    - skills/end-session/SKILL.md
---

# TASK-04: Implement session-based agent attribution

## Description

Replace generic agent attribution with session-based detection: inspect changed files to infer the agent that made the changes.

## Acceptance Criterion

- [x] **Phase 3 (Prepare Commit)** includes a step to determine agent attribution from session changes
- [x] The skill inspects the change history of the files to identify which agent modified them
- [x] Files changed during the session → attribute the current agent; pre-session changes → detect from attribution trailers in recent history and confirm with the user
- [x] If attribution is mixed or cannot be determined, ask the user; the current agent is the explicit fallback
- [x] The `[AGENT: ...]` trailer remains mandatory on the last line of the commit message
- [x] The behavior is described tool-agnostically ("inspect the recent change history" — no CLI invocations)

## Steps

1. Red: Verify current attribution is generic/placeholder-only
2. Green: Add session-based attribution step with fallback
3. Refactor: Ensure the description stays tool-agnostic and the fallback is explicit
