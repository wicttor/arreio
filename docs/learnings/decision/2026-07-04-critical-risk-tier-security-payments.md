---
slug: critical-risk-tier-security-payments
type: decision
domain: planning
priority: important
applicability:
  current_project: 10
  general: 8
tags: [risk-assessment, security, planning, safety-nets, high-stakes]
created_at: "2026-07-04T00:00:00Z"
updated_at: "2026-07-04T00:00:00Z"
source:
  type: commit
  reference: aa21a87
  extracted_at: "2026-07-04T00:00:00Z"
confidence: high
---

# Introduce CRITICAL Risk Tier Above HIGH for Security/Payments Areas

## Problem

The risk detection matrix for implementation planning had only three levels: LOW, MEDIUM, and HIGH. Both "multiple high-risk areas" and "security/payments area touched" were classified as HIGH — equating two very different concerns. Touching the payments subsystem is not the same risk category as touching two mildly-risky service boundaries, yet both produced the same classification and the same tier recommendation.

## Solution

Add a **CRITICAL** risk tier that takes unconditional precedence whenever security or payments areas are detected, regardless of other signals:

```
if any_area_is_security_or_payments:
  risk_level = CRITICAL
elif high_risk_count >= 2:
  risk_level = HIGH
elif any_area_is_api_migration_logic_infra:
  risk_level = MEDIUM
else:
  risk_level = LOW
```

CRITICAL plans always recommend external research, regardless of local pattern count:

| Risk Level | Patterns Found | Decision |
|------------|---------------|----------|
| **CRITICAL** | 0–2 | Recommend external |
| **CRITICAL** | 3+ | Recommend external |

## Decision Rationale

- **Security and payments are special:** Mistakes in these areas have outsized consequences (data breach, financial loss, legal liability) compared to other high-risk areas.
- **Precedence matters:** The CRITICAL check fires _before_ HIGH, so a plan touching both payments and 3+ other high-risk areas stays CRITICAL (not demoted to HIGH by the multi-area path).
- **External research is non-negotiable:** For CRITICAL areas, local codebase patterns are insufficient — the team must consult external security/payments best practices.

## Application

- Used in `skills/plan/references/high-risk-detection.md` during the Research phase
- CRITICAL-level plans force the `standard` or `deep` tier regardless of other complexity factors
- Triggers mandatory external research in both `detailed` and `smart` interaction modes

## Related Learnings

- [Five-dimension complexity assessment framework](../decision/complexity-assessment-framework-2026-07-04.md) — risk_level inherits from this matrix; CRITICAL is now a valid value
