---
title: "Daily counter algorithm for unique artifact naming"
timestamp: "2026-07-02"
category: pattern
domain: artifact-naming
tags: [id-generation, scoping, traceability, deterministic-naming]
severity: recommended
source: commit 3943146
---

# Daily Counter Algorithm for Unique Artifact Naming

## Problem

When multiple plans or artifacts are created on the same day, they need unique, deterministic, human-readable IDs to avoid collisions and enable traceability across sessions. Random UUIDs are opaque and hard to sort chronologically.

## Solution

Use a `YYYY-MM-DD-NNN-type` format with an auto-increment daily counter.

### Algorithm

```
1. Get current date in UTC (e.g., 2026-07-02)
2. Check target directory (e.g., docs/plans/.scope/) for files matching today's date
3. Count existing files matching YYYY-MM-DD-*.md
4. Set NNN = (count + 1), zero-padded to 3 digits
5. Generate ID: YYYY-MM-DD-NNN-scope
```

### Examples

- First plan of the day → `2026-07-02-001-scope`
- Second plan → `2026-07-02-002-scope`
- Tenth plan → `2026-07-02-010-scope`

### Error Handling

- If target directory does not exist, create it and start from `001`
- Count only files matching today's date pattern, not all files in directory

## Application

- Use for scope IDs in plan pipelines
- Adaptable to any artifact type (extracts, reviews, tasks)
- Combine with artifact type suffix (`-scope`, `-extract`, `-review`) for clarity

## Source

- `skills/plan/modules/1-scope/scope.md` — Step 6 implementation
- Commit `3943146`
