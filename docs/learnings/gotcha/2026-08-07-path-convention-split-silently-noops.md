---
title: "Path-convention split between a skill's refs and its data location silently no-ops"
timestamp: "2026-08-07"
category: gotcha
domain: process
tags: [paths, conventions, learnings-gate, silent-failure, drift]
severity: important
source: commit 40b4808
applicability:
  current_project: 10
  general: 7
related:
  - stale-cross-references-survive-renames-2026-07-04
  - learnings-gate-logic-2026-07-02
---

# Path-Convention Split Between a Skill's Refs and Its Data Location Silently No-ops

## Problem

Three path conventions for the same thing disagreed in one repo:

- The Plan skill's internal refs read `docs/learnings/index.md` (lowercase).
- A sibling skill (`arreio-init`) creates `docs/learn/index.md`.
- The actual learnings file is `docs/learnings/INDEX.md` (uppercase).

On case-sensitive Linux, the Plan skill's Learnings Gate searched for a path that didn't exist → it **silently treated learnings as empty every run** and no-op'd. No error, just missing context downstream. The gate's "skip silently if not found" recovery hid the misconfiguration.

## Solution

Pick one canonical path and make it consistent across (a) all `skills/**` internal references, (b) the skill that creates the data (`arreio-init`), and (c) the actual on-disk file. A read path in a skill is a contract — the producer (init) and the storage must match it exactly, including case.

When a convention change is intentional (e.g., adopting arreio's `docs/learn/`), update every reader in the same change; otherwise the unaffected readers silently break on a case-sensitive filesystem.

## Prevention

- For each persisted path a skill reads, grep the whole `skills/**` for that path and confirm the producer + storage agree (case included) before declaring the skill working.
- Treat "index not found → skip silently" as a **smell**: a misconfigured gate looks identical to "no learnings yet." Prefer a single explicit log distinguishing the two so path drift surfaces instead of hiding.
- On any path-convention decision, record it once (e.g., "arreio uses `docs/learn/`") and update all readers; do not leave half-migrated references.

## Source

- `skills/plan/**` — learnings path unified to `docs/learn/` (arreio convention, per session decision)
- `skills/work/**` — Work skill (Triage learnings gate) reads `docs/learn/index.md` per the same arreio convention; new skills authored against the canonical `docs/learn/` path, not the legacy `docs/learnings/` storage (session decision, 2026-08-07)
- Commit `40b4808`