---
title: "Five-dimension complexity assessment framework for implementation planning"
timestamp: "2026-07-04"
category: decision
domain: planning
tags: [complexity-assessment, risk-scoring, implementation-planning, estimation]
severity: recommended
source: commit 3c17d20
---

# Five-Dimension Complexity Assessment Framework

## Problem

When planning implementation work, "complexity" is often a gut-feel estimate that varies by developer. Without a structured scoring system, complexity assessments are inconsistent, making it hard to decide how much planning rigor a task needs.

## Solution

Score the design across five dimensions (0–3 each), sum the scores (0–15), and map to a complexity level:

### Dimensions

| Dimension | What It Measures | 0 | 1 | 2 | 3 |
|-----------|-----------------|---|---|---|---|
| `scope_breadth` | Files/components touched | 1 file | 2–3 files | 4–7 files | 8+ files |
| `integration_surface` | External system touchpoints | 0 integrations | 1 integration | 2–3 integrations | 4+ integrations |
| `risk_level` | Inherited from Research phase | Low | Medium | High | Critical |
| `novelty` | How new the approach is to the team | Known pattern, HIGH confidence | Known pattern, MEDIUM confidence | New pattern, researched externally | No precedent found |
| `data_migration` | Data/schema changes required | None | Schema-only (additive) | Data migration (non-destructive) | Destructive migration or rollback plan needed |

### Complexity Mapping

| Total Score | Complexity Level |
|-------------|-----------------|
| 0–2 | TRIVIAL |
| 3–5 | LOW |
| 6–9 | MEDIUM |
| 10–12 | HIGH |
| 13–15 | VERY_HIGH |

## Decision Rationale

- **Why 5 dimensions?** Covers the key risk factors (scope, dependencies, risk, unfamiliarity, data safety) without over-fitting. More dimensions add noise; fewer miss critical signals.
- **Why 0–3 scale?** Coarse enough to assign quickly, fine enough to distinguish levels. Avoids the false precision of 1–10 scales.
- **Why inherit risk_level from Research?** Risk assessment is done once in Research phase; re-scoring it in Design would create inconsistency. The Design phase only scores the four dimensions it owns.

## Application

- Run during the Design phase (Phase 3) after implementation units are decomposed
- Record all five individual scores + total + complexity level in the Design Artifact
- The complexity level drives plan tier selection in the Generate phase
- Reference: `skills/plan/references/design-complexity-assessment.md`

## Source

- `skills/plan/modules/design.md` — Step 4: Complexity Assessment
- `skills/plan/references/design-complexity-assessment.md`
- Commit `3c17d20`
