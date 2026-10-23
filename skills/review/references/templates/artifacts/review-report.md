---
title: Review Report Artifact
description: Template for the Review Report Artifact produced by the Report phase. Carries the approval status (approved / changes-requested / rejected) with rationale, the findings rollup (counts by severity and by category), non-binding recommendations, the scope-creep summary, learnings-to-capture for /learn, and the registry/work-index registration state. The Review skill's final deliverable.
type: template
version: 1.1
timestamp: "2026-10-23"
---

# Review Report Artifact

The product of the **Report** phase is the Review Report — the Review skill's final deliverable. It records the **approval status** (`approved` / `changes-requested` / `rejected`) derived deterministically from the Findings tallies per [approval-criteria.md](../../approval-criteria.md), with a one-line rationale tied to the counts; the findings rollup (by severity and by category); non-binding **recommendations**; the **scope-creep summary**; **learnings-to-capture** candidates (handed to `/learn`); and the registration state. A registry row is appended to `docs/review/index.md` always; for work-linked input, a distinct `## Review Report — <report-id>` block is appended to `docs/tasks/<work-id>/index.md`.

## Schema

```yaml
report-id: YYYY-MM-DD-NNN-report
analyze-id: YYYY-MM-DD-NNN-analyze
prepare-id: YYYY-MM-DD-NNN-prepare
scope-id: YYYY-MM-DD-NNN-scope
review-id: YYYY-MM-DD-NNN
input-shape: change-set | work-linked | task-in-review | ad-hoc
interactionMode: detailed | smart | autopilot
status: complete
timestamp: ISO-8601 timestamp

approval-status: approved | changes-requested | rejected
rationale: "[one-line, tied to the driving counts]"

findings-rollup:
  by-severity: { blocker: <N>, major: <N>, minor: <N>, nit: <N> }
  by-category: { quality: <N>, security: <N>, tests: <N>, documentation: <N>, integration: <N>, scope-creep: <N> }
  total: <N>

findings:                              # the full list from Analyze (the report is the only always-written artifact)
  - id: F01
    severity: blocker | major | minor | nit
    category: quality | security | tests | documentation | integration | scope-creep
    location: "src/lib/redis-client.ts:42"
    message: "[1-2 sentences]"
    evidence: "[quoted hunk line(s), test output, or tool message]"
    trace: "C1" | "general-quality" | "no-requirements"    # exactly one of trace / scope-creep
    scope-creep: true                  # only on creep findings, which carry no trace
    tasks: [<task-id>, ...]            # task-in-review
    accepted: null | "<reason>"        # scope-creep only; user-set

task-verdicts:                         # task-in-review only; omit otherwise
  - { task-id: <work-id>-T<NN>, verdict: approved | changes-requested | rejected, findings: [F01, ...] }

recommendations:
  blocking: [ "F<NN> @ <location>: <action>"          # for changes-requested/rejected — actionable blocker/major fixes
            | null ]
  polish: [ "F<NN> @ <location>: <optional improvement>"    # for approved (minor/nit) suggestions
          | null ]

scope-creep-summary: none | "<count> finding(s)" | "skipped (no requirements)"

learnings-to-capture:
  - title: "[working title]"
    domain: [primary domain]
    source: { finding-id }            # the finding id where this surfaced
    summary: "[1-2 sentence summary]"
    type: confirmed-pattern | refuted-assumption | gotcha | forced-decision

learning-gaps:
  - gap_name: "[Domain] — [what's missing]"
    domain: [primary domain]
    suggested_action: "Research external resource" | "Document post-review"

work-id: YYYY-MM-DD-NNN | null          # work-linked only; null otherwise

registration:
  registry-row-appended: true          # appended to docs/review/index.md (idempotent on report-id)
  work-index-block-appended: true | skipped   # work-linked and task-in-review; skipped if the work index is missing
  tasks-updated: true | not-applicable        # task-in-review: statuses/checkboxes updated per task-verdicts
```

Also save the Review Report to `docs/review/.report/<report-id>.md`.

## Closing Blocks

### Registry row (appended to `docs/review/index.md`, always)

```
- <report-id> — <target-summary> — <approval-status> — docs/review/.report/<report-id>.md
```

### Work-index block (appended to `docs/tasks/<work-id>/index.md`, work-linked and task-in-review)

```markdown
## Review Report — <report-id>

- **Status:** approved | changes-requested | rejected
- **Findings:** <blocker> blocker, <major> major, <minor> minor, <nit> nit
- **Tasks:** <approved> approved (completed), <blocked> blocked by this review | n/a   <!-- task-in-review only -->
- **Scope creep:** none | <count> | skipped (no requirements)
- **Learnings to capture:** <count> (run `/learn` to persist)
- **Review Report:** docs/review/.report/<report-id>.md
```

