---
title: Interaction Mode Propagation
description: Reference for how `interactionMode` propagates through the Plan pipeline (Scope → Research → Design → Generate → Tasks). Set at Orchestrator; each phase reads and applies mode-specific behavior.
type: reference
version: 1.0
timestamp: "2026-07-02"
---

# Interaction Mode Propagation

Reference for how `interactionMode` propagates through the Plan pipeline (Scope → Research → Design → Generate → Tasks). Set at Orchestrator; each phase reads and applies mode-specific behavior.

## Modes

| Mode          | Behavior                                              | Use Case                             |
| ------------- | ----------------------------------------------------- | ------------------------------------ |
| **Detailed**  | Pause at each phase; show artifacts; require approval | Complex work, unfamiliar codebases   |
| **Smart**     | Auto-proceed; pause only on HIGH-risk flags           | Familiar codebases with guardrails   |
| **Autopilot** | Run all phases auto (except Tasks, which always asks) | Straightforward work, time-sensitive |

## Phase Behavior by Mode

| Phase        | Detailed                                         | Smart                                                | Autopilot                         |
| ------------ | ------------------------------------------------ | ---------------------------------------------------- | --------------------------------- |
| **Scope**    | Present artifact; 3 options (proceed/edit/abort) | Auto-proceed; pause if 3+ gaps or conflicts detected | Auto-proceed                      |
| **Research** | Show findings; ask "Proceed to Design?"          | Auto-proceed; pause if 3+ gaps, non-software domain, or conflicting requirements | Auto-proceed                      |
| **Design**   | Show units; ask "Proceed to Generate?"           | Auto-proceed; pause if VERY_HIGH complexity          | Auto-proceed                      |
| **Generate** | Show plan; ask "Generate tasks?"                 | Auto-proceed; pause if DEEP tier or conflicts        | Auto-proceed                      |
| **Tasks**    | Ask "Create task files?"                         | Ask "Create task files?"                             | Ask "Create task files?" (always) |

**Smart mode pauses on:** Learning gaps ≥3, HIGH-risk factors, VERY_HIGH complexity, DEEP tier, recent learning conflicts.

## Artifact Schema

All phase artifacts (Scope 1-4) include:

```yaml
type: scope | research | design | plan
scope-id: 2026-07-02-001-scope
interactionMode: detailed | smart | autopilot # Passed from previous phase
status: pending | complete | failed
```

## Implementation

**Each phase must:**

1. Read `interactionMode` from incoming artifact (or context for Scope)
2. Apply mode-specific behavior per table above
3. Include `interactionMode` in output artifact

**Phase 5 (Tasks):** Always ask user about task slicing, even in Autopilot mode.

## Example

**SMART mode on complex codebase task:**

- Scope detects 3 learning gaps → pauses (HIGH-risk)
- User approves → Research runs
- Research detects unfamiliar framework → pauses (HIGH-risk)
- User approves → Design runs
- Design complexity MEDIUM → auto-proceeds
- Generate renders → auto-proceeds
- Tasks asks user → user chooses yes

**Result:** Paused only for critical decisions; faster than Detailed with safety guardrails.

## Error Handling

| Scenario                    | Recovery                              |
| --------------------------- | ------------------------------------- |
| Mode missing                | Default to "smart"; log warning       |
| Invalid mode value          | Reject; re-prompt Orchestrator        |
| Artifact missing mode field | Assume "smart"; log warning; continue |
| Timeout/connection lost     | Pause; ask user to retry or abort     |
