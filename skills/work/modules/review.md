---
title: Review
description: Close the Work workflow by simplifying the changed code (definitions authoritative in review-checklist), running a whole-work-id regression check, detecting scope creep from the touched-files ledger, rolling up source coverage, surfacing learnings for /learn, and deciding per task whether it is promoted from for-review to completed. Updates task statuses and checkboxes, appends the closing Work Report block to the task index, and runs the check-work.py coherence gate.
type: module
version: 1.1
timestamp: "2026-10-23"
---

# Phase 4 - Review

**Purpose:** Fourth and final step in the Work workflow. Reads the [Execution Log](../references/templates/artifacts/execution-log.md) from Execute, simplifies the executed code, runs a whole-`work-id` test-regression check, detects scope creep from the touched-files ledger, rolls up source coverage, and surfaces new learnings for the Learn skill (`/learn`) to persist. It then decides **per task** whether to promote it from `for-review` to `completed` (ticking its checkboxes), appends the closing `## Work Report — <review-id>` block to `docs/tasks/<work-id>/index.md`, and runs the coherence gate. Returns a [Work Report](../references/templates/artifacts/work-report.md) as the Work skill's final deliverable.

## Workflow

This is the Phase 4 pipeline for the Work Skill. It orchestrates the following steps:

### Step 0: Verification

Run the **[Step 0 verification](../references/error-handling.md)**. Required input: a valid **Execution Log** from Execute. Specifically verify:

