---
title: Execution Log Artifact
description: Template for the Execution Log produced by the Execute phase. Carries the per-task result table (outcome + gate trace + reason), aggregator counts, and the regression-detection summary; consumed by Review.
type: template
version: 1.1
timestamp: "2026-10-23"
---

# Execution Log Artifact

The product of the **Execute** phase is an Execution Log: a per-task result table with outcomes (`for-review` / `blocked` / `skipped`), the touched-files ledger, the Red/Green/Refactor gate trace, and any `reason`, plus aggregator counts and a regression-detection summary. Review consumes it.

## Schema

```yaml
execute-id: YYYY-MM-DD-NNN-execute
prepare-id: YYYY-MM-DD-NNN-prepare
triage-id: YYYY-MM-DD-NNN-triage
work-id: YYYY-MM-DD-NNN
work-branch: work/<short-description> | null   # inherited from the Work Manifest
input-shape: plan-based | task-file | ad-hoc
interactionMode: detailed | smart | autopilot
executionMode: inline | serial | parallel
status: complete
timestamp: ISO-8601 timestamp

results:                                 # one row per task in execution-list
  - task-id: <work-id>-T<NN>
    outcome: for-review | blocked | skipped
    touched-files: [path, ...]             # change list after minus before, excluding docs/tasks/<work-id>/
    already-satisfied: false | true        # true when Red passed immediately and no production change was needed
    gate-trace:
      red: { passed: true | false, at: ISO-8601, note: "..." }
      green: { passed: true | false, at: ISO-8601, note: "..." }
      refactor: { passed: true | false, at: ISO-8601, note: "..." }
    retries-used: 0 | 1 | 2
    reason: null | "[failing assertion snapshot, which gate failed, last error]"   # blocked/skipped only

deviations:                              # undeclared files kept because the AC could not pass without them
  - { task-id: <work-id>-T<NN>, path: path/to/file, why-required: "[reason]", kind: file | dependency }
plan-defects:                            # tasks blocked because they cannot be done as specified
  - { task-id: <work-id>-T<NN>, reason: "[what contradicts what]" }

aggregators:
  total: <N>
  for-review: <N>
  blocked: <N>
  skipped: <N>
  in-progress-left: 0                      # must be 0 for task-status coherence (orchestrator gate #4)

regression-detection:
  baseline-state: green | snapshot-and-continue
  new-regressions: [test-path or test-id, ...]   # failures beyond the known-failing snapshot
  snapshot-now-passing: [test-path or test-id, ...] # baseline failures now passing (improvements)

final-index-state:
  checklist-matches-task-files: true       # docs/tasks/<work-id>/index.md matches task frontmatter status
  uncompleted-rows: [<task-id>, ...]       # rows still - [] (blocked/skipped)
```

In `detailed` mode only, also save the Execution Log to `docs/plans/.work/.execute/<execute-id>.md`. In `smart`/`autopilot` mode, do not write it; pass it to the next phase in context.

## Validation Rules

- **execute-id:** Required. Format `YYYY-MM-DD-NNN-execute`.
- **prepare-id, triage-id, work-id, work-branch, input-shape:** Required, inherited (cross-phase consistency).
- **interactionMode, executionMode:** Both required, identical to the Prepare artifact.
- **results:** Required. One row per task in `execution-list`. Each row:
  - `outcome` one of `for-review`, `blocked`, `skipped` (Execute never writes `completed`)
  - `gate-trace` with the three gates; for a `for-review` task all three `passed: true`
  - `touched-files` recorded for every `for-review` task (empty when `already-satisfied`)
  - `reason` recorded for `blocked`/`skipped`; `null` for `for-review`
- **aggregators:** Required. `in-progress-left` must be `0` (task-status coherence — no task left `in-progress`).
- **regression-detection:** Required. `new-regressions` lists failures beyond the baseline snapshot (per the snapshot-and-continue policy in [task-execution-rules.md](../../task-execution-rules.md)).
- **final-index-state.checklist-matches-task-files:** Required, must be `true`; else Execute did not leave a coherent state (orchestrator quality gate #4 fails).
- **status:** Required. `complete`.

## Example (one blocked, rest completed)

```yaml
execute-id: 2026-08-07-003-execute
prepare-id: 2026-08-07-002-prepare
triage-id: 2026-08-07-001-triage
work-id: 2026-07-10-001
work-branch: work/redis-session-store
input-shape: plan-based
interactionMode: smart
executionMode: serial
status: complete
timestamp: 2026-08-07T15:30:00Z
results:
  - task-id: 2026-07-10-001-T01
    outcome: for-review
    touched-files: [src/lib/redis-client.ts, src/lib/session-store.ts, src/lib/redis-client.test.ts]
    already-satisfied: false
    gate-trace:
      red:    { passed: true, at: 2026-08-07T15:01:00Z, note: "fails on missing client" }
      green:  { passed: true, at: 2026-08-07T15:05:00Z, note: "all 3 scenarios green" }
      refactor: { passed: true, at: 2026-08-07T15:06:00Z, note: "thinned wrapper" }
    retries-used: 0
    reason: null
  - task-id: 2026-07-10-001-T02a
    outcome: blocked
    gate-trace:
      red:    { passed: true,  at: 2026-08-07T15:10:00Z, note: "fails on store impl" }
      green:  { passed: false, at: 2026-08-07T15:14:00Z, note: "TTL test still red after 2 retries" }
      refactor: { passed: false, at: null, note: "skipped (green not reached)" }
    retries-used: 2
    reason: "Green gate: TTL test 'returns null after 1s' fails after 2 retries; TTL not propagated to Redis SET"
deviations: []
plan-defects: []
aggregators:
  total: 2
  for-review: 1
  blocked: 1
  skipped: 0
  in-progress-left: 0
regression-detection:
  baseline-state: green
  new-regressions: []
  snapshot-now-passing: []
final-index-state:
  checklist-matches-task-files: true
  uncompleted-rows: [2026-07-10-001-T02a]
```

## Notes

- Task-status coherence (orchestrator quality gate #4) is verified at Review Step 0 and by the `final-index-state` block: every task `for-review`/`blocked`/`skipped` (or already `completed` from an earlier run), none `in-progress`, and no checkbox ticked before Review promotes the task.
- `new-regressions` feeds Review's regression check (a non-empty list is a Review Smart pause trigger).
- The gate trace + `reason` are the primary inputs to Review's learnings-capture (a blocked gate or a refuted assumption becomes a learning candidate).