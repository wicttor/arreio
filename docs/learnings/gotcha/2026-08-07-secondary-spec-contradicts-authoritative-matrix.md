---
title: "Don't re-encode an authoritative matrix as a contradicting secondary formula/list"
timestamp: "2026-08-07"
category: gotcha
domain: skill-design
tags: [single-source-of-truth, contradictions, decision-logic, templates, drift]
severity: important
source: commit 40b4808
applicability:
  current_project: 9
  general: 8
related:
  - 2026-07-04-error-handling-tables-enumerate-required-fields
  - specific-field-names-namespace-collisions-2026-07-04
---

# Don't Re-encode an Authoritative Matrix as a Contradicting Secondary Formula/List

## Problem

A decision lived in a rich reference matrix, but a downstream phase re-implemented it as a lossy formula that **contradicted** the matrix:

- `high-risk-detection.md` defined a risk × patterns matrix: **CRITICAL → always external** (even with 3+ patterns).
- `research.md` encoded the decision as `should_run_external_research = high_risk_detected AND patterns_found_count < 3` — which returns *false* for CRITICAL-with-3+ patterns. A critical Payments task with strong local patterns would skip external research.

The same class of bug appeared for section inclusion: the tier-selection matrix makes Alternative Approaches / Operational Notes / Learning Gaps **optional (➖)** for Fast tier, but the final-plan template's separate "Required Sections" table marked **all 8 sections ✅ required** — so every Fast plan was non-conformant.

## Solution

One source of truth per decision. A phase that consumes a decision must **defer to the authoritative reference**, not re-derive a secondary rule:

- The Research phase looks up its external-research decision directly in the risk × patterns matrix (the matrix is marked authoritative). No parallel formula.
- Section inclusion is tier-driven in the tier-selection reference only; templates must not re-declare a static "required sections" list that contradicts it. The all-✅ table was deleted; templates defer to the matrix.

## Prevention

- When a decision has a matrix/table, mark it authoritative; consumers reference it, they don't re-formulate it.
- If two documents describe the same rule, treat the duplication as a drift risk — converge to one and link from the other.
- New field/section/CIT: update the single source in the same change; never add a second list.

## Related Learnings

- `error-handling-tables-enumerate-required-fields` — the same SSoT theme, applied to enumerating required *fields*
- `specific-field-names-namespace-collisions` — naming consistency, one source of truth for field names

## Source

- `skills/plan/modules/research.md` (Step 3 defers to matrix) · `skills/plan/references/high-risk-detection.md` (matrix marked authoritative) · `skills/plan/references/templates/artifacts/final-plan.md` (all-✅ rules table deleted)
- Commit `40b4808`