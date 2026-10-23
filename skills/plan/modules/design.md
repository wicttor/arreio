---
title: Design
description: Design the solution based on the scoped context and research findings. Decomposes the approach into phased implementation units, assesses complexity, and produces a Design Artifact for the Generate phase.
type: module
version: 1.2
timestamp: "2026-10-23"
---

# Phase 3 - Design

**Purpose:** Third step in the planning workflow. Reads the Scoped Context and Research Findings, selects an approach, decomposes it into phased implementation units, assesses complexity, and returns a [Design Artifact](../references/templates/artifacts/design.md) that the Generate phase renders into a final plan.

## Workflow

This is the Phase 3 pipeline for the Plan Skill. It orchestrates the following steps:

### Step 0: Verification

Run the **[Step 0 verification](../references/error-handling.md)**. Required inputs:

1. **Scoped Context Artifact** with `scope-id`, `domain`, `Problem`, `Intended Behavior`, `Success Criteria`, `Source of Truth`, and a non-empty `Source Inventory`.
2. **Research Findings Artifact** with `research-id`, `Patterns Found`, `Codebase Trace` (a row per Source Inventory item), `High-Risk Detection` (with `risk_level`), `Tech Stack`. A missing or empty trace sends the run back to Research.
3. `interactionMode` present (default to `smart` if missing; log warning).
4. Cross-phase consistency: the research artifact's `scope-id` matches the scope output.
5. `force_deep` (boolean from the Orchestrator context; default `false`). It never changes `complexity` or `tier_recommended`; it only raises the amount of material this phase must produce (Steps 4–5).

### Step 1: Approach Selection

1. **Read the Scoped Context** to understand the problem, intended behavior, and success criteria.
2. **Read the Research Findings** to identify available patterns, confidence levels, high-risk areas, and technical constraints.
3. **Draft 2–3 candidate approaches** that satisfy the success criteria. Base each on:
   - Patterns found in the codebase (prefer HIGH-confidence patterns when available)
   - Tech stack constraints from research
   - Risk level and whether external research was conducted
4. **Evaluate each approach** against:
   - Fit with success criteria
   - Pattern reuse (higher confidence = lower risk)
   - Complexity (fewer integration points = simpler)
   - Reversibility (can it be rolled back?)
5. **Select the recommended approach.** If no clear winner emerges, present the top 2 to the user in one question and let them choose.
6. **Record the selected approach** as a 1–3 sentence summary in the Design Artifact's `Approach` field, including why it fits the context and research.

### Step 2: High-Level Technical Design

Produce a **directional** design representation (NOT an implementation specification). Choose ONE of:

- **Mermaid diagram** — Use `sequenceDiagram`, `flowchart`, or `graph` to show component interaction. Best for multi-actor flows.
- **Pseudo-code sketch** — High-level steps in plain language. Best for algorithmic/logic-heavy work.
- **Data-flow map** — ASCII arrows showing how data moves through the system. Best for pipeline/ETL work.

The design must:

- Reference real components, files, or services from the research findings (be concrete)
- Show the "happy path" only; edge cases go in the Implementation Units
- Avoid implementation details (naming, abstractions, code structure) — those are decided during execution

> **Note:** This is directional guidance for review, not an implementation specification to copy. The implementation phase will determine specific naming, abstractions, and code structure.

### Step 3: Implementation Unit Decomposition

Break the approach into **phased implementation units** that cover the Scope phase's **Source Inventory**, and nothing else. Each unit is a coherent, testable chunk of work. Follow [plan-coverage-rules.md](../references/plan-coverage-rules.md).

0. **Map first, then design units.** Start from the Source Inventory: one unit per source item is the default; each unit declares `Source: <item id>`. Merge units that share one source item and one file set. Split an item into several units only when one unit would exceed 5 files or about one day; write the reason for the Source Coverage table. Every inventory item ends up covered by a unit or listed as excluded with a reason quoted from the source. A unit with no source item does not belong in the plan: drop it or move the doubt to `Open Decisions`.

1. **Define phases** based on dependency layers:
   - **Phase 1: Foundation** — Units with no dependencies (infra, interfaces, schema)
   - **Phase 2: Integration** — Units depending on Phase 1 (wiring, middleware, adapters)
   - **Phase 3: Rollout** (if applicable) — Units for migration, feature flags, cutover

2. **For each unit, record:**
   - **Unit ID:** `U1`, `U2`, ... in ascending document order; letter suffixes (`U2a`) are reserved for the Tasks phase
   - **Name:** Short, descriptive
   - **Source:** the Source Inventory item ID(s) the unit implements
   - **Goal:** What this unit accomplishes (1 sentence)
   - **Dependencies:** Which earlier unit IDs must complete first (or "None")
   - **Files:** `Create`, `Modify`, and `Test` paths: exact repository-relative paths in backtick code formatting. A glob is allowed only for a generated set with its count. Never write "as needed", "if required", or "etc."; an unknown path becomes an Open Decision.
   - **Excluded:** (optional) what the source defers that a reader might expect here, with the source reference
   - **Acceptance Criteria:** A list of one or more checkable criteria. **Each criterion later becomes exactly one task and one test** (see Tasks phase). Phrase each as a single, verifiable outcome — not a bundle.
   - **Test Scenarios:** `[Scenario]: [Input -> Expected Outcome]` (required for Phase 1–2 units; optional for rollout-only)

