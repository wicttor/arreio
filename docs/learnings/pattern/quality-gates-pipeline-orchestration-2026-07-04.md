---
title: "Quality gates between pipeline phases with schema validation and error recovery"
timestamp: "2026-07-04"
category: pattern
domain: skill-design
tags: [pipeline-architecture, quality-gates, validation, error-recovery, orchestration]
severity: recommended
source: commit 3c17d20
---

# Quality Gates Between Pipeline Phases

## Problem

In multi-phase pipelines, each phase consumes the output of the previous phase. If an upstream artifact is malformed, missing fields, or inconsistent, the downstream phase either crashes or produces incorrect results — often with confusing error messages far from the root cause.

## Solution

Insert quality gates between every phase. Before passing an artifact to the next phase, the orchestrator validates it against four checks:

### Gate Checks

| # | Check | What It Validates | On Failure |
|---|-------|-------------------|------------|
| 1 | **Schema validation** | Required fields present and well-formed per the artifact type | Return to producing phase with field list |
| 2 | **Cross-phase consistency** | IDs (`scope-id`, `research-id`, `design-id`, `plan-id`) match upstream artifacts; `interactionMode` is identical | Return with ID mismatch details |
| 3 | **Status check** | Artifact `status` is `confirmed` (not `pending` or `failed`) | Return; producing phase must re-confirm |
| 4 | **Tier/complexity coherence** | `tier_recommendation` is consistent with `complexity` and `risk_level` | Return with coherence violation details |

### Error Recovery

When a gate fails, the orchestrator returns to the producing phase with the error context. The producing phase re-runs its confirmation step, fixes the issue, and re-emits the artifact.

This follows the error-handling reference (`skills/plan/references/error-handling.md`) for structured recovery.

## Application

- Insert gates in the orchestrator between each phase transition
- Gate checks are additive — later phases may add phase-specific checks beyond the standard four
- The "tier/complexity coherence" gate only applies after the Design phase (when both values exist)
- Keep gate logic thin; delegate detailed field lists to the error-handling reference

## Source

- `skills/plan/SKILL.md` — Quality Gates section
- `skills/plan/references/error-handling.md`
- Commit `3c17d20`
