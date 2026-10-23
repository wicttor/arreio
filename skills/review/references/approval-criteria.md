---
title: Approval Criteria
description: Authoritative reference for the Report phase. Defines how the final approval status (approved / changes-requested / rejected) is derived deterministically from the Findings tallies and the presence of any scope-creep flag. Report looks this up; it does not re-encode the rule.
type: reference
version: 1.1
timestamp: "2026-10-23"
---

# Approval Criteria

Authoritative reference for the **Report** phase (Step 1). Defines how the final **approval status** (`approved` / `changes-requested` / `rejected`) is derived deterministically from the Findings tallies (counts by severity) and the presence of any `scope-creep: true` finding. Report looks this reference up; it does not re-encode the rule.

## The Three Approval Statuses

| Status                | Meaning                                                | Merge implication                       |
| --------------------- | ------------------------------------------------------ | --------------------------------------- |
| `approved`            | The change is mergeable                                | Merge away; optionally address minor/nit |
| `changes-requested`   | Fix the listed issues before merge                     | Do not merge until the majors / creep are addressed |
| `rejected`            | Do not merge — a blocker means the change is unsound  | Do not merge; rework and re-review       |

## Decision Rule (authoritative)

> Report derives `approval-status` **deterministically** from the Findings tallies and the scope-creep flag. There is no reviewer discretion in the derivation. Do not apply a separate formula — this rule is the single source of truth.

```
let b = count of findings with severity == blocker
let m = count of findings with severity == major
let creep = any finding with scope-creep == true

if b >= 1:
    approval-status = "rejected"
    rationale = "<b> blocker finding(s); do not merge"
else if m >= 1 or creep:
    approval-status = "changes-requested"
    rationale = "<m> major finding(s)" + (" and <c> scope-creep finding(s)" if creep)
else:
    approval-status = "approved"
    rationale = "no blocker, no major, no scope-creep (<minor> minor, <nit> nit)"
```

### Derivation order

1. **blocker** wins everything: any `blocker` → `rejected`, regardless of majors or creep. Two blockers and zero majors is still `rejected`.
2. Otherwise **major** and **scope-creep** each independently force `changes-requested`. Either one (or both) is sufficient.
3. Only when **no blocker, no major, and no scope-creep** is the change `approved` (any number of `minor`/`nit` is acceptable).

### Why scope-creep forces changes-requested

A `scope-creep: true` finding (per [scope-creep-detection.md](scope-creep-detection.md)) means the change goes **beyond** the resolved requirements. That is a scope decision the merge should not make silently — the reviewer must explicitly accept the creep as intentional (often by amending the requirements) or roll it back. Hence it forces `changes-requested` even at `minor` severity. A creep finding can still be elevated to `rejected` if it also carries `blocker` via the rubric (e.g. creep that breaks a core flow).

## Accepted Scope-Creep

A `scope-creep: true` finding forces `changes-requested` because a scope decision should not be made silently. The user can make that decision: when Analyze pauses on a creep finding (Smart/Detailed), they may **accept** it as intentional, recording `accepted: "<reason>"` on the finding. An accepted finding keeps its severity and stays in the tallies, but no longer counts toward `creep` in the rule above. Accepting never changes a severity: an accepted `blocker` still yields `rejected`. In Autopilot nothing is accepted (there is no one to decide), so any creep stays blocking. Nothing else can be accepted.

## Per-Task Verdicts (task-in-review input)

For `input-shape: task-in-review`, the run-level `approval-status` above is still derived, but each evaluated task also gets its own verdict, derived by the same rule over **only the findings attributed to that task** (`tasks: [...]` on the finding, from the boundary's `task-files`):

```
for each evaluated task t:
    F(t) = findings whose tasks include t, plus run-level findings that carry no task attribution
    verdict(t) = the rule above applied to F(t)
```

- A finding with no task attribution (a cross-cutting issue in a shared file or a run-level finding) is in `F(t)` for every evaluated task: it holds all of them.
- `approved` → Report promotes the task to `completed` (checkboxes ticked).
- `changes-requested` or `rejected` → Report sets the task to `blocked` with `block-reason` (finding ids) and `blocked-by: review:<report-id>`.
- A task with no findings is `approved` even when the run-level status is not, so one bad task does not hold the others.

## Rationale Format

Record a one-line rationale tied to the tallies (Report Step 1):

```yaml
approval-status: changes-requested
rationale: "2 major finding(s) and 1 scope-creep finding(s); no blocker"
```

```yaml
approval-status: rejected
rationale: "1 blocker finding(s); do not merge"
```

```yaml
approval-status: approved
rationale: "no blocker, no major, no scope-creep (3 minor, 2 nit)"
```

The rationale always surfaces the counts that drove the decision, so a glance at the report shows why the verdict landed where it did.

## Empty Findings Set

When the Findings set is empty (the nothing-to-review case from Scope, or a genuinely clean review), the derivation still runs:

```
b = 0, m = 0, creep = false -> approval-status = "approved"
rationale = "no findings; clean review (or nothing-to-review)"
```

A clean review is `approved` by default. The Report records whether this was a genuine clean review or a nothing-to-review (empty boundary) so the reader can tell them apart.

## Work-linked Edge Cases

For `input-shape: work-linked` or `task-in-review`:

- The Review's `approval-status` is **independent** of the Work run's own `work-state` (`complete`/`partial`/`nothing-done`). Work's Phase-4 Review is a behavior-preserving cleanup; this Review is a standards review. The two verdicts coexist without one overriding the other.
- The `## Review Report — <report-id>` block appended to the work index records this `approval-status` next to Work's `## Work Report` block so both are visible.
- Work's own gate (regression, ledger-based scope check) already held these tasks at `for-review`; this Review's per-task verdicts decide whether each becomes `completed` or `blocked`. After the user addresses a `blocked-by: review` task, `/review <work-id>` evaluates it again.

## Validation (Report Step 1 re-checks)

- `approval-status` is one of `approved` / `changes-requested` / `rejected`.
- Per-task verdicts (task-in-review) match the per-task rule above, and every evaluated task has exactly one verdict.
- The derivation matches the rule above for the recorded tallies (a `rejected` only when `b >= 1`; a `changes-requested` only when `b == 0` and (`m >= 1` or `creep`); `approved` only when `b == 0`, `m == 0`, and not `creep`).
- The rationale surfaces the driving counts.
- No `approval-status` is derived when findings-coherence failed (Step 0 returned the Findings to Analyze per [error-handling.md](error-handling.md) Category 2).

## Notes

- This reference is the single source of truth for the approval derivation. Report looks it up and records the status + rationale; the orchestrator and the other phases never re-encode the rule.
- The rule is intentionally **non-discretionary**: the same tallies always produce the same status. Reviewer judgment lives in the **finding severities** (per [severity-rubric.md](severity-rubric.md)) and the **scope-creep flag** (per [scope-creep-detection.md](scope-creep-detection.md)), not in the approval derivation.
- `changes-requested` and `rejected` are both Report Smart pause triggers (per [interaction-mode-propagation.md](interaction-mode-propagation.md)); `approved` with non-empty learnings is also a pause trigger.