---
title: Generate
description: Render the final plan from the Design Artifact by selecting a tier, filling the plan template, and saving it to docs/plans/. Produces a Final Plan Artifact for the optional Tasks phase.
type: module
version: 1.0
timestamp: "2026-07-03"
---

# Phase 4 - Generate

**Purpose:** Fourth step in the planning workflow. Reads the Design Artifact, selects a plan tier (Fast/Standard/Deep) based on complexity and risk, renders the final plan from the [Final Plan template](../references/templates/artifacts/final-plan.md), and saves it to `docs/plans/`. Returns a [Final Plan Artifact](../references/templates/artifacts/final-plan.md) that the optional Tasks phase consumes.

## Workflow

This is the Phase 4 pipeline for the Plan Skill. It orchestrates the following steps:

### Step 0: Verification

Before starting the **Generate** phase, verify that the Orchestrator skill has provided a valid **Design Artifact** from the previous phase. If the artifact is missing or invalid, use the **[Error Handling & Recovery workflow](../references/error-handling.md)** to recover or terminate the plan.

Specifically verify:

1. The Design Artifact exists and contains `design-id`, `scope-id`, `research-id`, `interactionMode`, `complexity`, `tier_recommendation`, `Approach`, `High-Level Technical Design`, and `Implementation Units`.
2. The `complexity` field is one of: `TRIVIAL`, `LOW`, `MEDIUM`, `HIGH`, `VERY_HIGH`.
3. The `interactionMode` is present and valid (default to `smart` if missing; log warning).
4. Cross-phase consistency: the `scope-id` and `research-id` match the upstream artifacts.

### Step 1: Tier Selection

Select the plan tier based on complexity, risk, and user preference. For the full algorithm, risk floor rules, and tier section requirements, see **[plan-tier-selection.md](../references/plan-tier-selection.md)**.