1. The Execution Log carries `execute-id`, `prepare-id`, `triage-id`, `work-id`, `input-shape`, `interactionMode`, `executionMode`, the per-task result table, and the aggregator counts.
2. **Task-status coherence** (the orchestrator's quality gate #4): every task ended `for-review` (or was already `completed` in an earlier run), `blocked` (with a recorded reason), or `skipped` (with a recorded reason) — none left `in-progress` — and no checkbox is ticked for a task that is not `completed`. Execute is responsible for leaving this coherent; Review re-verifies and refuses to proceed (Category 2 recovery) if not.
3. `interactionMode` is present and valid (default to `smart` if missing; log warning).
4. Cross-phase consistency: `work-id`, `triage-id`, `prepare-id`, `execute-id` match the upstream artifacts.

The tasks Review evaluates are the Execution Log's `for-review` tasks plus the manifest's `pending-review-tasks` from earlier runs. If there are none (`work-state: nothing-ready` was carried through), Review still produces a Work Report recording that no task was runnable — do not abort.

### Step 1: Simplify and Consolidate

Review the code touched by the `for-review` tasks for simplification and consolidation. The definitions and the per-check criteria are authoritative in **[review-checklist.md](../references/review-checklist.md)** — Review applies the checklist, it does not re-encode it. Run its checks across the changed files (the union of those tasks' `touched-files`):

- **Dead code / duplication** — remove code made unreachable or duplicated by the run; honor DRY by extracting shared logic.
- **Naming and structure** — tighten intention-revealing names; collapse overlarge functions/classes to single responsibility; no speculative generality.
- **Boundary isolation** — keep side effects at the boundaries; prefer pure functions where the changes permit it.

Apply each change as a **refactor** — the relevant tasks' AC tests must stay green; if any targeted check would change behavior, treat it as scope creep (Step 3) rather than a refactor, and do not apply it here. Never edit a file that no task touched.

Record `simplification-summary` (what was simplified/clipped) and `consolidations` (any merged logic / extracted abstractions) in the Work Report.

### Step 2: Whole-Work-Id Regression Check

1. Run the full test suite for the `work-id`'s affected scope (the union of the evaluated tasks' test paths, plus any files they touched that are covered elsewhere) using the Execute-resolved test command (`runner` + `packageManager`).
2. **Compare against the Prepare baseline** recorded in the Execution Plan:
   - `baseline: green` — the suite must still be green; **any failure is a regression** (binary threshold: one failure = gate fails).
   - `baseline: snapshot-and-continue` — failures must be a subset of the recorded known-failing snapshot; any **new** failure is a regression.
3. Record `regression-check: clean | regressions-found` with the failing-test list if any. A regression cannot be attributed to one task, so it holds **every** evaluated task at `for-review` (Step 4a).

### Step 3: Scope-Creep Detection

Scope creep is read from the ledger, not judged from memory. Apply the checks in [review-checklist.md](../references/review-checklist.md#scope-creep-checks-authoritative):

1. **Per-task scope** — for each evaluated task, compare its `touched-files` to its declared set (`files.create` ∪ `files.modify` ∪ `files.test`). Every touched path outside the declared set is a finding; every recorded deviation is a finding. Then confirm the change is bounded by **that task's single AC** (behavior beyond what `files.test` asserts is a finding).
2. **Manifest scope** — confirm no task was added, removed, or silently expanded beyond what Triage resolved. (A `dependency-warning: expanded-to-upstream` from the task-file shape is expected, not creep.)
3. Record `scope-creep` findings per task (file path + why it exceeds the AC, or the deviation's `why-required`), or `scope-creep: none`. Surface every finding to the user — never fold it silently into a task.

### Step 4: Source Coverage Rollup

Plan-based input only (ad-hoc: the prompt is the source — report each stated outcome against its task instead).

1. For each `Source Coverage` row recorded in the manifest, list the tasks of its units and their final status once Step 4a has run; mark the item `done` only when every task is `completed`.
2. Report items that are not done with the blocking task and reason. Report `Excluded` rows unchanged. List any task whose unit appears in no coverage row as an **orphan** (a defect in the plan or the task list).
3. Record `source-coverage` in the Work Report. Running the coherence gate (Step 7) with `--plan` prints the same table mechanically.

### Step 4a: Gate Decision — Per Task

Decide, for each evaluated task, whether it is promoted to `completed`:

- `regression-check: regressions-found` → **all** evaluated tasks stay `for-review`.
- A task with scope-creep findings → that task stays `for-review`.
- A task with no findings, while the regression check is clean → `task-status-target: completed`.

Record the decision with a brief summary: e.g., "Gate passed for 7/9 tasks; T04, T06 held for review (scope creep: 2 files)" or "Gate blocked for all: regressions-found (3 new failures)".

### Step 5: Learnings Capture

Surface new learnings discovered during execution for the Learn skill to persist (Work does not write `docs/learn/` directly):

1. For each notable finding — a confirmed pattern, a refuted assumption, a gotcha hit, or a decision forced by the run — record a learning candidate with: a working title, the domain, the source (task-id + gate where found), and a 1–2 sentence summary.
2. Carry the Work Manifest's `Learning Gaps` forward; add any gaps the run revealed (e.g., a missing test pattern that forced a workaround).
3. Record `learnings-to-capture` (candidates) and `learning-gaps` in the Work Report. The user is prompted (per interaction mode) to run `/learn` to persist them (orthogonal to approval gates).

### Step 6: Generate the Work Report Artifact

1. **Assign a `review-id`** per [id-generation.md](../references/id-generation.md) (format `YYYY-MM-DD-NNN-review`, saved to `docs/plans/.work/.review/`). Reuse it if the user later picks **Edit & Retry**.

2. Produce a **Work Report** block (as markdown) following the schema in [work-report.md](../references/templates/artifacts/work-report.md). Include:
   - `review-id`, inherited `execute-id`, `prepare-id`, `triage-id`, `work-id`, `input-shape`
   - `interactionMode` and `executionMode` (both carried)
   - the final task-outcome rollup (`completed` / `for-review` / `blocked` / `skipped`, after the Step 4a promotions)
   - `tasks`: per task, `task-id`, `unit`, final `status`, and `touched-files` from the ledger (so `/review` scopes to what each task changed)
   - `simplification-summary` and `consolidations`
   - `regression-check` (`clean` | `regressions-found` + failing list)
   - `scope-creep` findings (or `none`) and `deviations`
   - `source-coverage`, `decisions` taken (Triage Step 2a.7), `plan-defects`, unreachable tasks, and `suggestions` (ad-hoc extras the user did not ask for)
   - `learnings-to-capture` and `learning-gaps`
   - a final `work-state`:
     - `complete`: all tasks `completed` and regression-clean
     - `for-review`: at least one task held at `for-review` (regressions or scope creep; pending `/review`)
     - `partial`: some tasks `blocked`/`skipped` but progress made (all other tasks `completed`)
     - `nothing-done`: empty run or all blocked early

### Step 7: Update Tasks, Register the Work Report, and Run the Gate

**Promote tasks** per Step 4a. For each task with `task-status-target: completed`:

1. Open `docs/tasks/<work-id>/T<NN>-<name>.md`.
2. Set frontmatter `status: completed` and flip the `## Acceptance Criteria` checkbox to `- [x]`.
3. Tick that task's row in `docs/tasks/<work-id>/index.md` from `- [ ]` to `- [x]` (forward only).

Tasks held at `for-review` keep their status and unticked boxes. Idempotent: re-running Review with the same `review-id` produces the same state and never reverts a `completed` task.

**Append status block to task index** — the block records the final state next to the checklist, so a future glance shows how the run ended:

```markdown
## Work Report — <review-id>

- **Status:** complete | partial | for-review | nothing-done
- **Tasks:** <completed>/<total> completed, <for-review> for-review, <blocked> blocked, <skipped> skipped
- **Regression check:** clean | regressions-found (<N>)
- **Scope creep:** none | <count> finding(s)
- **Source coverage:** <done>/<total> items done | n/a
- **Learnings to capture:** <count> (run `/learn` to persist)
- **Work Report:** docs/plans/.work/.review/<review-id>.md
```

If the index does not exist (ad-hoc input that somehow lost its index), create it with the checklist before appending the block. The block is **append-only** and idempotent on `review-id` (a re-run overwrites the block with the same `review-id`, never duplicates).

**Run the coherence gate.** When Python 3 is available, run:

```bash
python skills/work/scripts/check-work.py docs/tasks/<work-id> [--plan docs/plans/<plan-id>-<slug>.md]
```

(adjust the script path to where the skill is installed; pass `--plan` for plan-based input). On `FAIL`, fix the incoherent task file, checkbox, or duplicate block it names and re-run; a task held at `for-review` or `blocked` is a warning, not an error. Without Python, verify the same properties by hand per [review-checklist.md](../references/review-checklist.md#coherence-gate-manual-checklist).

### Step 8: Present, Confirm, and Save

Apply the **[phase confirmation behavior](../references/interaction-mode-propagation.md)** for the current `interactionMode`, using these review-specific **Smart pause triggers**:

- Any task held at `for-review` (regressions, scope creep, or deviations), or
- `regression-check: regressions-found` (any test failures detected), or
- `scope-creep` findings exist (confirm the creep is intentional or roll it back), or
- A source item is not done, or a plan defect was recorded, or
- `learnings-to-capture` is non-empty and the user may want to capture them now via `/learn` before closing.

- **Detailed:** present the Work Report and ask one question with options _(1) Finalize Work, (2) Edit & Retry, (3) Abort_. On **Edit & Retry**, loop back through Steps 1–7 reusing the `review-id` (the index block is overwritten, not duplicated, because it keys on `review-id`). On **Abort**, stop and inform the Orchestrator.
- **Smart:** pause only when a pause trigger above is true; otherwise auto-proceed.
- **Autopilot:** auto-proceed (no confirmation).

Then save the artifact to `docs/plans/.work/.review/<review-id>.md` (ensure `interactionMode` and `executionMode` are included).

### Step 9: Return to Orchestrator

Return the Work Report to the Orchestrator — `path`, `review-id`, `work-id`, `work-state`, `interactionMode`, `executionMode`, and `learnings-to-capture` count. The Orchestrator marks the Work workflow complete.

**Next steps (user-facing):**

- If `work-state: for-review`, inform the user: "<N> task(s) are held at `for-review`. Run `/review <work-id>` to audit them before final approval."
- Optionally chain to the Learn skill (`/learn <work-id>` or `/learn <candidate-ref>`) when `learnings-to-capture` is non-empty; otherwise the session ends.

## Output: Work Report Artifact

- Verify that the Work Report is complete and valid: `review-id`, `execute-id`, `prepare-id`, `triage-id`, `work-id`, `input-shape`, `interactionMode`, `executionMode`, the task-outcome rollup, `simplification-summary`, `consolidations`, `regression-check`, `scope-creep`, `source-coverage`, `learnings-to-capture`, and `learning-gaps`.
- Verify that **task-status coherence** held: the Execution Log's outcomes plus the Step 4a promotions match `docs/tasks/<work-id>/index.md` and the task files' frontmatter, and the coherence gate printed `PASS` (or the manual checklist was satisfied).
- Verify that only tasks with no findings were promoted to `completed`, and that their checkboxes were ticked (task file and index).
- Verify that the `## Work Report — <review-id>` block was appended to `docs/tasks/<work-id>/index.md` and is idempotent on `review-id` (no duplicate blocks).
- Verify that the simplification/consolidation/scope-creep/learnings rules were **applied from** [review-checklist.md](../references/review-checklist.md) rather than re-encoded inline.
- Verify that `work-state` reflects the gate outcome: `complete | for-review | partial | nothing-done`.
- Verify that the artifact is saved to `docs/plans/.work/.review/<review-id>.md`.

> The Work Report is the primary deliverable of the Work Skill. Tasks held at `for-review` signal that Standalone Review approval is required before moving to `completed`. The Orchestrator marks the workflow complete; user runs `/review <work-id>` next if tasks are held; optionally chains to `/learn` when learnings were surfaced (orthogonal to approval gates).
