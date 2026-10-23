# Implementation Plan

## 8. Saves milestone

Goal: durable character saves. Not in this milestone: economy rules, networking.

### 2.1 Core seams (S)
- Add `FSResult`, `FSClock`, `FSFileSystem` to `src/core/`.
- Tests: **U-CORE-01..02**

### 2.2 Journal (M)
- One JSON line per record, CRC per line, replay after the last committed sequence.
- Tests: **U-JRN-01..03**, **FI-06**

### 2.3 Save and load (L)
- Atomic write with `.old` fallback and three backups; load picks the newest valid file.
- Tests: **U-SAVE-01**

## 9. Economy milestone
### 3.1 Shops
