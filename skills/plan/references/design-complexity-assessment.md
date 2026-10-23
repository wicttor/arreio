---
title: Design Complexity Assessment
description: Reference for the Design phase. Defines the complexity scoring algorithm across four dimensions, the heuristics for assigning complexity levels, and how complexity maps to interaction-mode pause behavior. Risk is not scored here; it only sets the tier floor.
type: reference
version: 1.3
timestamp: "2026-10-23"
---

# Design Complexity Assessment

This file documents the complexity scoring system used by the **Design** phase (Phase 3) to size a solution and decide whether to pause for user confirmation in Smart mode. It defines four scoring dimensions, the complexity-level thresholds, and the mapping to interaction-mode behavior.

**Risk is not a scoring dimension.** Risk already raises the plan tier through the risk floor in [plan-tier-selection.md](plan-tier-selection.md). Scoring it here as well counted the same fact twice and pushed ordinary work into `HIGH`/`VERY_HIGH`. Complexity answers "how big and how new is the work"; risk answers "how bad is a failure".

## When to Apply

Complexity assessment runs at the end of the Design phase, after the approach and implementation units have been drafted but before the artifact is presented or saved. The resulting `complexity` field is written to the Design Artifact and read by the Generate phase to select a plan tier (see [plan-tier-selection.md](plan-tier-selection.md)).

## Scoring Dimensions

Score each dimension from 0 to 3, then sum for a total complexity score (0–12).

| Dimension               | 0 — None                | 1 — Low                 | 2 — Medium                        | 3 — High                          |
| ----------------------- | ----------------------- | ----------------------- | --------------------------------- | --------------------------------- |
| **Scope Breadth**       | Single file             | 2–3 files, one module   | Multiple modules                  | Cross-system / cross-repo         |
| **Integration Surface** | No new integrations     | One new internal API    | Multiple internal or one external | Multiple external / third-party   |
| **Novelty**             | Existing pattern reused | Minor variation         | New pattern in familiar domain    | New pattern in unfamiliar domain  |
| **Data / Migration**    | No data changes         | Additive, backward-safe | Schema change with migration path | Destructive or no rollback path   |

### Scoring Procedure (follow in order)

1. For each of the four dimensions, write one line of **evidence** (file count, named integrations, matched pattern, migration note) before choosing the score. A score without evidence is not allowed.
2. Pick the **lowest score whose column matches the evidence**; if evidence sits between two columns, take the higher (see Notes).
3. Add the four scores, then apply the threshold mapping below literally. Do not adjust the level by "feel".
4. Do not default to `MEDIUM`: a 1-file tweak is `TRIVIAL`/`LOW`, a cross-module change with an external service is `HIGH`. Let the arithmetic decide.
5. Record the inherited `risk_level` in the artifact for the tier floor, but do **not** add it to the sum.

### Dimension Definitions

- **Scope Breadth** — How many files, modules, or systems the change touches. Read from the Implementation Units' `Files` lists.
- **Integration Surface** — Number and kind of APIs/services the solution must connect to. Pull from the Research Findings `Patterns Found` and `Tech Stack`.
- **Novelty** — Whether the approach reuses an existing local pattern or introduces a new one. Compare the chosen approach against `Patterns Found` confidence levels.
- **Data / Migration** — Whether data schemas change and whether the change is reversible. Read from the Design's `Operational / Rollout Notes` draft. A new format with no existing data is "Additive".

## Complexity Level Thresholds

Map the total score to a complexity level:

```
total = sum(scope_breadth, integration_surface, novelty, data_migration)

if total >= 9:
  complexity = VERY_HIGH
elif total >= 6:
  complexity = HIGH
elif total >= 3:
  complexity = MEDIUM
elif total >= 1:
  complexity = LOW
else:
  complexity = TRIVIAL
```

| Level     | Score Range | Typical Profile                                     |
| --------- | ----------- | --------------------------------------------------- |
| TRIVIAL   | 0           | Single-file tweak, no integrations                  |
| LOW       | 1–2         | Small feature, one module, no migration             |
| MEDIUM    | 3–5         | Multi-module feature, one integration, additive     |
| HIGH      | 6–8         | Cross-module or external integration, schema change |
| VERY_HIGH | 9–12        | Cross-system, new pattern, destructive migration    |

## Mapping to Interaction Mode

| Mode      | Pause Behavior                                          |
| --------- | ------------------------------------------------------- |
| Detailed  | Always pause; show units and complexity; ask to proceed |
| Smart     | Pause **only** if `complexity = VERY_HIGH`              |
| Autopilot | Never pause; auto-proceed                               |

**Smart mode also pauses if any of these flags are true** (regardless of complexity):

- Research phase reported HIGH risk and `patterns_found_count < 3`
- 3+ learning gaps were identified in the Scope phase
- The selected approach has no local pattern precedent (Novelty = 3)
- The unit count exceeds the coverage cap (see [plan-coverage-rules.md](plan-coverage-rules.md))

## Mapping to Plan Tier

Complexity feeds into tier selection in the Generate phase:

| Complexity       | Default Tier | Rationale                                  |
| ---------------- | ------------ | ------------------------------------------ |
| TRIVIAL / LOW    | Fast         | Short plan; minimal structure needed       |
| MEDIUM           | Standard     | Full template; phased units; risk table    |
| HIGH / VERY_HIGH | Deep         | Full template + alternatives + rollout ops |

The table is the **complexity-only** default. Design then applies the risk floor with `recommend_tier(complexity, risk_level)` and writes the result as `tier_recommended`. See [plan-tier-selection.md](plan-tier-selection.md) for the complete algorithm, including user preference and the `--deep` override (which does not change `complexity` or `tier_recommended`).

## Worked Example

**Task:** Migrate session storage from in-memory to Redis.

| Dimension           | Score | Reasoning                                         |
| ------------------- | ----- | ------------------------------------------------- |
| Scope Breadth       | 2     | Multiple modules: middleware, store, client       |
| Integration Surface | 2     | One external system (Redis)                       |
| Novelty             | 2     | Redis is new to the codebase                      |
| Data / Migration    | 1     | Additive; sessions expire naturally               |
| **Total**           | **7** | **Complexity: HIGH**                              |

Risk (confirmed Security: session handling, HIGH) is inherited and not scored. Tier: complexity HIGH → Deep; `tier_recommended: deep`.

Result: In Smart mode, this would **not** pause (HIGH, not VERY_HIGH) unless the secondary flags trigger (e.g., 3+ learning gaps).

## Error Handling

| Scenario                                                         | Recovery                                 |
| ---------------------------------------------------------------- | ---------------------------------------- |
| Risk level missing from Research artifact                        | Default to MEDIUM for the tier floor; log warning |
| Implementation Units not yet drafted                             | Defer scoring until units exist          |
| Two dimensions conflict (e.g., no migration but destructive note) | Use the higher score; log warning        |
| Score lands exactly on a threshold (e.g., 6)                     | Round up to the higher level (HIGH)      |

## Notes

- Complexity is a planning aid, not a precise metric — favor conservative (higher) scoring when uncertain
- The complexity value must be written to the Design Artifact for the Generate phase to consume
- If the user overrides the tier in the Generate phase, complexity is preserved for reference but no longer drives tier selection
