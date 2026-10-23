---
plan-id: 2026-01-01-003
type: plan
title: "Saves milestone"
status: complete
source: prompt
tier: standard
---

# Saves milestone

## Source Coverage

| Source item | Title | Units / Outcome |
| --- | --- | --- |
| 2.1 | Core seams | U1 |
| 2.2 | Journal | U2 |

Justification: 2 source items span 9 planned files.

## Implementation Units (Phased)

- U1. **Core seams**
  - **Source:** 2.1
  - **Dependencies:** None
  - **Files:**
    - Create: `src/core/Existing.h`, `src/core/Clock.h`
    - Modify: `src/core/Missing.cpp`

- U2. **Journal**
  - **Source:** 2.2
  - **Dependencies:** U1
  - **Files:**
    - Create: `src/core/Clock.h`

## Open Decisions

None.
