---
title: Capture
description: Entry point to the Learn workflow. Resolves an explicit (type + text) or candidate (Work/Review learnings-to-capture ref) input, selects the entry to draft, drafts the per-type body and frontmatter per the authoritative write contract (entry-schema), allocates the learn-id umbrella and the slug, and returns a Captured Entry for the Refine phase.
type: module
version: 1.0
timestamp: "2026-08-08"
---

# Phase 1 - Capture

**Purpose:** Entry point to the Learn workflow. Resolves the incoming input (an explicit `<type> <text>` author request **or** a candidate ref to a Work/Review `learnings-to-capture` list), selects **one** entry to draft, drafts its per-type body and frontmatter per the authoritative [entry-schema.md](../references/entry-schema.md), allocates the `learn-id` umbrella and proposes the `slug`, and returns a [Captured Entry](../references/templates/artifacts/captured-entry.md) for the Refine phase. Capture drafts; it does **not** validate against existing entries (that is Refine's job) and it never writes the entry file or the index (that is Index's job). Maintain-only input (`/learn maintain`) does not reach Capture — the Orchestrator routes it straight to Maintain.

## Workflow

This is the Phase 1 pipeline for the Learn Skill. It orchestrates the following steps:

### Step 0: Verification

Run the **[Step 0 verification](../references/error-handling.md)**. Required input: a valid **Learn Input Artifact** (see [learn-input.md](../references/templates/artifacts/learn-input.md)) from the Orchestrator. Specifically verify:

