---
title: Plan Tier Selection
description: Reference for the Generate phase. Defines the Fast/Standard/Deep tier model, the selection algorithm that combines complexity, risk, and user preference, and the template sections each tier requires.
type: reference
version: 1.2
timestamp: "2026-10-01"
---

# Plan Tier Selection

This file documents the tier system used by the **Generate** phase (Phase 4) to right-size the final plan document. It defines three tiers, the selection algorithm, the template sections each tier requires, and how tier choice interacts with the interaction mode.

## When to Apply

Tier selection happens at the start of the Generate phase, after reading the Design Artifact (which carries the `complexity` field) and the Research Findings (which carry the `risk_level`). The chosen tier determines which sections of the [Final Plan template](templates/artifacts/final-plan.md) are rendered and how much structure the plan contains.

## The Three Tiers

| Tier         | Use When                                           | Length    | Sections Included                                                |
| ------------ | -------------------------------------------------- | --------- | ---------------------------------------------------------------- |
| **Fast**     | Trivial/low complexity, straightforward work       | 1–2 pages | Overview, High-Level Design, Units (single phase), Risks (brief) |
| **Standard** | Medium complexity, typical feature work            | 2–4 pages | All template sections, phased units, full risk table             |
| **Deep**     | High/very-high complexity, cross-system, high-risk | 4+ pages  | All template sections + alternatives + rollout ops + monitoring  |

## Selection Algorithm

Tier selection is **two pure functions**. Run them step by step with the real values; never shortcut to a "typical" tier.

Values are compared case-insensitively (`HIGH` = `High`). `risk_level` comes from the Research Findings; `complexity` from the Design Artifact.

```
# A. Recommendation — computed in the Design phase (Step 4) and re-computed in Generate (Step 1).
#    Depends ONLY on complexity and risk. Never on user input or --deep.
function recommend_tier(complexity, risk_level):
  # 1. Complexity-driven default
  if complexity in [TRIVIAL, LOW]:   tier = Fast
  elif complexity == MEDIUM:         tier = Standard
  else:  # HIGH or VERY_HIGH         tier = Deep

  # 2. Risk floor (see table below) — may only raise the tier
  if risk_level == HIGH and tier == Fast: tier = Standard
  if risk_level == CRITICAL:              tier = Deep
  return tier

# B. Selection — computed in the Generate phase (Step 1).
function select_tier(complexity, risk_level, user_preference, force_deep):
  recommended = recommend_tier(complexity, risk_level)
  floor       = risk_floor(risk_level)            # Fast | Standard | Deep

  if force_deep:                       return Deep                  # explicit user request; always honored
  if user_preference == "auto":        return recommended           # Auto = the algorithm, NOT a fixed tier
  # Explicit tier: honor it, but never go below the risk floor
  return max(user_preference, floor)   # order: Fast < Standard < Deep
```

`tier_recommended` is **always** `recommend_tier(...)` — it is never changed by user preference or `--deep`. `tier` is `select_tier(...)`. When they differ, the plan records an auditable override.

### Inputs

| Input             | Source                                              | Values                                |
| ----------------- | --------------------------------------------------- | ------------------------------------- |
| `complexity`      | Design Artifact                                     | TRIVIAL, LOW, MEDIUM, HIGH, VERY_HIGH |
| `risk_level`      | Research Findings Artifact                          | LOW, MEDIUM, HIGH, CRITICAL           |
| `user_preference` | User (asked in Generate Step 1; see mode behavior)  | `fast`, `standard`, `deep`, or `auto` |
| `force_deep`      | Orchestrator context (`--deep` flag, SKILL.md)      | `true` or `false` (default `false`)   |

### Risk Floor

The risk level sets a **minimum tier** that user preference cannot override:

| Risk Level | Minimum Tier |
| ---------- | ------------ |
| LOW        | Fast         |
| MEDIUM     | Fast         |
| HIGH       | Standard     |
| CRITICAL   | Deep         |