Both the registry row and the work-index block are **append-only** and **idempotent on `report-id`**: a re-run overwrites the entry with the same id, never duplicates it. The work-index block is deliberately distinct from Work's own `## Work Report — <review-id>` block (different label, different skill, different `report-id`).

## Validation Rules

- **report-id:** Required. Format `YYYY-MM-DD-NNN-report`.
- **analyze-id, prepare-id, scope-id, review-id, input-shape:** Required, inherited (cross-phase consistency).
- **interactionMode:** Required, identical across Prepare/Analyze/Report (orchestrator quality gate #2).
- **approval-status:** Required. One of `approved`, `changes-requested`, `rejected`, derived per [approval-criteria.md](../../approval-criteria.md) (the derivation is non-discretionary: `rejected` iff blocker ≥ 1; `changes-requested` iff no blocker and (major ≥ 1 or scope-creep present); `approved` otherwise).
- **rationale:** Required. One line surfacing the driving counts.
- **findings:** Required (may be empty). The full list; each finding has `severity`, `category`, repo-relative `location`, `message`, non-empty `evidence` for blocker/major, exactly one of `trace` / `scope-creep: true`, and (task-in-review) `tasks`. `accepted` only on scope-creep findings with a user reason.
- **task-verdicts:** Required for task-in-review, one row per evaluated task, each derived from only the findings attributed to that task (see [approval-criteria.md](../../approval-criteria.md#per-task-verdicts-task-in-review-input)).
- **findings-rollup:** Required. Counts by severity and by category must match the Findings artifact's tallies.
- **recommendations:** Required. `blocking` populated for `changes-requested`/`rejected` (actionable blocker/major fixes); `polish` populated for `approved` (minor/nit). Either list may be empty (e.g. a genuinely clean approved review has `blocking: null`, `polish: []`).
- **scope-creep-summary:** Required. `none`, `"<count> finding(s)"`, or `skipped (no requirements)` (consistent with the Findings `scope-creep-ran`).
- **learnings-to-capture:** Required (may be empty). Each candidate has title/domain/source/summary/type. Review does not write `docs/learn/` directly — these are handed to `/learn`.
- **learning-gaps:** Required (may be empty).
- **work-id:** Required for work-linked input (and the work-index block is then expected); `null` otherwise (and the work-index block is `skipped`).
- **registration.registry-row-appended:** Required, must be `true`.
- **registration.tasks-updated:** Required for task-in-review (`true`: every `approved` task is `completed` with checkboxes ticked, every other evaluated task is `blocked` with `block-reason` and `blocked-by: review:<report-id>`); `not-applicable` otherwise.
- **registration.work-index-block-appended:** Required for work-linked and task-in-review input (`true` or `skipped`); `skipped` for other input.
- **status:** Required. `complete`.

## Example (changes-requested — two majors, one scope-creep)

```yaml
report-id: 2026-08-08-001-report
analyze-id: 2026-08-08-001-analyze
prepare-id: 2026-08-08-001-prepare
scope-id: 2026-08-08-001-scope
review-id: 2026-08-08-001
input-shape: change-set
interactionMode: smart
status: complete
timestamp: 2026-08-08T15:45:00Z
approval-status: changes-requested
rationale: "2 major finding(s) and 1 scope-creep finding(s); no blocker"
findings-rollup:
  by-severity: { blocker: 0, major: 2, minor: 1, nit: 0 }
  by-category: { quality: 1, security: 0, tests: 1, documentation: 0, integration: 0, scope-creep: 1 }
  total: 3
findings:
  - id: F01
    severity: major
    category: tests
    location: "src/lib/session-store.ts:22"
    message: "Production-code change ships no test for the new behavior."
    evidence: "src/lib/session-store.ts:22 adds save(); no test file covers session-store"
    trace: C2
    accepted: null
  - id: F02
    severity: major
    category: scope-creep
    location: "src/lib/cache.ts:hunk-1"
    message: "Adds a TTL cache layer beyond C1/C2."
    evidence: "src/lib/cache.ts:hunk-1 adds class TtlCache; no criterion mentions caching"
    scope-creep: true
    accepted: null
  - id: F03
    severity: minor
    category: quality
    location: "src/lib/redis-client.ts:42"
    message: "Magic number 3 for retry count."
    evidence: "src/lib/redis-client.ts:42 `for (let i = 0; i < 3; i++)`"
    trace: C1
    accepted: null
recommendations:
  blocking:
    - "F01 @ src/lib/session-store.ts:22: Add tests for get/save/delete per C2"
    - "F02 @ src/lib/cache.ts:hunk-1: Split the cache layer off into its own task or roll back"
  polish:
    - "F03 @ src/lib/redis-client.ts:42: Extract MAX_RETRIES constant"
scope-creep-summary: "1 finding(s)"
learnings-to-capture:
  - title: "TTL cache layers tend to creep into session-store changes — split before estimating"
    domain: data-storage
    source: { finding-id: F02 }
    summary: "Scope-creep finding F02 recurred; confirming the pattern of cache layers bundling into session work."
    type: confirmed-pattern
learning-gaps: []
work-id: null
registration:
  registry-row-appended: true
  work-index-block-appended: skipped
```

## Example (approved — clean review)

```yaml
report-id: 2026-08-08-002-report
analyze-id: 2026-08-08-002-analyze
prepare-id: 2026-08-08-002-prepare
scope-id: 2026-08-08-002-scope
review-id: 2026-08-08-002
input-shape: ad-hoc
interactionMode: autopilot
status: complete
timestamp: 2026-08-08T15:50:00Z
approval-status: approved
rationale: "no blocker, no major, no scope-creep (0 minor, 0 nit)"
findings-rollup:
  by-severity: { blocker: 0, major: 0, minor: 0, nit: 0 }
  by-category: { quality: 0, security: 0, tests: 0, documentation: 0, integration: 0, scope-creep: 0 }
  total: 0
findings: []
recommendations:
  blocking: null
  polish: []
scope-creep-summary: "skipped (no requirements)"
learnings-to-capture: []
learning-gaps: []
work-id: null
registration:
  registry-row-appended: true
  work-index-block-appended: skipped
```

## Example (task-in-review — one task approved, one blocked)

```yaml
report-id: 2026-10-23-001-report
analyze-id: 2026-10-23-001-analyze
prepare-id: 2026-10-23-001-prepare
scope-id: 2026-10-23-001-scope
review-id: 2026-10-23-001
input-shape: task-in-review
interactionMode: smart
status: complete
timestamp: 2026-10-23T16:00:00Z
approval-status: changes-requested
rationale: "1 major finding(s); no blocker"
findings:
  - id: F01
    severity: major
    category: tests
    location: "src/b.ts:12"
    message: "The empty-title branch added here is not covered by any assertion."
    evidence: "src/b.ts:12 `if (!title) return DEFAULT;` has no covering assertion in src/b.test.ts"
    trace: C2
    tasks: [2026-10-23-001-T02]
    accepted: null
  - id: F02
    severity: nit
    category: documentation
    location: "src/a.ts:3"
    message: "Exported parse() lacks a docstring."
    evidence: "src/a.ts:3 `export function parse(`"
    trace: C1
    tasks: [2026-10-23-001-T01]
    accepted: null
findings-rollup:
  by-severity: { blocker: 0, major: 1, minor: 0, nit: 1 }
  by-category: { quality: 0, security: 0, tests: 1, documentation: 1, integration: 0, scope-creep: 0 }
  total: 2
task-verdicts:
  - { task-id: 2026-10-23-001-T01, verdict: approved, findings: [F02] }
  - { task-id: 2026-10-23-001-T02, verdict: changes-requested, findings: [F01] }
recommendations:
  blocking:
    - "F01 @ src/b.ts:12: add a test for the empty-title branch, then run /review 2026-10-23-001 again"
  polish:
    - "F02 @ src/a.ts:3: add a docstring to parse()"
scope-creep-summary: none
learnings-to-capture: []
learning-gaps: []
work-id: 2026-10-23-001
registration:
  registry-row-appended: true
  work-index-block-appended: true
  tasks-updated: true
```

Result: T01 becomes `completed` (checkboxes ticked); T02 becomes `blocked` with `block-reason: "F01"` and `blocked-by: review:2026-10-23-001-report`. Running `/review 2026-10-23-001` after the fix evaluates T02 again.

## Notes

- The Review Report is the primary deliverable of the Review skill. The Orchestrator marks the workflow complete and may chain to `/learn` when `learnings-to-capture` is non-empty.
- Approval is **non-discretionary**: the same tallies always produce the same status. Reviewer judgment lives in finding severities and the scope-creep flag, not in the approval derivation (see [approval-criteria.md](../../approval-criteria.md)).
- **No GitHub sync:** this skill does not post comments/reviews/labels. The registry row + (work-linked) work-index block are the only outbound writes — both local, both on disk.
- For work-linked and task-in-review input, Review's `approval-status` is **independent** of Work's own `work-state`; the two verdicts coexist (the `## Review Report` block sits next to Work's `## Work Report` block).