1. **Read inputs:**
   - `complexity` from the Design Artifact
   - `risk_level` from the Research Findings (carried via the Design Artifact's complexity assessment)
   - `tier_recommendation` from the Design Artifact (the algorithm's suggestion)

2. **Determine user preference:**
   - In **Detailed** mode: Ask the user via `ask_user_question` which tier they want, presenting the recommendation. Options: `Fast`, `Standard`, `Deep`, `Auto`.
   - In **Smart** mode: Auto-select, unless a pause trigger fires (Deep tier, preference conflicts with risk floor, or CRITICAL risk). If paused, ask the user.
   - In **Autopilot** mode: Set `user_preference = auto`; never ask.

3. **Apply the selection algorithm** (see [plan-tier-selection.md](../references/plan-tier-selection.md)):
   - Start from the complexity-driven default tier.
   - Upgrade if risk warrants it (respect the risk floor).
   - Honor user preference unless it violates the risk floor.

4. **Record the selected tier** as `tier` and the algorithm's recommendation as `tier_recommended` (for audit when the user overrides).

### Step 2: Plan Rendering

Render the final plan from the [Final Plan template](../references/templates/artifacts/final-plan.md), including only the sections required by the selected tier.

1. **Assemble frontmatter:**

   ```yaml
   plan-id: YYYY-MM-DD-NNN
   type: plan
   title: "[Plan title]"
   status: complete
   tier: fast | standard | deep
   tier_recommended: fast | standard | deep
   complexity: TRIVIAL | LOW | MEDIUM | HIGH | VERY_HIGH
   risk: Low | Medium | High | Critical
   scope-id: YYYY-MM-DD-NNN-scope
   research-id: YYYY-MM-DD-NNN-research
   design-id: YYYY-MM-DD-NNN-design
   interactionMode: detailed | smart | autopilot
   created: YYYY-MM-DD
   updated: YYYY-MM-DD
   version: 1.0
   ```

2. **Render sections per tier** (see [plan-tier-selection.md](../references/plan-tier-selection.md) for the full section list):

   | Section                       | Fast | Standard | Deep |
   | ----------------------------- | :--: | :------: | :--: |
   | Overview                      |  ✅  |    ✅    |  ✅  |
   | High-Level Technical Design   |  ✅  |    ✅    |  ✅  |
   | Implementation Units (Phased) |  ✅  |    ✅    |  ✅  |
   | Alternative Approaches        |  ➖  |    ✅    |  ✅  |
   | Risk Analysis & Mitigation    |  ✅  |    ✅    |  ✅  |
   | Operational / Rollout Notes   |  ➖  |    ✅    |  ✅  |
   | Related Learnings             |  ✅  |    ✅    |  ✅  |
   | Learning Gaps                 |  ➖  |    ✅    |  ✅  |

   Legend: ✅ required, ➖ optional (skip if not applicable).

3. **Carry forward content from the Design Artifact:**
   - `Approach` → Overview
   - `High-Level Technical Design` → High-Level Technical Design
   - `Implementation Units` → Implementation Units (Phased)
   - `Alternative Approaches` → Alternative Approaches Considered
   - `Related Learnings` → Related Learnings
   - `Learning Gaps` → Learning Gaps

4. **Build the Risk Analysis table** from the Research Findings' high-risk detection and the Design's complexity:
   - Each risk row: `| [Specific risk] | High/Medium | [Concrete mitigation] |`
   - Fast tier: 1–2 rows (brief)
   - Standard tier: full table covering all detected high-risk areas
   - Deep tier: full table with impact ratings + rollback plan

5. **Build Operational / Rollout Notes** (Standard/Deep only) from the Design's rollout units:
   - Feature flags, monitoring, data migration, rollback plan, performance baseline
   - Skip the section entirely if not applicable (Fast tier, or no rollout units)

6. **Right-size:** Per Plan Skill core principles — small tasks → short plans; complex work → more structure. Do not pad a Fast plan with empty sections; do not omit required sections from a Deep plan.

### Step 3: Plan ID Generation

1. **Generate a unique `plan-id`** using the daily counter algorithm:
   - Format: `YYYY-MM-DD-NNN` where `NNN` is a zero-padded 3-digit counter
   - **Algorithm:**
     - Get current date in UTC (e.g., 2026-07-03)
     - Check existing plan files in `docs/plans/` for today's date
     - Count existing files matching `2026-07-03-*.md` (excluding the `.scope/`, `.research/`, `.design/` subdirectories)
     - Set `NNN = (count + 1)` formatted as zero-padded 3 digits (001, 002, 010, etc.)
     - Example: If two plans created today, next one gets `plan-id: 2026-07-03-003`
   - **If user selected "Edit & Retry" in Step 5:**
     - Reuse the original `plan-id` from the previous artifact. Do NOT increment the counter.
     - Overwrite the existing plan file.
   - **Error handling:** If `docs/plans/` does not exist, create it; treat count as 0 and start from 001

2. **Derive the plan filename:**
   - Format: `docs/plans/YYYY-MM-DD-NNN-<kebab-case-name>.md`
   - The `<kebab-case-name>` is derived from the plan title (lowercase, hyphens, no stopwords)
   - Example: `docs/plans/2026-07-03-001-migrate-session-storage-to-redis.md`

### Step 4: Assemble and Save

1. **Assemble the complete plan document** by combining the frontmatter (Step 2.1) with the rendered sections (Step 2.2–2.6).
2. **Set the `plan-id` field** in the frontmatter to the generated `plan-id`.
3. **Save the plan** to `docs/plans/YYYY-MM-DD-NNN-<kebab-case-name>.md`.

### Step 5: Update Plans Index

Append an entry to `docs/plans/index.md`:

```markdown
| [YYYY-MM-DD-NNN](YYYY-MM-DD-NNN-<kebab-case-name>.md) | [Plan Title] | [tier] | [complexity] | [risk] | ready |
```

If `docs/plans/index.md` does not exist, create it with a header row and the new entry. If it exists but is malformed, log a warning and append the entry without reformatting existing rows.

### Step 6: Present and Confirm

1. Read the `interactionMode` value from the incoming Design Artifact (see **[interaction-mode-propagation.md](../references/interaction-mode-propagation.md)** for details).

2. **If `interactionMode = detailed`:**
   - Present the assembled Final Plan to the user via `ask_user_question` for explicit confirmation
   - Ask: "Is this plan ready? Should I proceed to task generation?"
   - Options: (1) Proceed to Tasks, (2) Edit & Retry, (3) Skip Tasks, (4) Abort
   - If user selects "Edit & Retry," iterate through Steps 1–4 as needed (reuse the `plan-id`)
   - If user selects "Skip Tasks," save the plan and inform the Orchestrator that the plan is complete (no task slicing)
   - If user selects "Abort," stop and inform Orchestrator of abort
   - If user selects "Proceed," continue to return

3. **If `interactionMode = smart`:**
   - Check for pause triggers:
     - Is the selected tier `Deep`?
     - Did the user's tier preference conflict with the risk floor?
     - Did research report CRITICAL risk (Security or Payments)?
   - If any pause trigger is true: Pause and show the plan summary with the trigger explanation; ask "Should I proceed to tasks?"
   - If no pause trigger: Auto-proceed (no confirmation)

4. **If `interactionMode = autopilot`:**
   - Auto-proceed immediately to return (no confirmation needed)
   - The Tasks phase (Phase 5) will still ask the user before creating task files, per the interaction-mode spec

5. **Return to Orchestrator:**
   - Return the Final Plan Artifact (path, `plan-id`, `tier`, `interactionMode`) to the Orchestrator skill
   - Orchestrator will handle transition to Phase 5 (Tasks) — which is optional and always asks the user — or mark the plan as complete

## Output: Final Plan Artifact

- Verify that the Final Plan is complete and valid, containing all required frontmatter fields (`plan-id`, `type`, `title`, `status`, `tier`, `complexity`, `risk`, `scope-id`, `research-id`, `design-id`, `interactionMode`, `created`, `updated`, `version`) and all tier-required sections.
- Verify that all file paths in the plan are repository-relative (never absolute) and wrapped in backtick code formatting.
- Verify that `## Related Learnings` is present and references `docs/learnings/index.md` entries (or states "No relevant learnings found").
- Verify that `## Learning Gaps` is present (may be empty).
- Verify that the plan is saved to `docs/plans/YYYY-MM-DD-NNN-<kebab-case-name>.md` and registered in `docs/plans/index.md`.

> The Final Plan is the primary deliverable of the Plan Skill. Pass it to `tasks` (Phase 5, optional) for task slicing, or mark the plan as complete if the user declines tasks.
