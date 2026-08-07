---
title: "Confirm-before-persist ordering in retryable pipelines"
timestamp: "2026-08-07"
category: pattern
domain: skill-design
tags: [pipelines, confirmation, idempotency, ordering, retry, side-effects]
severity: important
source: commit 40b4808
applicability:
  current_project: 9
  general: 9
related:
  - idempotent-index-upsert-by-id-2026-08-07
  - interaction-mode-propagation-2026-07-02
---

# Confirm-Before-Persist Ordering in Retryable Pipelines

## Problem

Two pipeline phases persisted their artifact BEFORE presenting the confirmation step, and the confirmation offered "Edit & Retry." Each retry re-ran save + index unconditionally:

- Phase saved the file, appended a row to the index (blind append), THEN asked "proceed / edit / retry / abort."
- A user picking "Edit & Retry" re-ran the same steps, appending ANOTHER index row — duplicates accumulated.
- A later "Abort" left an artifact + index row already written; nothing was gated by the decision.

## Solution

In any phase whose confirmation includes "Edit & Retry" or "Abort":

1. Run the cheap, in-memory steps (render, select, ID assignment).
2. Present the confirmation (per `interactionMode`) and capture the decision.
3. Only on Proceed (or any auto-proceed path) run the side-effecting steps: write the artifact file and update the index.
4. Abort = write nothing. Edit & Retry = loop back to step 1 reusing the same ID; nothing to undo.

Persisting is the LAST side effect, gated by the decision — never before it.

## Prevention

- Order phases as: produce-in-memory → confirm → persist + register.
- Any side-effecting step (file write, index row) must come AFTER the confirmation gate, not before it.
- Pair with idempotent index registration (upsert by id) so even out-of-order retries cannot duplicate.

## Source

- `skills/plan/modules/generate.md`, `skills/plan/modules/tasks.md` — confirmation moved before save+index (Generate Steps 4→5; Tasks Steps 5→6→7→8)
- Commit `40b4808`