3. **Decomposition check:** The unit count is capped at 1.5 × the covered source items (rounded up). Above the cap, merge units; if a split is genuinely needed, add a `Justification:` line under the Source Coverage table. Do not add units to keep tasks small: the Tasks phase splits criteria into tasks later (see [task-slicing-rules.md](../references/task-slicing-rules.md)), and that never changes the plan's unit count. Do not put execution steps (red/green/refactor, per-task file limits) in the plan.

4. **Dependency check:** Verify no cycles exist. A unit may only depend on units in earlier phases. If a cycle is detected, restructure the units.

### Step 3b: Integrity Checks

A plan can cover every source item and still be unbuildable. Before the units are final, run these checks against the **Codebase Trace** from Research and record each result in the `Integrity Checks` table. Do the work; a row is `ok`, `fixed in U<n>` (the unit now carries the fix), or `OD<n>`. None may stay open.

1. **Layering.** For every unit dependency and every cross-module call a unit introduces, confirm the direction is allowed by the layer rule in the trace. When a lower layer needs to be called by code that the higher layer owns (a rule that uses a service which depends on the rules), add the interface or port to the lower layer, inside the earliest unit that can own it. Never build a dependency the rule forbids.
2. **Seams and interfaces.** For every interface, seam or port a unit introduces, list the operations each consumer unit needs from it (name the consumer). Any needed operation the seam lacks becomes an acceptance criterion on the unit that owns the seam.
3. **Effect owners.** Every unit that needs time, randomness, IDs, file or network I/O, or persistence names the unit whose files hold the production implementation (a test fake is not enough). No owner means a missing file entry or an Open Decision.
4. **Hook points.** Every behavior wired into existing code (damage, death, input, lifecycle, save/load) has the existing call site from the trace in some unit's `Modify` list, and the unit that listens or feeds is named.
5. **Data and content.** Every unit that changes a data shape lists the schema, the content or asset files, and the importer or baker that must change, and records any editing constraint from the trace. A shape change with no consumer update is a defect.
6. **State that must survive.** For each piece of state a unit says persists across restarts or replays, name the unit that writes it and the unit that reads it back. A writer without a reader, or the reverse, is a defect.
7. **Old versus new types.** For each overlap in the trace, state the relation (replace, wrap, coexist) in the unit that introduces the new type, and make criteria that depend on a field the old type lacks explicit.
8. **Numbers and snippets.** Do not write file or test counts in prose; the gate recounts them. Example snippets and test scenarios use the field names and shapes of the schemas they cite, copied from the source or the code.
9. **Preconditions.** If the source lists a step, manual check or decision that must be done first and the trace shows it is still pending, the dependent unit says so in its Dependencies or the plan raises an Open Decision.

If a check needs a fact the trace does not contain, go back to the code and read it; do not guess. A fix must not add a unit that no source item backs: extend an existing unit's files and criteria, or write an Open Decision.

### Step 4: Complexity Assessment

Score the design across four dimensions (0–3 each) and compute the complexity level. For the scoring table, dimension definitions, and threshold mapping, see **[design-complexity-assessment.md](../references/design-complexity-assessment.md)**.

1. Score each dimension:
   - `scope_breadth` — from the Implementation Units' file lists
   - `integration_surface` — from Research Findings' patterns and tech stack
   - `novelty` — compare chosen approach against `Patterns Found` confidence
   - `data_migration` — from the design's operational/rollout notes draft
2. Sum the scores (0–12). `risk_level` is inherited from Research Findings and is **not** part of the sum; it only feeds the tier floor in step 5.
3. Map to complexity level: `TRIVIAL | LOW | MEDIUM | HIGH | VERY_HIGH`.
4. Record the four scores, the total, the inherited `risk_level` (not scored), and the complexity level in the Design Artifact.
5. **Compute `tier_recommended`** by evaluating `recommend_tier(complexity, risk_level)` from [plan-tier-selection.md](../references/plan-tier-selection.md) with the actual values from steps 1–3 (complexity-driven default, then the risk floor). Apply the Anti-Default Rules there: `HIGH`/`VERY_HIGH` → `deep`, `MEDIUM` → `standard`, `TRIVIAL`/`LOW` → `fast`, raised only by risk. Do not ignore `risk_level`, and do not pick `standard` by default. `force_deep` and user preference do **not** affect this value.
6. **If `force_deep` is true:** also draft rollout notes (feature flags, monitoring, data migration, rollback, performance baseline — or `Not applicable — <reason>` per item) and a cross-system integration map so Generate can fill the Deep sections from real content. When the work has no deployed users, data, or services, one line is enough: `Not applicable — <reason>` for the whole rollout section.

### Step 5: Alternative Approaches

