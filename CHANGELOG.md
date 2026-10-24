# Changelog

All notable changes to Arreio are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

> Versions prior to 1.0.5 predate this changelog. See `git log` for historical commits.

## [Unreleased]

## [1.6.0] - 2026-10-23

### Added

- **Plan: Codebase Trace (Research Step 1b).** Research now traces the real code per Source Inventory item: touch points found by symbol and opened, the layer and allowed dependency direction (from architecture docs or build files), overlapping existing types, data and content files with their editing constraints, and discrepancies against file lists in the source. Unfound touch points are recorded as `not found` for Design to turn into Open Decisions. Required in every mode; tech-stack detection and query table gained C++/Unreal and C#/.NET.
- **Plan: Integrity Checks (Design Step 3b).** Nine checks run against the trace before units are final: layering (add a port in the lower layer instead of inverting a dependency), seam operations per consumer, effect owners (time, IDs, I/O, persistence), hook points in existing code, data and content, state that must survive (writer and reader), old versus new types, numbers and snippets, preconditions. Results go into the Design artifact; Generate rejects a design with an open row.
- **Plan gate: repository checks.** `check-plan.py` now verifies `Modify` paths exist (or are created by an earlier unit), `Create` paths do not exist and are created by one unit only, and file counts stated in prose match the lists. `--repo` sets the root (default: nearest `.git` ancestor), `--no-fs` skips these checks.
- **Plan gate: hard unit ceiling.** Units above 2x covered source items (`--hard-ratio`) fail even with a `Justification:`. The 1.5x cap stays a justified warning.
- **Plan evals.** `plan-files-bad.md` with `repo-stub`, and `m2-codebase-grounded.json` replaying the soulcrystals M2 plan review.

### Changed

- **Generated plans start as `status: ready`**, not `complete`; the gate warns on `complete`. Generate marks earlier `ready` plans for the same `source:` as `superseded by <plan-id>` in the index and in their frontmatter.

### Why

Plan 003 for soulcrystals M2 matched the source one-to-one but its review found seven blocking defects (inverted dependency, under-specified seam, missing clock, incomplete content files, unplanned damage/death hooks, wrong input files, rotation not persisted). The 1.3-1.5 fixes bounded scope; nothing grounded the plan in the code. Replaying `check-plan.py` against that plan now reports the nonexistent `Modify` paths, the 81-versus-90 file count and the 2.33x unit ratio.

## [1.5.0] - 2026-10-23

### Added

