---
plan-id: 2026-01-01-001
type: plan
title: "Saves milestone"
status: ready
source: evals/fixtures/milestone-source.md#8-saves-milestone
tier: standard
---

# Saves milestone

## Overview

Durable saves. **Out of scope:** economy rules, networking.

## Source Coverage

| Source item | Title | Units / Outcome |
| --- | --- | --- |
| 2.1 | Core seams | U1 |
| 2.2 | Journal | U2 |
| 2.3 | Save and load | U3 |

## Implementation Units (Phased)

### Phase 1: Foundation

- U1. **Core seams**
  - **Source:** 2.1
  - **Dependencies:** None
  - **Files:**
    - Create: `src/core/FSResult.h`, `src/core/FSClock.h`, `src/core/FSFileSystem.h`
    - Test: `tests/core/CoreSeamsTests.cpp` (`U-CORE-01..02`)
  - **Acceptance Criteria:**
    - Seams compile engine-free and fakes record operations.

- U2. **Journal**
  - **Source:** 2.2
  - **Dependencies:** U1
  - **Files:**
    - Create: `src/persistence/Journal.cpp`
    - Test: `tests/persistence/JournalTests.cpp` (`U-JRN-01..03`, `FI-06`)
  - **Acceptance Criteria:**
    - Replay applies only records after the committed sequence.

### Phase 2: Integration

- U3. **Save and load**
  - **Source:** 2.3
  - **Dependencies:** U1, U2
  - **Files:**
    - Create: `src/persistence/SaveWriter.cpp`
    - Test: `tests/persistence/SaveTests.cpp` (`U-SAVE-01`)
  - **Acceptance Criteria:**
    - Load picks the newest valid file among live, `.old` and backups.

## Open Decisions

None.