Document the approaches considered but not selected, with rejection rationale.

- **TRIVIAL / LOW complexity:** At least 1 alternative (may be brief).
- **MEDIUM complexity:** At least 1 alternative with rationale.
- **HIGH / VERY_HIGH complexity, or `force_deep` is true:** At least 1 alternative with rationale, and a second one only when it was genuinely considered. If the source of truth already fixes the approach, say so in one line and list only the alternatives that were real. Never invent an alternative to fill a count.

Format: `**[Approach Name]**: [Description] → **Rejected because:** [Rationale]`

### Step 6: Learnings and Gaps Update

1. **Carry forward** the `Related Learnings` and `Learning Gaps` from the Scoped Context.
2. **Add new learnings** discovered during design (e.g., a pattern confirmed or refuted).
3. **Add new gaps** the design revealed (e.g., "No learning on Redis failover in production").
4. Update both lists in the Design Artifact.
5. **Open Decisions.** Collect anything the source of truth does not settle (missing values, conflicting contracts, unknown paths). Write each as `OD<n>: [question] — Recommended: [default and why] — Affects: [units]`. Never add a gate unit, never edit accepted source documents, never schedule a spec change as a unit unless the Source Inventory contains it. Write `None.` when empty.

### Generate the Design Artifact

1. **Assign a `design-id`** per [id-generation.md](../references/id-generation.md) (format `YYYY-MM-DD-NNN-design`, saved to `docs/plans/.design/`). Reuse it if the user later picks **Edit & Retry**.

2. Produce a **Design Artifact** block (as markdown) following the schema in [design.md](../references/templates/artifacts/design.md).
   - Include the generated `design-id`, inherited `scope-id` and `research-id`, `interactionMode`, `complexity`, and `tier_recommended` (the value computed in Step 4.5 — never re-derive it from complexity alone).
   - Include the `Source Coverage` mapping (inventory item → units or exclusion), the compact `Codebase Trace` (item → touched files and layer, copied from Research), the `Integrity Checks` table, and the `Open Decisions` list.
   - **Announce the coverage line in every mode:** `Coverage: N source items -> M units (xR), K excluded`.

### Step 7: Present, Confirm, and Save

Apply the **[phase confirmation behavior](../references/interaction-mode-propagation.md)** for the current `interactionMode`, using these design-specific **Smart pause triggers**:

- `complexity = VERY_HIGH`, or
- Research reported HIGH risk with `patterns_found_count < 3`, or
- 3+ learning gaps carried from Scope, or
- The selected approach has no local pattern precedent (Novelty = 3), or
- The unit count exceeds the coverage cap (Step 3.3), or
- Open Decisions block 3+ units, or
- An Integrity Check is resolved as an Open Decision for a blocking layering or persistence problem.

- **Detailed:** present the Design Artifact and ask one question with options *(1) Proceed to Generate, (2) Edit & Retry, (3) Abort*. On **Edit & Retry**, loop back through Steps 1–6 reusing the `design-id`. On **Abort**, stop and inform the Orchestrator.
- **Smart:** pause only when a pause trigger above is true; otherwise auto-proceed.
- **Autopilot:** auto-proceed (no confirmation).

Then, **in every mode**, save the artifact to `docs/plans/.design/<design-id>.md` (ensure `interactionMode`, `complexity`, and `tier_recommended` are included) and return it, with the `interactionMode` value, to the Orchestrator for the transition to Phase 4 (Generate). The Design artifact is small and is the audit trail for how the Source Inventory became units (see [Artifact Persistence](../references/interaction-mode-propagation.md#artifact-persistence)).

## Output: Design Artifact

- Verify that the Design Artifact is complete and valid, containing all required fields: `design-id`, `scope-id`, `research-id`, `interactionMode`, `complexity`, `tier_recommended`, Approach, High-Level Technical Design, Codebase Trace, Implementation Units (each with Source and Acceptance Criteria), Integrity Checks, Source Coverage, Complexity Assessment, Alternative Approaches, Open Decisions, Related Learnings, and Learning Gaps.
- Verify the coverage: every Source Inventory item is covered or excluded with a reason, every unit has a `Source`, the unit count is within the cap (or justified), unit IDs ascend, and every dependency is an earlier unit.
- Verify that no `Files` entry says "as needed", "if required", or "etc.", that every `Modify` path appears in the Codebase Trace or was opened, and that no file is created by two units.
- Verify that `Integrity Checks` has all nine rows, none left open.
- Verify that the `complexity` value matches the threshold mapping from the four dimension scores.
- Verify that `tier_recommended` equals `recommend_tier(complexity, risk_level)` per [plan-tier-selection.md](../references/plan-tier-selection.md) (e.g., `complexity: HIGH` → `deep`, not `standard`).
- Verify that, when `force_deep` is true, the artifact contains the rollout/integration drafts from Step 4.6 and at least one real alternative.
- Verify that the artifact is saved to `docs/plans/.design/<design-id>.md` in every mode.

> Pass the design artifact to `generate` (Phase 4) for final plan generation.