- **Learn: entry discipline.** New `skills/learn/references/entry-discipline.md` defines what may become an entry: a six-point durability test, the evidence every entry must cite (a real commit sha, a candidate key, or the user's own words), reproducible rubrics for `applicability`, `confidence` and `priority`, a rule against filling sections the input does not support (they are asked for, or the entry is left out), and decline codes. Capture applies it while drafting and Refine re-applies it before accepting. A run that authors nothing is reported, not an error.
- **Learn: candidate keys and `work-id` refs.** Every candidate gets a key (`<report-id>#<finding-id | task-id:gate | cN>`) stored in the entry's `source.reference` or `also-seen-in`, so `/learn <ref>` skips candidates already captured instead of re-offering them. `/learn <work-id>` (the ref Work chains with) now resolves to every Work and Review Report of that work. Autopilot authors every not-yet-captured candidate that passes the durability test; Detailed and Smart ask one selection question.
- **Learn: stale-reference check.** Maintain's refresh reports repository paths an entry cites that no longer exist (`stale-references`) without editing or pruning it.
- **Learn gate script and evals.** `skills/learn/scripts/check-learn.py` (Python 3, standard library only) checks entry frontmatter, body sections per type, evidence format, lineage links, and `docs/learn/index.md` against the entries (five-field records, derived applicability enum, By Category counts and rows, By Domain coverage). Index and Maintain run it before recording `index-coherent`. `skills/learn/evals/` holds five scenario evals and good/bad store fixtures.

### Changed

- **`summary` is a required frontmatter field**, copied verbatim into the index record. The schema said optional while Refine and the orchestrator required it; the index could be written with a body-derived summary the entry did not carry.
- **Refine-time merge folds the draft into the existing entry.** The old text had the draft and the analog swap roles in different documents (and the example contradicted itself). Now the existing entry is the canonical one: no new file, nothing de-indexed, the draft's reference appended to a new optional `also-seen-in`. Base-wide merges in Maintain still de-index the analog and keep its file with `superseded-by`.
- **`update-existing` keeps lineage.** The overwrite carries over `created_at`, `related`, `migrated-from` and `also-seen-in` instead of resetting them. Re-authoring an obsolete slug offers revive or a new slug rather than silently writing over it.
- **Index coherence counts active entries.** The YAML length is compared with entry files that are not obsolete or superseded; the old rule compared with every file, which fails after the first de-index. `Last updated` is stamped on every upsert and rebuild.
- **Prune no longer deadlocks.** A superseded entry was never prunable because the merge itself adds it to the canonical's `related`; only references from other entries now block a prune.
- **Dedup compares inside a type + domain bucket** instead of every pair; the schema's `domain`-must-be-in-`tags` rule (contradicted by its own examples) and the slug-equals-title rule are replaced by "the slug describes the title".

### Fixed

- **Empty index seed.** `arreio-init`'s Learn index template was a stub the learn skill could not parse; it now matches the empty seed in `index-format.md` (`entries: []`), which is also what Pre-Flight self-healing writes.
- **Project-specific text.** Removed the hard-coded "28 entries" and links to this repository's own `docs/learn` entries that dangle in any other project.

## [1.4.0] - 2026-10-23

### Added

- **Source-bound execution.** Triage reads the plan's `source`, `Source Coverage`, and `Open Decisions` and treats the plan (or the prompt, for ad-hoc work) as the source of truth. Open Decisions are resolved before Prepare (asked in Detailed/Smart; the plan's recommended default is recorded in Autopilot, and never invented when absent) and appended to the task index. Review rolls up which source items are done and reports decisions, plan defects, unreachable tasks, and ad-hoc `suggestions`.
- **Touched-files ledger and deviations.** Execute records the files each task changed; undeclared files are reverted unless the AC cannot pass without them, in which case they are recorded as deviations. Review compares the ledger to the declared files instead of judging scope creep from memory.
- **Coherence gate script.** `skills/work/scripts/check-work.py` (Python 3, standard library only) checks task statuses, one test per task, index and Acceptance Criteria checkboxes against statuses, duplicate Work Report blocks, and (with `--plan`) source coverage and orphan units. Review runs it after promoting tasks; a manual checklist covers environments without Python.
- **Work evals.** `skills/work/evals/` holds four scenario evals and good/bad run fixtures that exercise the gate.
- **Review: task-in-review, end to end.** `/review <work-id>` now scopes to the tasks awaiting review (`for-review`, or `blocked` by an earlier review) from the Work Report's per-task `touched-files`, defaults requirements to those tasks' Acceptance Criteria, attributes every finding to the task(s) it affects, and derives a verdict per task. Approved tasks become `completed` (checkboxes ticked); the others become `blocked` with `block-reason` and `blocked-by: review:<report-id>` and are re-reviewed by running `/review <work-id>` again after the fix. One bad task no longer holds the others. Previously the module set never implemented this shape.
- **Review: complete reports.** The Review Report now carries the full findings list with evidence (it used to hold only a rollup, and the Findings artifact is not written outside `detailed` mode), plus `task-verdicts`.
- **Review: finding discipline.** Every finding quotes its evidence and stays inside the change; one finding per root cause; nits roll up past five; security findings need a demonstrated source-to-sink path (a keyword is never a finding); a regression is claimed only with a run against the recorded baseline.
- **Review: accepted scope-creep.** In Detailed/Smart the user can accept a creep finding with a reason (never in Autopilot); it keeps its severity but no longer forces `changes-requested`.
- **Review gate script and evals.** `skills/review/scripts/check-review.py` (Python 3, standard library only) checks finding fields and evidence, the rollup against the findings, the approval status against the tallies, per-task verdicts, task statuses and checkboxes, and the registry row and work-index block. `skills/review/evals/` holds five scenario evals and good/bad report fixtures.

### Changed

- **Clean status model.** Execute stops at `for-review` when the gates pass and never writes `completed`; Review promotes each task without findings to `completed` and ticks the checkboxes then. A regression holds every task, a scope-creep finding holds only its task. A dependency counts as satisfied at `completed` or `for-review`. `/review` approval now also ticks the task and index checkboxes.
- **Execution mode ignores priority.** `P0` no longer forces `inline`; `/plan` marks every Foundation task `P0`, so every plan-based run was forced inline. HIGH-risk is judged by consequence, not keywords. `parallel` requires file-disjoint tasks per wave and runs the regression gate once per wave.
- **Ad-hoc work stays inside the prompt.** One task per outcome the user stated (no fixed cap), merge before split, the module's existing test file instead of a new one per task, exact file paths; extra ideas become `suggestions`.
- **Already-satisfied rule.** A test that passes at Red must cite the code that satisfies the AC and cannot mark the task done on that observation alone.

### Fixed

- **Branch setup after `/plan` and on resume.** The dirty-tree check ignores `docs/plans/`, `docs/tasks/`, and `docs/learn/` and is skipped when already on the work branch, so `/work` no longer fails right after `/plan` or on every resume.
- **Review step numbering.** Removed a duplicated scope-creep step and the contradictory flow that marked tasks `completed` in Execute and reverted them to `for-review` in Review.

## [1.3.1] - 2026-10-23

### Fixed

- **README.** Project structure now shows `/plan`'s `.scope/` and `.design/` folders as always created; documents the optional Python 3 requirement for the coverage gate; Quick Start mentions source-bound plans.

## [1.3.0] - 2026-10-23

### Added

