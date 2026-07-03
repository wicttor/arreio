---
title: Scope
description: Gather context, check existing plans and learnings, validate domain, and return a scoped context object for downstream modules (research, design, generate).
type: Documentation
version: 1.0
timestamp: "2026-07-01"
---

# Phase 1 - Scope & Context Gathering

**Purpose:** Entry point to the planning workflow. Gathers context, checks existing plans and learnings, validates domain, and returns a scoped context object that downstream modules (research, design, generate) consume.

## Workflow

This is the Phase 1 pipeline for the Plan Skill. It orchestrates the following steps:

### Step 0: Verification

Before starting the **Scope** phase, verify that the Orchestrator skill has provided a valid **User Input Artifact**. If the artifact is missing or invalid, use the **[Error Handling & Recovery workflow](../references/error-handling.md)** to recover or terminate the plan.

### Step 1: Check for Existing Plan

1. Search `docs/plans/index.md` for existing plans related (grep title and description) to the task.
   - If the index file does not exist, assume no existing plans are present.
   - Ask the user via `ask_user_question` (multiple choice):
     ```
     The Plans Index was not found. Do you want to run the /arreio-init to create all the necessary folders, files, and index for planning? (Recommended)
     What would you like to do?
      - Yes: Run /arreio-init to create the planning structure
      - No: Skip and continue without creating the structure
     ```
   - If the user selects "Yes," run `/arreio-init` to create the necessary structure, then run the Step 1 of the Scope phase again to check for existing plans.

2. **If an existing plan is found:**
   - Read the plan to understand its title and goal. Plan files are stored in `docs/plans/` with naming format: `YYYY-MM-DD-NNN-plan.md` (e.g., `docs/plans/2026-07-02-001-plan.md`)
   - Ask the user via `ask_user_question` (multiple choice):
     ```
     An existing plan was found: "[Plan Title]"
     What would you like to do?
     - Resume: Continue working on this plan
     - Review: Read the plan before deciding
     - Archive: Keep for reference, mark as inactive
     - Delete: Remove the plan entirely
     - Create New: Start fresh
     ```
   - Handle each choice:
     - **Resume:** Use plan as-is; set `existing_plan.action: resume`, `existing_plan.path: docs/plans/YYYY-MM-DD-NNN-plan.md`
     - **Review:** Show plan summary, then re-prompt with same options
     - **Archive:** Move to archive; set `existing_plan.action: archive`, update `docs/plans/index.md` to mark as archived
     - **Delete:** Remove file; set `existing_plan.action: delete`, update `docs/plans/index.md` to remove entry
     - **Create New:** Keep old plan in archive; set `existing_plan.action: create-new`, `existing_plan.path: null`

3. **If no existing plan is found:**
   - Set `existing_plan.path: null`, `existing_plan.action: none`
   - Proceed to Step 2

### Step 2: Domain Validation

- Check if the context provided is a software/code planning task.
- This is important because the downstream skills (research, design, generate) are tailored for software planning.
- If the task is non-software, suggest a universal planning approach instead.

### Step 3: Bootstrap Problem Context

Evaluate if context is "rich enough" by checking the **User Input Artifact** contains **all three** of:

- Problem frame (clear problem statement)
- Intended behavior (desired outcome or deliverable)
- Success criteria (1-3 measurable criteria)

**If any of these three are missing or vague:**
Ask the user to provide additional context. Use the following questions to gather the necessary information:

1. **Problem Frame:** Ask "What problem are you trying to solve? Describe it in 1-2 sentences."
2. **Intended Behavior:** Ask "What should happen after this is implemented? Describe the desired outcome."
3. **Success Criteria:** Ask "How will we know this is complete? What specific outcomes define success?" Collect 1-3 criteria.

**If all three are present and concrete:**
Extract these from the **User Input Artifact** and proceed to Step 4 without asking follow-up questions.

### Step 4: Learnings Index Gate

