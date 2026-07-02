---
title: "Interaction mode propagation for multi-phase skill pipelines"
date: 2026-07-02
category: pattern
domain: skill-design
tags: [pipeline-architecture, user-interaction, mode-propagation, orchestration]
severity: recommended
source: commit 3943146
---

# Interaction Mode Propagation for Multi-Phase Skill Pipelines

## Problem

Skills with multiple phases (scope → research → design → generate → tasks) need different levels of user interaction depending on task complexity. Without a propagation system, each phase must independently decide when to ask the user, leading to inconsistent UX and either too many interruptions or too little oversight.

## Solution

Set `interactionMode` once at the orchestrator level. Each downstream phase reads it from the incoming artifact and applies mode-specific behavior. All phases write the mode to their output artifact for the next phase to consume.

### Mode Table

| Mode         | Behavior                                              | Use Case                             |
| ------------ | ----------------------------------------------------- | ------------------------------------ |
| **Detailed** | Pause at each phase; show artifacts; require approval | Complex work, unfamiliar codebases   |
| **Smart**    | Auto-proceed; pause only on HIGH-risk flags           | Familiar codebases with guardrails   |
| **Autopilot**| Run all phases auto (except Tasks, which always asks) | Straightforward work, time-sensitive |

### Phase Behavior by Mode

| Phase        | Detailed                          | Smart                                      | Autopilot         |
| ------------ | --------------------------------- | ------------------------------------------ | ----------------- |
| **Scope**    | Present artifact; user confirms   | Auto-proceed; pause if ≥3 gaps or conflict | Auto-proceed      |
| **Research** | Show findings; ask to proceed     | Auto-proceed; pause on HIGH-risk           | Auto-proceed      |
| **Design**   | Show units; ask to proceed        | Auto-proceed; pause on VERY_HIGH complexity| Auto-proceed      |
| **Generate** | Show plan; ask to generate tasks  | Auto-proceed; pause on DEEP tier           | Auto-proceed      |
| **Tasks**    | Ask to create task files          | Ask to create task files                   | Ask (always)      |

### Artifact Schema

All phase artifacts include:

```yaml
type: scope | research | design | plan
scope-id: 2026-07-02-001-scope
interactionMode: detailed | smart | autopilot
status: pending | confirmed | failed
```

## Application

- **Each phase must:** read `interactionMode` from incoming artifact, apply mode-specific behavior, include `interactionMode` in output artifact.
- **Default:** If mode is missing from artifact, default to `smart` and log a warning.
- **Tasks phase:** Always asks user about task slicing, even in Autopilot mode.

## Source

- `skills/plan/modules/1-scope/scope.md` — Step 7 implementation
- `skills/plan/references/interaction-mode-propagation.md` — Full reference doc
- Commit `3943146`
