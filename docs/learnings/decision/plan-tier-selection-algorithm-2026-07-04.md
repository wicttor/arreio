---
title: "Plan tier selection algorithm with complexity defaults, risk floors, and user preference"
timestamp: "2026-07-04"
category: decision
domain: planning
tags: [plan-tiers, tier-selection, risk-floor, complexity-driven, user-preference]
severity: recommended
source: commit 3c17d20
---

# Plan Tier Selection Algorithm

## Problem

Implementation plans need different levels of detail based on work complexity — a one-file bugfix doesn't need the same rigor as a cross-system migration. Without a selection algorithm, every plan gets the same template, wasting effort on simple work or under-planning complex work.

## Solution

Three plan tiers with a deterministic selection algorithm:

### Tiers

| Tier | Sections | Use Case |
|------|----------|----------|
| **Fast** | Overview, Design, Units, Risk (brief), Learnings | TRIVIAL/LOW complexity, well-understood patterns |
| **Standard** | Fast + Alternatives, Rollout Notes, Learning Gaps | MEDIUM complexity, moderate risk |
| **Deep** | Standard + full Risk Analysis with impact ratings + rollback plan | HIGH/VERY_HIGH complexity, CRITICAL risk |

### Selection Algorithm

```
1. Start from complexity-driven default:
   TRIVIAL/LOW → Fast
   MEDIUM → Standard
   HIGH/VERY_HIGH → Deep

2. Apply risk floor (never go below):
   CRITICAL risk → floor at Deep
   HIGH risk → floor at Standard

3. Honor user preference unless it violates risk floor:
   If user prefers Fast but floor is Standard → upgrade to Standard
   If user prefers Deep for LOW complexity → allow (user knows context)
```

### Decision Rationale

- **Why three tiers?** Two (simple/complex) loses nuance; four+ adds overhead without clear benefit. Three maps cleanly to the complexity scale.
- **Why risk floors?** Safety mechanism: CRITICAL risk work (security, payments, data loss) must have Deep planning regardless of complexity score.
- **Why allow user overrides upward?** Users have context the algorithm doesn't. Overriding up (Fast→Deep) is always safe; overriding down is blocked by risk floors.

## Application

- Run during Generate phase (Phase 4) after complexity is assessed
- Record both `tier` (selected) and `tier_recommended` (algorithm's suggestion) for audit trail
- Reference: `skills/plan/references/plan-tier-selection.md`

## Source

- `skills/plan/modules/generate.md` — Step 1: Tier Selection
- `skills/plan/references/plan-tier-selection.md`
- Commit `3c17d20`