Always search for project learnings (in `docs/learnings/index.md`) for entries matching the task description. For details on keyword matching, relevance rating, gap identification, and examples, see **[learnings-gate-logic.md](../references/learnings-gate-logic.md)**. Add HIGH and MEDIUM relevance learnings to `Related Learnings`; identify and document any learning gaps.

### Step 5: Requirements Search

1. Search `docs/` for files whose names or content match the task description.
   - Keywords: exact match on filename, grep content for relevant terms
   - If the directory does not exist, skip silently
   - ignore files in `docs/archives/`,`docs/plans/`, and `docs/learn/` (already handled in previous steps)
2. **For each match:**
   - Extract the title and a 1-2 sentence relevant excerpt
   - Add to `Requirements Found` list
3. If no matches found, set `Requirements Found` to empty.

### Step 6: Generate the Scoped Context Artifact

1. **Generate a unique `scope-id`** using the following template:
   - Format: `YYYY-MM-DD-NNN-scope` where `NNN` is a zero-padded 3-digit counter
   - **Algorithm (for new artifacts only):**
     - Get current date in UTC (e.g., 2026-07-02)
     - Check existing scoped context files in `docs/plans/.scope/` for today's date
     - Count existing files matching `2026-07-02-*.md`
     - Set `NNN = (count + 1)` formatted as zero-padded 3 digits (001, 002, 010, etc.)
     - Example: If two plans created today, next one gets `scope-id: 2026-07-02-003-scope`
   - **If user selected "Edit & Retry" in Step 7:**
     - Reuse the original `scope-id` from the previous artifact. Do NOT increment the counter.
     - Overwrite the existing artifact file.
   - **Error handling:** If `docs/plans/.scope/` does not exist, create it; treat count as 0 and start from 001

2. Produce a **Scoped Context Artifact** block (as markdown) with the schema defined in `../references/templates/artifacts/scoped-context.md`.
   - Include the generated `scope-id` in the artifact

### Step 7: Present and Confirm

1. Read the `interactionMode` value from the context (set by Orchestrator; see **[interaction-mode-propagation.md](../references/interaction-mode-propagation.md)** for details).

2. **If `interactionMode = detailed`:**
   - Present the assembled Scoped Context Artifact to the user via `ask_user_question` for explicit confirmation
   - Ask: "Is this context correct? Should I proceed to the research phase?"
   - Options: (1) Proceed to Research, (2) Edit & Retry, (3) Abort
   - If user selects "Edit & Retry," iterate through Steps 2-5 as needed
   - If user selects "Abort," stop and inform Orchestrator of abort
   - If user selects "Proceed," continue to Step 3 below

3. **If `interactionMode = smart`:**
   - Check for HIGH-risk flags in the Scoped Context:
     - Are there 3+ learning gaps?
     - Did domain validation flag non-software task?
     - Are requirements conflicting?
   - If HIGH-risk flag present: Pause and show artifact with risk description; ask "Should I proceed anyway?"
   - If no HIGH-risk flag: Auto-proceed (no confirmation)

4. **If `interactionMode = autopilot`:**
   - Auto-proceed immediately to save and return (no confirmation needed)

5. **Save the artifact:**
   - Save the Scoped Context Artifact (markdown block) to `docs/plans/.scope/<scope-id>.md`
   - Verify that `interactionMode` is included in the saved artifact (for downstream phases to read)

6. **Return to Orchestrator:**
   - Return the Scoped Context Artifact and `interactionMode` value to the Orchestrator skill
   - Orchestrator will handle transition to Phase 2 (Research) or abort based on confirmation result

## Output: Scoped Context Artifact

- Verify that the Scoped Context Artifact is complete and valid, containing all required fields, and it accurately reflects the user's input and any existing plans, learnings, or requirements found.
- Verify that the `interactionMode` value is set correctly based on the user's selection in the Orchestrator skill.
- Verify that the artifact is saved to `docs/plans/.scope/<scope-id>.md` for future reference or reuse.

> Pass the scoped context to `research` (Phase 2) for the research phase.