- **Source-bound planning.** Scope now identifies a *source of truth* (a milestone's numbered steps, a spec section, or the prompt) and extracts a binding Source Inventory, asking one question in every mode when the source is unclear. Design maps one unit per source item (merge before split, unit cap of 1.5× covered items); every unit declares a `Source`. Plans gain `source:` frontmatter, a `Source Coverage` table, and an `Open Decisions` section for doubts the source does not settle (no new gates, no edits to accepted documents). See `skills/plan/references/plan-coverage-rules.md`.
- **Coverage gate script.** `skills/plan/scripts/check-plan.py` (Python 3, standard library only) checks source coverage, unit traceability, the unit cap, unit order and dependencies, concrete file lists, `Open Decisions`, and (optionally) the source's test IDs. Generate runs it on the saved plan and registers the plan only on `PASS`; a manual checklist covers environments without Python.
- **Plan evals.** `skills/plan/evals/` holds three scenario evals and good/bad fixtures that exercise the gate.

### Changed

- **Risk is judged by consequence, not keywords.** Keywords only nominate candidate areas; each is confirmed or dismissed with cited evidence, and only confirmed areas set the risk level (e.g. an in-process "transaction" or a game "session" no longer counts as Payments/Security). External research follows a relaxed risk × patterns matrix and never overrides the source of truth.
- **Complexity no longer double counts risk.** The complexity score has four dimensions (0–12; thresholds 3/6/9); risk only sets the tier floor.
- **Deep plans stay honest.** Deep requires at least one real alternative (never invented) and allows a single `Not applicable` line for rollout notes when nothing is deployed.
- **Scope and Design artifacts are always written** (all modes) as the audit trail; Research stays `detailed`-only. Design announces `Coverage: N source items -> M units (xR), K excluded` in every mode.
- **Plan template fixes.** Title precedes the Overview; render only template sections; `Files` must be exact paths; unit IDs ascend in document order (letter suffixes are reserved for Tasks).
- **Tasks no longer edit the plan.** Splitting a criterion into finer tasks is recorded in the task manifest, never as new plan units.

## [1.2.1] - 2026-10-09

### Changed

- **npm discoverability.** Rewrote the package description, expanded keywords (agent skills, Codex, Copilot, Cursor, TDD, slash commands, etc.), made `author` an object with a profile URL, and now publish `CHANGELOG.md` and `ARCHITECTURE.md`.

## [1.2.0] - 2026-10-01

### Added

- **`/plan --deep` flag.** Forces the Deep plan tier in any interaction mode (including Autopilot), skipping the tier question. `tier_recommended` still records the algorithm's result so the override is auditable. The Design phase also produces ≥ 2 alternatives and rollout/integration drafts when the flag is set.

### Fixed

- **Work/Review/Learn reliability pass.** Each skill gets an "Execution Rules" block (ordered steps, no invented values, compute-don't-copy, one question at a time, phase-transition announcements, write rules). Work's execution-mode selection now states first-match-wins evaluation, treats `serial` as a fallback only, and builds its Detailed-mode question (with an `Auto` option) from computed values. `--deep` stays Plan-only: the other skills have no plan tier.
- **Plan tier no longer collapses to Standard.** The tier prompt hardcoded "Auto … (result: Standard)" and its example contradicted the algorithm (HIGH complexity → Deep). The prompt is now built from computed values, `Auto` resolves to `tier_recommended`, and Design computes `tier_recommended` with the same `recommend_tier(complexity, risk_level)` function Generate re-checks.
- **Complexity scoring consistency.** Risk now maps to a fixed score (LOW 0, MEDIUM 1, HIGH 2, CRITICAL 3); the missing-risk default is MEDIUM = 1 (was documented as 2); each dimension requires cited evidence.

### Changed

- **`docs/` is no longer tracked in this repository.** It is generated by the skills at runtime and is now in `.gitignore`.
- **Intermediate phase artifacts are now written only in `detailed` mode.** In `smart` and `autopilot` mode, the plan, work, review, and learn pipelines pass phase artifacts in context instead of writing hidden files (`.scope/`, `.research/`, `.design/`, `.triage/`, `.prepare/`, `.execute/`, `.analyze/`, `.capture/`, `.refine/`, `.index/`, `.maintain/`). Final deliverables (plans, tasks, Work Reports, Review Reports, learn entries) are still always written. `arreio-init` no longer pre-creates the intermediate directories.

## [1.0.5] - 2026-09-02

### Fixed

- **Postinstall script targeted wrong directory.** When Arreio was installed as a dependency, the `postinstall` script used `process.cwd()`, which inside `node_modules/arreio/` points to the package directory itself — not the consuming project. Skills were being copied to `node_modules/arreio/.agents/skills/` instead of `<project>/.agents/skills/`. Switched the destination base to `process.env.INIT_CWD || process.cwd()`, which npm sets to the original invocation directory during lifecycle scripts.

### Documentation

- **README: clarified npm 10+ install-script behavior.** Replaced the misleading "informational advisory" note with actionable guidance. npm 10+ blocks lifecycle scripts by default; users must run `npm install-scripts approve arreio` to run the postinstall, or invoke `/arreio-init` in their AI coding agent to install skills manually.