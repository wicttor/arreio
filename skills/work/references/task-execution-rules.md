---
title: Task Execution Rules
description: Authoritative reference for the Execute phase (and the gates Prepare records). Defines the status model, the per-task Red/Green/Refactor gates, the retry-limit and blocked-transition policy, the resume policy, the skip transition, the touched-files ledger and deviation policy, and the snapshot-and-continue regression policy. Execute and Prepare defer to these definitions; neither re-encodes them.
type: reference
version: 1.1
timestamp: "2026-10-23"
---

# Task Execution Rules

Authoritative reference for the **Execute** phase and the per-task gates Prepare records. Defines the **status model**, the per-task **Red/Green/Refactor** gates, the **retry-limit** and **blocked** transition, the **resume** policy, the **skip** transition, the **touched-files ledger** with its **deviation** policy, and the **snapshot-and-continue** regression policy. Execute enforces these; Prepare records the applicable set and thresholds read-only; neither re-encodes them.

## Core Invariants (inherited from `/plan`)

- **One Acceptance Criterion per task** — each task carries exactly one AC and exactly one `files.test` asserting it.
- **Test-first** — every task runs Red → Green → Refactor; the failing test is written and confirmed **before** implementation.
- **Execute the tasks as given** — never merge, split, add, or drop a task during execution. Anything the task list does not cover is a deviation (below), not new work.
- **Forward-only status** — a task never moves backward (`completed` is never re-opened; checkboxes are ticked forward only, never reset).

## Status Model (authoritative)

```
not-started -> in-progress -> for-review -> completed
                    |              |
                    +-> blocked    +-> blocked   (Review/Standalone Review rejects)
not-started -> skipped            (explicit user confirmation only)
```

| status        | Set by                           | Meaning                                                                                 | Checkboxes (task AC / index) |
| ------------- | -------------------------------- | --------------------------------------------------------------------------------------- | ---------------------------- |
| `not-started` | `/plan` Tasks, Triage (ad-hoc)   | Not run yet                                                                             | `[ ]` / `[ ]`                |
| `in-progress` | Execute (mid-task)               | A gate is running; only valid while Execute is running or after an interruption         | `[ ]` / `[ ]`                |
| `for-review`  | Execute (Refactor gate passed)   | Implemented and green, awaiting Review's run-level checks (regression, scope, simplify) | `[ ]` / `[ ]`                |
| `completed`   | Review (checks clean for the task) | Verified: run-level checks passed for this task                                       | `[x]` / `[x]`                |
| `blocked`     | Execute or Review                | Could not reach a gate, or Review/Standalone Review rejected it; reason recorded        | `[ ]` / `[ ]`                |
| `skipped`     | Execute (user-confirmed)         | Deliberately not run; reason recorded                                                   | `[ ]` / `[ ]`                |

Rules:

- **Execute never writes `completed`.** Its terminal success is `for-review`. This keeps a task from being marked done and then reverted when Review finds a regression or scope creep.
- **Review promotes** `for-review` → `completed` per task (Review Step 4a) and ticks both checkboxes at that moment. A task that fails Review's per-task checks stays `for-review`.
- A task is `completed` only after Review, so the end state of a clean run is all `completed`; of a gated run, `for-review` tasks await `/review`.

## Per-Task Gates

| Gate         | Criteria (authoritative)                                                                                                                             | On pass                                 | On fail                                                                                               |
| ------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------- | ----------------------------------------------------------------------------------------------------- |
| **Red**      | The new test at `files.test[0]` exists and **fails for the right reason** — the assertion matching the AC fires; not a setup/import/compile error. | Proceed to Green                        | If it passes immediately: apply the Already-Satisfied rule below; if setup error: log and fix the test |
| **Green**    | The task's single AC test now passes **and** there is no new regression beyond the Prepare baseline (see Regression Policy).                         | Proceed to Refactor                     | Increment retry; on retry-limit → `blocked`                                                           |
| **Refactor** | Cleanup of naming/duplication/structure; the AC test stays green **and** no regression. No behavior change.                                          | Gates-passed transition (`for-review`)  | Revert the refactor; retry once; then `blocked`                                                       |

### Already-Satisfied Rule

