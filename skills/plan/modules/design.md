---
title: Design
description: Design the solution based on the scoped context and research findings. Decomposes the approach into phased implementation units, assesses complexity, and produces a Design Artifact for the Generate phase.
type: module
version: 1.0
timestamp: "2026-07-03"
---

# Phase 3 - Design

**Purpose:** Third step in the planning workflow. Reads the Scoped Context and Research Findings, selects an approach, decomposes it into phased implementation units, assesses complexity, and returns a [Design Artifact](../references/templates/artifacts/design.md) that the Generate phase renders into a final plan.

## Workflow

This is the Phase 3 pipeline for the Plan Skill. It orchestrates the following steps:

### Step 0: Verification

Before starting the **Design** phase, verify that the Orchestrator skill has provided valid **Scoped Context** and **Research Findings** artifacts from the previous phases. If either artifact is missing or invalid, use the **[Error Handling & Recovery workflow](../references/error-handling.md)** to recover or terminate the plan.

Specifically verify:

1. The Scoped Context artifact exists and contains `scope-id`, `domain`, `Problem`, `Intended Behavior`, and `Success Criteria`.
2. The Research Findings artifact exists and contains `research-id`, `Patterns Found`, `High-Risk Detection` (with `risk_level`), and `Tech Stack`.
3. The `interactionMode` is present in either artifact (default to `smart` if missing; log warning).
4. Cross-phase consistency: the `scope-id` referenced by the research artifact matches the scope output.

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
5. **Select the recommended approach.** If no clear winner emerges, present the top 2 to the user via `ask_user_question` and let them choose.
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

Break the approach into **phased implementation units**. Each unit is a coherent, testable chunk of work.

1. **Define phases** based on dependency layers:
   - **Phase 1: Foundation** — Units with no dependencies (infra, interfaces, schema)
   - **Phase 2: Integration** — Units depending on Phase 1 (wiring, middleware, adapters)
   - **Phase 3: Rollout** (if applicable) — Units for migration, feature flags, cutover

2. **For each unit, record:**
   - **Unit ID:** `U1`, `U2`, ... (never renumber; preserve across iterations)
   - **Name:** Short, descriptive
   - **Goal:** What this unit accomplishes (1 sentence)
   - **Dependencies:** Which unit IDs must complete first (or "None")
   - **Files:** `Create`, `Modify`, and `Test` paths — repository-relative, in backtick code formatting
   - **Test Scenarios:** `[Scenario]: [Input -> Expected Outcome]` (required for Phase 1–2 units; optional for rollout-only)

3. **Size check:** If a unit touches > 5 files or delivers 2+ separable outcomes, flag it for splitting in the Tasks phase (see [task-slicing-rules.md](../references/task-slicing-rules.md)).

4. **Dependency check:** Verify no cycles exist. A unit may only depend on units in earlier phases. If a cycle is detected, restructure the units.

### Step 4: Complexity Assessment

Score the design across five dimensions (0–3 each) and compute the complexity level. For the scoring table, dimension definitions, and threshold mapping, see **[design-complexity-assessment.md](../references/design-complexity-assessment.md)**.

1. Score each dimension:
   - `scope_breadth` — from the Implementation Units' file lists
   - `integration_surface` — from Research Findings' patterns and tech stack
   - `risk_level` — **inherited** from Research Findings (do not re-score)
   - `novelty` — compare chosen approach against `Patterns Found` confidence
   - `data_migration` — from the design's operational/rollout notes draft
2. Sum the scores (0–15).
3. Map to complexity level: `TRIVIAL | LOW | MEDIUM | HIGH | VERY_HIGH`.
4. Record all five scores, the total, and the complexity level in the Design Artifact.

### Step 5: Alternative Approaches

Document the approaches considered but not selected, with rejection rationale.

- **TRIVIAL / LOW complexity:** At least 1 alternative (may be brief).
- **MEDIUM complexity:** At least 1 alternative with rationale.
- **HIGH / VERY_HIGH complexity:** At least 2 alternatives with side-by-side rationale.

Format: `**[Approach Name]**: [Description] → **Rejected because:** [Rationale]`

