---
title: Plan Coverage Rules
description: Reference for Scope, Design, and Generate. Defines the source of truth, the Source Inventory, the unit-per-source-item mapping, the unit cap, concrete-file rules, Open Decisions, and the checks that scripts/check-plan.py enforces.
type: reference
version: 1.0
timestamp: "2026-10-23"
---

# Plan Coverage Rules

A plan implements a **source of truth**. These rules keep the plan the same size and shape as that source. [scripts/check-plan.py](../scripts/check-plan.py) enforces rules 1–8 mechanically; run it, do not re-implement it.

## Contents

- Source of truth and Source Inventory
- Mapping rules (1–8)
- Source Coverage table format
- Open Decisions
- Manual fallback checklist

## Source of truth and Source Inventory

The **source of truth** is the document section that already defines the work: a milestone's numbered steps, a spec section, an issue with a checklist. Scope Step 5 identifies it. When there is none, the user's prompt is the source (`source: prompt`) and the inventory is built from its Success Criteria.

The **Source Inventory** lists the source's items, using the source's own IDs and wording:

```yaml
source: doc/content/docs/implementation-plan.mdx#8-m2-souls-and-saves   # or `prompt`
source_items:
  - id: "2.1"
    title: "Core seams and shared types"
    tests: [U-CORE-01..05]          # test IDs named by the source, if any
exclusions:                          # things the source says are not in scope
  - "U-SOUL-05 (M6)"
  - "Hub economy (M3)"
```

Never invent items, never rename IDs, never reorder items that the source orders.

## Mapping rules

1. **One unit per source item is the default.** Each unit carries `Source: <item id>`; every unit has one.
2. **Every item is covered or excluded.** An excluded item needs a reason that quotes or points at the source (e.g. `Excluded — source says "Not in M2"`).
3. **Merge before you split.** Merge units that share one source item and one file set. Split one item into several units only when a single unit would exceed 5 files or about one day; write the reason in the Source Coverage table.
4. **Unit cap.** Units ≤ 1.5 × covered source items (rounded up). Above the cap, merge, or add a `Justification:` line under the Source Coverage table. Never exceed it silently.
5. **Unit IDs follow document order** (`U1`, `U2`, … ascending). Letter suffixes (`U2a`) are reserved for the Tasks phase. If a unit must be added late, renumber the plan before saving; IDs are stable only after the plan is saved.
6. **Dependencies point backwards.** A unit depends only on earlier units. Phases are dependency layers; a phase never contains a lower-numbered unit than the phase before it.
7. **Files are concrete.** Every path in `Files` is an exact repository-relative path. A pattern is allowed only for a generated set, with its count (e.g. `` `tests/M2/*Tests.cpp` (6 files) ``). The phrases "as needed", "if required", "where needed", "etc." are not allowed. If a path is unknown, put it in Open Decisions.
8. **Tests are named once.** Each source test ID belongs to the unit that owns its behaviour. A closing gate unit may list all test IDs; any other duplicate is a warning.
9. **No new gates.** Do not add units or blocking steps for work the source does not contain (contract reviews, spec rewrites, extra research units). Do not change accepted source documents. Put the doubt in Open Decisions.
10. **Criteria stay verifiable.** A unit has one or more Acceptance Criteria, each a single checkable outcome. The Tasks phase turns each criterion into one task; it does not change the unit count.

## Source Coverage table

Rendered in the plan under `## Source Coverage`:

```markdown
| Source item | Title | Units / Outcome |
| --- | --- | --- |
| 2.1 | Core seams and shared types | U1 |
| 2.2 | Character state, deltas | U2, U3 |
| 2.7 | Crash injection | Excluded — source cut list defers it |

Justification: U2/U3 split because the registry exceeds 5 files.
```

`Justification:` is required only when the unit cap is exceeded or a source item is split across units.

## Open Decisions

Questions the plan cannot resolve from the source go in `## Open Decisions`, one line each:

```markdown
- **OD1:** [question] — Recommended: [default and why] — Affects: U4, U6
```

Rules: list a recommended default; name the affected units; never edit the source or add a unit to resolve it; write `None.` when empty. A unit affected by an open decision may still be planned with the recommended default, marked `(assumes OD1)`.

## Manual fallback checklist

When Python is unavailable, verify the same things by hand and report the result in one line:

- [ ] `source:` frontmatter present; `## Source Coverage` and `## Open Decisions` sections present
- [ ] Every inventory item has units or an exclusion with a reason; no unit lacks `Source:`
- [ ] Table units match unit `Source:` fields
- [ ] Unit count ≤ ceil(1.5 × covered items), or justified
- [ ] Unit IDs ascend in document order; every dependency is an earlier unit
- [ ] No vague phrases in `Files`
- [ ] Every test ID the source names appears in the plan
