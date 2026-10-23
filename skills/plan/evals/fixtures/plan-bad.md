---
plan-id: 2026-01-01-002
type: plan
title: "Saves milestone"
status: complete
tier: deep
---

# Saves milestone

## Source Coverage

| Source item | Title | Units / Outcome |
| --- | --- | --- |
| 2.1 | Core seams | U1, U2, U3, U4 |
| 2.2 | Journal | U6 |

## Implementation Units (Phased)

- U1. **Results**
  - **Source:** 2.1
  - **Dependencies:** None
  - **Files:**
    - Create: seams and matching implementations as needed

- U2. **Clock**
  - **Source:** 2.1
  - **Dependencies:** None
  - **Files:**
    - Create: `src/core/FSClock.h`

- U3. **Fake filesystem**
  - **Source:** 2.1
  - **Dependencies:** U2

- U4. **Builders**
  - **Source:** 2.1
  - **Dependencies:** U6

- U6. **Journal**
  - **Source:** 2.2
  - **Dependencies:** U1

- U5. **Contract review gate C1**
  - **Dependencies:** U1