### Step 6: Learnings and Gaps Update

1. **Carry forward** the `Related Learnings` and `Learning Gaps` from the Scoped Context.
2. **Add new learnings** discovered during design (e.g., a pattern confirmed or refuted).
3. **Add new gaps** the design revealed (e.g., "No learning on Redis failover in production").
4. Update both lists in the Design Artifact.

### Generate the Design Artifact

1. **Generate a unique `design-id`** using the daily counter algorithm:
   - Format: `YYYY-MM-DD-NNN-design` where `NNN` is a zero-padded 3-digit counter
   - **Algorithm:**
     - Get current date in UTC (e.g., 2026-07-03)
     - Check existing design files in `docs/plans/.design/` for today's date
     - Count existing files matching `2026-07-03-*.md`
     - Set `NNN = (count + 1)` formatted as zero-padded 3 digits (001, 002, 010, etc.)
     - Example: If two designs created today, next one gets `design-id: 2026-07-03-003-design`
   - **If user selected "Edit & Retry" in Step 7:**
     - Reuse the original `design-id` from the previous artifact. Do NOT increment the counter.
     - Overwrite the existing artifact file.
   - **Error handling:** If `docs/plans/.design/` does not exist, create it; treat count as 0 and start from 001

2. Produce a **Design Artifact** block (as markdown) with the schema defined in `../references/templates/artifacts/design.md`.
   - Include the generated `design-id`, inherited `scope-id` and `research-id`, `interactionMode`, `complexity`, and `tier_recommendation` (derived from complexity per [plan-tier-selection.md](../references/plan-tier-selection.md)).

### Step 7: Present and Confirm

1. Read the `interactionMode` value from the incoming artifact (or context; see **[interaction-mode-propagation.md](../references/interaction-mode-propagation.md)** for details).

2. **If `interactionMode = detailed`:**
   - Present the assembled Design Artifact to the user via `ask_user_question` for explicit confirmation
   - Ask: "Does this design capture the right approach and units? Should I proceed to the generate phase?"
   - Options: (1) Proceed to Generate, (2) Edit & Retry, (3) Abort
   - If user selects "Edit & Retry," iterate through Steps 1–6 as needed (reuse the `design-id`)
   - If user selects "Abort," stop and inform Orchestrator of abort
   - If user selects "Proceed," continue to save and return

3. **If `interactionMode = smart`:**
   - Check for pause triggers:
     - Is `complexity = VERY_HIGH`?
     - Did research report HIGH risk with `patterns_found_count < 3`?
     - Are there 3+ learning gaps from the Scope phase?
     - Does the selected approach have no local pattern precedent (Novelty = 3)?
   - If any pause trigger is true: Pause and show the artifact with the trigger explanation; ask "Should I proceed anyway?"
   - If no pause trigger: Auto-proceed (no confirmation)

4. **If `interactionMode = autopilot`:**
   - Auto-proceed immediately to save and return (no confirmation needed)

5. **Save the artifact:**
   - Save the Design Artifact (markdown block) to `docs/plans/.design/<design-id>.md`
   - Verify that `interactionMode`, `complexity`, and `tier_recommendation` are included in the saved artifact (for the Generate phase to read)

6. **Return to Orchestrator:**
   - Return the Design Artifact and `interactionMode` value to the Orchestrator skill
   - Orchestrator will handle transition to Phase 4 (Generate) or abort based on confirmation result

## Output: Design Artifact

- Verify that the Design Artifact is complete and valid, containing all required fields: `design-id`, `scope-id`, `research-id`, `interactionMode`, `complexity`, `tier_recommendation`, Approach, High-Level Technical Design, Implementation Units, Complexity Assessment, Alternative Approaches, Related Learnings, and Learning Gaps.
- Verify that the `complexity` value matches the threshold mapping from the five dimension scores.
- Verify that the `tier_recommendation` is consistent with the complexity and risk level per [plan-tier-selection.md](../references/plan-tier-selection.md).
- Verify that the artifact is saved to `docs/plans/.design/<design-id>.md` for future reference or reuse.

> Pass the design artifact to `generate` (Phase 4) for final plan generation.