1. The Learn Input Artifact carries exactly one of: an `explicit` request (`type` + `text`), a `candidate` ref, **or** a `maintain` flag.
2. If the shape is `maintain`, **do not run Capture** — the Orchestrator should have routed directly to Maintain (Phase 4). Surface a routing error to the Orchestrator (Category 2).
3. `interactionMode` is present and valid (default to `smart` if missing; log warning).
4. The required folders already exist (the Orchestrator's Pre-Flight Check is responsible for creation); do not re-create them here.

If the input is empty or ambiguous, ask the user one question: "What would you like to capture? Provide a type (decision/pattern/gotcha/workflow) and text, a candidate ref, or `maintain`."

### Step 1: Resolve Input Shape

Determine which of the two authoring shapes applies (maintain is rejected in Step 0):

1. **Explicit** — the input carries a `<type>` (one of `decision` / `pattern` / `gotcha` / `workflow`) and `<text>` (prose, a file/commit ref, or a short description to expand).
2. **Candidate** — the input carries a ref to a Work `review-id` (`docs/plans/.work/.review/<id>.md`), a Review `report-id` (`docs/review/.report/<id>.md`), or a `work-id` (`YYYY-MM-DD-NNN`, the id Work chains with).

Record `input-shape: explicit | candidate`. If `<type>` is provided but is not one of the four, ask the user to pick from the four (Step 2 confirms intent either way).

### Step 2: Select the Entry to Draft

Capture produces **one** Captured Entry per run (single-shape artifact). The shape determines the selection:

#### 2a. Explicit

1. Validate `<type>` is one of the four; record it as `capture.target-type`.
2. The `<text>` is the sole source. If it is a short description, this is a Smart pause trigger (Step 6), and every section the text does not support is **asked for** in Step 3, never filled in.
3. The entry to draft is fixed: one entry of `<type>` from `<text>`.

#### 2b. Candidate

1. Resolve the ref to the report file(s) by its shape:
   - ends in `-review` → Work Report `docs/plans/.work/.review/<review-id>.md`.
   - ends in `-report` → Review Report `docs/review/.report/<report-id>.md`.
   - bare `YYYY-MM-DD-NNN` → every Work Report under `docs/plans/.work/.review/` and every Review Report under `docs/review/.report/` whose `work-id` equals it (the union of their lists; each candidate keeps its own report id).
   Read each report's `learnings-to-capture` list.
2. If the combined list is empty, inform the user (no candidates to curate) and stop — do not fabricate an entry.
3. Give every candidate its **key**: the report id plus `#<finding-id>` when `source` carries one, `#<task-id>:<gate>` when it carries a task and gate, else `#c<n>` (its 1-based position in that report's list). A candidate whose key already appears as an entry's `source.reference` or in an entry's `also-seen-in` is **already captured** and is skipped (listed with that reason, never re-offered as new).
4. Run the [durability test](../references/entry-discipline.md#the-durability-test) on each remaining candidate by reading what its `source` points at (the task file, the finding in the Review Report). One that fails is declined with its code; say which test it failed.
5. Pick the entries per the [Candidate Lists](../references/interaction-mode-propagation.md#candidate-lists) rule for the mode (one selection question in Detailed/Smart, none in Autopilot). If the candidate's recorded `type` is one of the four, use it; otherwise map: `confirmed-pattern` → `pattern`, `refuted-assumption` → `gotcha`, `gotcha` → `gotcha`, `forced-decision` → `decision`. The user may override the inferred type.
6. Record the selected candidate as `capture.source-candidate` (with its key, carried for traceability into the entry's `source` frontmatter).

> Capture handles one entry per run. For several picked candidates the Orchestrator loops Capture → Refine → Index once per candidate, and each loop starts with the key check of step 3 (an earlier loop may have folded a later candidate in).

### Step 3: Draft the Entry

Draft the entry's frontmatter and body per the authoritative write contract **[entry-schema.md](../references/entry-schema.md)** — Capture looks it up; it does not re-encode the field list or the body section template:

1. **Frontmatter** — populate from the text/candidate:
   - `type` (one of the four), `slug` (proposed in Step 4), `domain`, `tags`, `summary`, `priority`, `applicability: { current_project: N, general: N }` (numeric scores 0–10), `confidence` (`high` / `medium` / `low`), `source` (`type: commit|candidate|user`, `reference`, `extracted_at`), `created_at`/`updated_at`.
   - For a candidate input, `source.type: candidate` and `source.reference: <candidate key>` (Step 2b.3). The reference format for every source type is fixed in [entry-discipline.md](../references/entry-discipline.md#evidence).
2. **Body** — draft the per-type section template (entry-schema.md defines the canonical sections per type): `decision` (Problem / Solution / Decision Rationale / Application / Related Learnings), `pattern` (Problem / Pattern / When to Apply / Example / Related Learnings), `gotcha` (Problem / Trap / Solution / Prevention / Related Learnings / Source), `workflow` (Convention / Why / How / Related Learnings).
3. **Extract domain and tags** from the text/candidate — name the primary `domain` and 2–6 `tags` (related domains).
4. **Score applicability, confidence and priority** with the rubrics in [entry-discipline.md](../references/entry-discipline.md#rubrics), from facts you can name (files that exist, evidence cited). Capture proposes these; Refine validates them.
5. If the `<text>` is a file/commit ref, **read** that file/commit and ground the draft in the actual content (Capture does not invent content from a bare ref — it reads and summarizes the decision the ref embodies).
6. **Do not invent.** Fill a body section only from the input, the files it points at, or the user's answer ([entry-discipline.md](../references/entry-discipline.md#do-not-invent)). For each section the input does not support, ask one question for it (2–4 options, including "leave the entry out"). `Related Learnings` lists only slugs found in `docs/learn/index.md`; otherwise `(none yet)`.
7. **Durability.** Run the [durability test](../references/entry-discipline.md#the-durability-test) on the draft and record each answer. If it fails and the user cannot supply what is missing, stop with the decline code; write nothing.

### Step 4: Propose slug and Allocate the learn-id Umbrella

1. **Propose a `slug`** — a kebab-case, globally-unique stable key for the entry. Derive from the title (concise, descriptive); for time-bound decisions a date suffix is allowed (`critical-risk-tier-security-payments-2026-07-04`). The slug is the upsert key for the entry file and its index record. Refine checks uniqueness; Capture only **proposes**.
2. **Allocate a `learn-id`** umbrella of the form `YYYY-MM-DD-NNN` per [id-generation.md](../references/id-generation.md), counting existing `docs/learn/.capture/YYYY-MM-DD-NNN-capture.md` files for today (`detailed` mode only; in `smart`/`autopilot` use the in-memory label per id-generation.md). The `learn-id` is the pipeline umbrella carried through Capture → Refine → Index (Maintain-only runs allocate their own `maintain-id` and have no `learn-id`).
3. **Assign a `capture-id`** per [id-generation.md](../references/id-generation.md) (format `YYYY-MM-DD-NNN-capture`, saved to `docs/learn/.capture/`). Reuse it if the user later picks **Edit & Retry**.

### Step 5: Generate the Captured Entry Artifact

Produce a **Captured Entry** block (as markdown) following the schema in [captured-entry.md](../references/templates/artifacts/captured-entry.md). Include:

- `capture-id`, `learn-id`, `input-shape`, `interactionMode`
- `target-type` (the entry's type), the proposed `slug`
- the drafted `frontmatter` (per [entry-schema.md](../references/entry-schema.md)) and the drafted `body` (per-type sections)
- `source-candidate` (the picked candidate, or `null` for explicit input)
- `durability` — one line per test of the durability test (`pass` or the failing code)
- `inferred: true | false` — `true` when the draft was inferred from a short description or a candidate (a Step 6 pause trigger); `false` when grounded in a concrete ref/file the user provided

### Step 6: Present, Confirm, and Save

Apply the **[phase confirmation behavior](../references/interaction-mode-propagation.md)** for the current `interactionMode`, using these capture-specific **Smart pause triggers**:

- `input-shape: candidate` (the draft was inferred from a candidate — confirm the inferred `type`, `domain`, `tags`, and body match intent), or
- `inferred: true` (the explicit `<text>` was a short description expanded to a full draft — confirm it matches intent), or
- The `<text>` was a file/commit ref that could not be grounded (could not read the content) — ask the user to supply the decision in prose instead.

- **Detailed:** present the Captured Entry and ask one question with options *(1) Proceed to Refine, (2) Edit & Retry, (3) Abort*. On **Edit & Retry**, loop back through Steps 1–5 reusing the `capture-id` and `learn-id` (re-propose `slug` only if the `target-type` changed). On **Abort**, stop and inform the Orchestrator.
- **Smart:** pause only when a pause trigger above is true; otherwise auto-proceed.
- **Autopilot:** auto-proceed (no confirmation).

Then, **in `detailed` mode only**, save the artifact to `docs/learn/.capture/<capture-id>.md` (ensure `interactionMode` and `target-type` are included) and return it, with the `interactionMode` value, to the Orchestrator for the transition to Phase 2 (Refine). In `smart` and `autopilot` mode, do **not** write the file; pass the artifact to the next phase in context (see [Artifact Persistence](../references/interaction-mode-propagation.md#artifact-persistence)).

## Output: Captured Entry Artifact

- Verify that the Captured Entry is complete and valid: `capture-id`, `learn-id`, `input-shape`, `interactionMode`, `target-type`, the proposed `slug`, the drafted `frontmatter`, and the drafted `body`.
- Verify that `target-type` is one of `decision` / `pattern` / `gotcha` / `workflow`.
- Verify that every body section traces to the input (nothing invented), `summary` is present, `source.reference` is in the fixed format, and the `durability` answers are all `pass`.
- Verify that the frontmatter and body conform to [entry-schema.md](../references/entry-schema.md) (the per-type section template), without re-encoding the schema inline.
- Verify that the `learn-id` umbrella was allocated (Capture is the allocating phase) and the `slug` is kebab-case and descriptive.
- Verify that, in `detailed` mode, the artifact is saved to `docs/learn/.capture/<capture-id>.md`; in `smart`/`autopilot` mode, verify that **no** file was written and the artifact was passed to the next phase in context.

> Pass the Captured Entry to `refine` (Phase 2) for type/frontmatter validation and the duplicate + analog check against existing entries.