If Red passes immediately, do not mark the task done on that observation alone:

1. Identify the existing code that satisfies the AC and cite its path in the gate-trace note.
2. Confirm the test asserts the AC (not something weaker) by reading it.
3. Make no production change; the touched-files ledger for the task is empty. Proceed through Refactor (a no-op is valid) and take the gates-passed transition with `already-satisfied: true`.

If the assertion is weaker than the AC, strengthen the test until it fails for the right reason, then continue normally.

## Retry-Limit and Blocked Transition

- **Default retry-limit per task: 2** attempts to reach Green from a confirmed Red.
- Reaching the limit without Green transitions the task to **`blocked`**:
  - Set frontmatter `status: blocked` with a recorded `reason` (the failing assertion snapshot, which gate failed, the last error).
  - Leave the index checklist as `- [ ]` and append `— blocked: <reason>`.
  - Per the execution mode: `inline`/`serial` pause and surface; `parallel` blocks only dependents in later waves.
- A `blocked` task is **not auto-retried** on resume — it is carried with its reason (see Resume Policy). To retry it, the user re-runs Work and explicitly proceeds (the task's `status` is reset to `not-started` only on an Edit & Retry of Triage/Prepare).
- A task whose dependency is `blocked` or `skipped` cannot run; it is carried as `not-started` with `ready: false` and listed in the Work Report as unreachable.

## Resume Policy (authoritative)

On re-entry (re-running Work), before running each task, read its task-file frontmatter `status`:

| status        | Action on resume                                                                       |
| ------------- | -------------------------------------------------------------------------------------- |
| `completed`   | Skip (never re-open); checkbox stays `- [x]`                                           |
| `for-review`  | Skip in Execute (already green); carried to Review, which promotes it or keeps it      |
| `blocked`     | Carry with recorded reason; not auto-retried                                           |
| `skipped`     | Carry with recorded reason; not auto-retried                                           |
| `in-progress` | Re-enter the cycle at the last-run gate; do not tick any checkbox until the gates pass |
| `not-started` | Run the full Red → Green → Refactor cycle                                              |

**Dependency satisfaction.** A dependency is satisfied when it is `completed` **or** `for-review` (green, awaiting Review's verification). Without this, no dependent task could start in the same run, because Execute only takes tasks to `for-review`. A dependency that is `blocked`, `skipped`, `not-started`, or `in-progress` is not satisfied.

The orchestrator's quality gate #4 requires the end state to be coherent: no task left `in-progress`; checkboxes match statuses (see the Status Model table).

## Skip Transition

- Skipping a task requires **explicit user confirmation** — never auto-skip.
- Set frontmatter `status: skipped` with a recorded `reason`.
- Leave the index checkbox as `- [ ]` and append `— skipped: <reason>`.
- A `skipped` task is not auto-retried on resume (Resume Policy).

## Gates-Passed Transition (Execute) and Complete Transition (Review)

When the Refactor gate passes, **Execute**:

- Sets frontmatter `status: for-review`. No checkbox changes.

When Review's checks pass for the task, **Review**:

- Sets frontmatter `status: completed`.
- Flips the task file's `## Acceptance Criteria` checkbox to `- [x]`.
- Ticks that task's row in `docs/tasks/<work-id>/index.md` from `- [ ]` to `- [x]` (forward only).

## Touched-Files Ledger and Deviations (authoritative)

Scope creep is detected from what a task actually changed, not from memory of what it did.

**Ledger.** Around each task, Execute records the set of changed paths: take the working-tree change list before Red (`git status --porcelain` or the agent's equivalent) and again after Refactor; the task's `touched-files` is the difference. Exclude the Work run's own bookkeeping — the task files and `index.md` under `docs/tasks/<work-id>/`. Outside a git repository, record the files the task wrote or edited from the agent's own actions. In `parallel` mode the ledger is taken per wave and attributed to tasks by the files each one declared (waves are file-disjoint — see [execution-mode-selection.md](execution-mode-selection.md)).

**Declared set.** A task's declared set is `files.create` ∪ `files.modify` ∪ `files.test`.

**Undeclared files.** A touched path outside the declared set is handled when it is found, before the next gate:

| Situation                                                                              | Action                                                                                                  |
| -------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------- |
| The change is not needed for the AC test to pass                                       | Revert it immediately. Not a deviation.                                                                 |
| The AC test cannot pass without it (e.g. a missing barrel export, a shared type)        | Keep it as a **deviation**: record `{task-id, path, why-required}` in the ledger and continue the cycle. |
| A manifest or lockfile changed by installing a package the Green step needs            | Allowed; record it as a deviation with kind `dependency`.                                               |

Deviations never expand the task list and never change the AC. They are reported in the Execution Log and Work Report and are scope-creep findings at Review (Review Step 3), which keeps the affected task at `for-review` until the user accepts them. Execute never decides on the user's behalf that a deviation is fine.

**Plan defects.** If the task cannot be completed as specified (the AC contradicts the code, a declared file does not exist and cannot be created, the test path is wrong), do not improvise: the task goes `blocked` with the reason, and the Work Report lists it as a plan defect for the user to fix in the plan or task file.

## Snapshot-and-Continue Regression Policy (authoritative)

When Prepare recorded `baseline: snapshot-and-continue` (the suite was red at baseline), a Prepare-recorded **known-failing test set** is the snapshot. Execute's regression gate behaves as follows:

- A failing test in the snapshot is **not** a regression (it was already failing).
- A **new** failing test (not in the snapshot) **is** a regression and fails the Green/Refactor gate.
- A snapshot test that now **passes** is an improvement, not a regression (do not block on it; record it for Review).

When `baseline: green`, the snapshot is empty — any failure is a regression.

When `baseline: red` without a snapshot-and-continue decision, Prepare must resolve the policy before Execute runs (it is a Prepare Smart pause trigger).

## Mid-Task Interruption

If Execute is interrupted mid-task:
- Set frontmatter `status: in-progress` (so a resume re-enters the cycle at the right gate).
- Do **not** tick any checkbox.
- On resume, re-enter at the last-attempted gate for that task.

## Per-Task Execution Cycle (Execute Step 3 follows this)

```
for each runnable task (status not-started | in-progress):
  snapshot working-tree change list (ledger start)
  gate Red:
    write/confirm the AC test at files.test[0]
    run it; assert it fails for the right reason
    if passes immediately -> Already-Satisfied rule
  gate Green:
    implement minimum code in files.create / files.modify
    run the AC test; assert green with no new regression (snapshot policy)
    on fail -> increment retry; on retry-limit -> blocked
  gate Refactor:
    clean up; re-run the AC test; assert green with no regression
    on fail -> revert refactor; retry once -> else blocked
  ledger end: touched-files = change list now - ledger start; handle undeclared files
  gates-passed transition:
    status -> for-review   (Review promotes to completed and ticks checkboxes)
```

## Failure-Condition Reference

| Trigger                                                 | Outcome per this reference                                               |
| ------------------------------------------------------- | ------------------------------------------------------------------------ |
| Red passes immediately on a `not-started` task          | Already-Satisfied rule; `for-review` with `already-satisfied: true`      |
| Green not reached within retry-limit (2)                | Task → `blocked` with reason + assertion snapshot                        |
| Refactor introduces a regression                        | Revert the refactor; retry once; then `blocked`                          |
| Task cannot be done as specified (plan defect)          | Task → `blocked`; listed as a plan defect in the Work Report             |
| Undeclared file touched but not needed                  | Revert it; no deviation                                                  |
| Undeclared file touched and required for Green          | Recorded deviation; Review keeps the task at `for-review`                |
| New regression on a `for-review` task's Refactor re-run | Surfaced as a Review Smart pause trigger (do not auto-mark)              |
| Runner command fails (not an assertion failure)         | Category 6 recovery per [error-handling.md](error-handling.md)           |

## Notes

- This reference is the single source of truth for the status model, gate criteria, the retry-limit, blocked/skip/transition/resume rules, the ledger and deviation policy, and the snapshot-and-continue regression policy.
- Prepare records the applicable set and thresholds **read-only** in the Execution Plan; Execute enforces them; Review verifies they were enforced (not re-defined inline).
- The 2-attempt default mirrors the per-phase retry-limit philosophy in [error-handling.md](error-handling.md) but is task-scoped (a blocked task is not a phase termination).