Rationale: High/critical risk mandates enough structure to capture alternatives, rollout, and rollback — even if the user wants a short plan.

### Anti-Default Rules (read before computing)

- **`Standard` is not a neutral default.** It is the result only for `MEDIUM` complexity (or a `HIGH` risk floor lifting a Fast result). `HIGH`/`VERY_HIGH` complexity → **Deep**; `TRIVIAL`/`LOW` → **Fast** unless risk lifts it.
- **Compute, then write.** Fill the function inputs with the actual `complexity` and `risk_level`, evaluate, and only then write `tier_recommended`. Do not copy a tier from an example in this file.
- **Auto means "use `tier_recommended`".** Never substitute `Standard` because it is the middle option.

### Deep Override (`--deep`)

The user can force a Deep plan in **any** interaction mode (including Autopilot and Smart) by invoking `/plan --deep <task>` (parsing rules in [SKILL.md](../SKILL.md#skill-invocation)).

- `force_deep = true` → `tier = deep`, regardless of complexity, risk, or `user_preference`. The tier question is **not asked**, in any mode.
- `tier_recommended` still holds the algorithm's result, so the override is auditable (`tier: deep`, `tier_recommended: fast`, etc.).
- Deep only adds structure, so it never violates the risk floor.
- The Smart-mode "tier is Deep" pause does **not** fire for a `--deep` plan (the user already chose it). CRITICAL-risk pause still applies.
- Because Design runs before Generate, the Design phase also receives `force_deep` so it produces the material a Deep plan needs (≥ 2 alternatives, rollout draft, integration map) — see [design.md](../modules/design.md) Steps 4–5.

## Tier Section Requirements

### Fast Tier

Required sections:

- Overview (1–2 sentences)
- High-Level Technical Design (one of: Mermaid, pseudo-code, or data-flow map)
- Implementation Units (single phase, 1–3 units)
- Risk Analysis & Mitigation (brief table, 1–2 rows)
- Related Learnings

Optional (skip if not applicable): Alternative Approaches, Operational Notes, Learning Gaps.

### Standard Tier

Required sections (all template sections):

- Overview
- High-Level Technical Design
- Implementation Units (phased, 2+ phases)
- Alternative Approaches Considered (at least 1)
- Risk Analysis & Mitigation (full table)
- Operational / Rollout Notes
- Related Learnings
- Learning Gaps

### Deep Tier

Required sections (all Standard sections, plus):

- Alternative Approaches Considered (at least 2, with side-by-side comparison)
- Risk Analysis & Mitigation (full table with impact ratings)
- Operational / Rollout Notes (must include: feature flags, monitoring, data migration, rollback plan, performance baseline)
- Explicit complexity and tier in frontmatter
- Cross-system integration map (data-flow or sequence diagram)

**Required does not mean invented.** On a Deep plan forced by `--deep` for a small change, a required item that genuinely does not apply (e.g., data migration for a doc-only change) is written as `Not applicable — <one-line reason>`. Never omit the item and never fabricate content to fill it.

## Interaction Mode Behavior

| Mode      | `user_preference`                                      | Tier Selection Behavior                                                                                   |
| --------- | ------------------------------------------------------ | --------------------------------------------------------------------------------------------------------- |
| Detailed  | Asked (prompt below), unless `force_deep`              | Ask the user; offer to override. `force_deep` → no question, announce "Deep plan forced by `--deep`"      |
| Smart     | `auto` (asked only if a pause trigger fires)           | Auto-select; pause **only** on the triggers below                                                         |
| Autopilot | `auto`                                                 | Auto-select; never pause                                                                                  |

`force_deep = true` overrides `user_preference` in every row.

**Smart mode pause triggers:**

- Selected tier is Deep **and `force_deep` is false** (signals complex work worth a review)
- User preference conflicts with risk floor (e.g., user wants Fast but risk is HIGH)
- Research phase reported CRITICAL risk (Security or Payments)

## Asking the User for Preference

In Detailed mode (or when Smart mode pauses), ask one question. **Build it from the computed values — every `<…>` placeholder below must be replaced; never print an example tier.**

```
Design complexity is <complexity> (score <total>/15) and risk level is <risk_level>.
I recommend the <tier_recommended> tier.
Which tier would you like for the plan?
  - Fast: Short plan, minimal structure (1-2 pages)
  - Standard: Full plan with phased units and risk table (2-4 pages)
  - Deep: Comprehensive plan with alternatives and rollout ops (4+ pages)
  - Auto: Use the recommendation (result: <tier_recommended>)
```

- Append ` [Recommended]` to the option that equals `tier_recommended`.
- If the risk floor makes an option unavailable (e.g., Fast at HIGH risk), keep it listed but say "(below risk floor — will be raised to <floor>)".
- Tip to include once in the question text: `/plan --deep` forces a Deep plan without this question.

Record the user's choice as the selected **`tier`** in the final plan frontmatter; preserve the algorithm's suggestion as **`tier_recommended`** so an override is auditable.

## Worked Examples

### Example 1: Low complexity, low risk

- `complexity = LOW`, `risk_level = LOW`, `user_preference = auto`
- `recommend_tier` → Fast. Auto → **Fast** (`tier_recommended: fast`).

### Example 2: Medium complexity, medium risk, auto

- `complexity = MEDIUM`, `risk_level = MEDIUM`, `user_preference = auto`
- `recommend_tier` → Standard. Auto → **Standard** (`tier_recommended: standard`).

### Example 3: Medium complexity, high risk, user wants fast

- `complexity = MEDIUM`, `risk_level = HIGH`, `user_preference = fast`
- `recommend_tier` → Standard. Floor (HIGH) = Standard. `max(Fast, Standard)` → **Standard**.
- Smart mode would pause (preference conflicts with risk floor).

### Example 4: High complexity, high risk, auto

- `complexity = HIGH` (score 8), `risk_level = HIGH`, `user_preference = auto`
- `recommend_tier` → **Deep** (HIGH complexity → Deep; not Standard). Auto → **Deep** (`tier_recommended: deep`).
- Smart mode pauses (Deep tier).

### Example 5: High complexity, critical risk (payments)

- `complexity = HIGH`, `risk_level = CRITICAL`, `user_preference = auto`
- `recommend_tier` → Deep. Auto → **Deep**. Smart mode pauses (Deep + CRITICAL).

### Example 6: `--deep` on a small change, Autopilot

- `complexity = LOW`, `risk_level = LOW`, `force_deep = true`, mode = autopilot
- `tier_recommended: fast`, `tier: deep`. No question asked, no pause. Required Deep sections without real content are written as `Not applicable — <reason>`.

## Error Handling

| Scenario                                | Recovery                                        |
| --------------------------------------- | ----------------------------------------------- |
| `complexity` field missing from Design  | Default to MEDIUM; log warning                  |
| `risk_level` missing from Research      | Default to MEDIUM; log warning                  |
| User provides invalid preference value  | Treat as `auto`; log warning                    |
| Selected tier conflicts with risk floor | Enforce risk floor; inform user of the override |
| Design's `tier_recommended` differs from `recommend_tier(complexity, risk_level)` | Recompute in Generate; the recomputed value is authoritative; log warning |
| `--deep` given but the phase artifact lacks the rollout/alternatives material | Generate writes `Not applicable — <reason>` for items that do not apply; never invents content |

## Notes

- Tier choice is recorded in the final plan's frontmatter as `tier: fast | standard | deep`
- The tier also influences the Tasks phase: Fast tier often produces 1–3 tasks; Standard 4–8; Deep 8+
- If the user overrides the tier (explicit choice or `--deep`), preserve the algorithm's recommendation in a `tier_recommended` field for audit
- Tier selection is the primary "right-sizing" mechanism — Small tasks → short plans; complex work → more structure (per Plan Skill core principles)
