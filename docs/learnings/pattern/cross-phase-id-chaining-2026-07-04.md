---
title: "Cross-phase ID chaining for pipeline traceability"
timestamp: "2026-07-04"
category: pattern
domain: skill-design
tags: [pipeline-architecture, traceability, artifact-naming, cross-phase-validation]
severity: recommended
source: commit 3c17d20
---

# Cross-Phase ID Chaining for Pipeline Traceability

## Problem

In multi-phase pipelines, each phase produces an artifact consumed by the next. Without explicit ID linkage, it's impossible to trace which scope produced which design, or which research informed which plan. Debugging a bad plan requires manually correlating artifacts by timestamp.

## Solution

Each downstream artifact carries the IDs of all upstream artifacts it depends on. The ID chain is validated at every phase boundary:

```
scope-id: 2026-07-04-001-scope
  ↓ (validated by Research Step 0)
research-id: 2026-07-04-001-research
  ↓ (validated by Design Step 0)
design-id: 2026-07-04-001-design
  ↓ (validated by Generate Step 0)
plan-id: 2026-07-04-001
```

### Step 0 Verification

Every phase's Step 0 checks that the incoming artifact's upstream IDs match the expected values. For example, Design Step 0 verifies that `research-id` in the incoming research artifact matches the `scope-id` from the scope artifact.

### Benefits

- **Traceability:** From any plan, you can walk back to its scope, research, and design
- **Consistency:** Mismatched IDs indicate a pipeline error (wrong artifact passed)
- **Auditability:** Each artifact is a checkpoint in the decision chain

## Application

- Every artifact schema includes inherited IDs from upstream phases
- Step 0 verification in every phase module checks cross-phase consistency
- IDs use the daily counter algorithm (`YYYY-MM-DD-NNN-<type>`) for uniqueness
- If IDs don't match, return to the producing phase with the mismatch details

## Source

- `skills/plan/SKILL.md` — Quality Gates (cross-phase consistency)
- `skills/plan/modules/design.md` — Step 0 verification
- `skills/plan/modules/generate.md` — Step 0 verification
- Commit `3c17d20`
