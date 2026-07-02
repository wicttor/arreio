---
title: Scope
type: Documentation
version: 1.0
date: 2026-07-01
---

# Phase 1 - Scope & Context Gathering

**Purpose:** Entry point to the planning workflow. Gathers context, checks existing plans and learnings, validates domain, and returns a scoped context object that downstream modules (research, design, generate) consume.

## Workflow

This is the Phase 1 pipeline for the Plan Skill. It orchestrates the following steps:

### Step 0: Verification

Before starting the **Scope** phase, verify that the Orchestrator skill has provided a valid **User Input Artifact**.
If the artifact is missing or invalid, use the **Error Handling & Recovery workflow** to recover or terminate the plan.

### Step 1: Check for Existing Plan

1. Search `docs/plans/index.md` for existing plans related to the task.
2. **If an existing plan is found:**
   - Read the plan to understand its title and goal.
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
     - **Resume:** Use plan as-is; set `existing_plan.action: resume`
     - **Review:** Show plan summary, then re-prompt with same options
     - **Archive:** Move to archive; set `existing_plan.action: archive`
     - **Delete:** Remove file; set `existing_plan.action: delete`
     - **Create New:** Keep old plan; set `existing_plan.action: create-new`

3. **If no existing plan is found:**
   - Set `existing_plan.path: null`, `existing_plan.action: none`
   - Proceed to Step 2

### Step 2: Domain Validation

- Check if the context provided is a software/code planning task.
- This is important because the downstream skills (research, design, generate) are tailored for software planning.
- If the task is non-software, suggest a universal planning approach instead.

### Step 3: Bootstrap Problem Context

If the context provided by the Orchestrator is not rich enough, not relevant for the current project, or missing key information, ask the user to provide additional context. Use the following questions to gather the necessary information:

1. **Problem Frame:** Ask "What problem are you trying to solve? Describe it in 1-2 sentences."
2. **Intended Behavior:** Ask "What should happen after this is implemented? Describe the desired outcome."
3. **Success Criteria:** Ask "How will we know this is complete? What specific outcomes define success?" Collect 1-3 criteria.

If the user already provided rich context in the initial input, extract these from the **User Input Artifact**.

### Step 4: Learnings Index Gate

Always search for project learnings (in `docs/learnings/index.md`) for entries matching the task description. For details on keyword matching, relevance rating, gap identification, and examples, see **[learnings-gate-logic.md](references/learnings-gate-logic.md)**. Add HIGH and MEDIUM relevance learnings to `Related Learnings`; identify and document any learning gaps.

### Step 5: Requirements Search

1. Search `docs/brainstorms/` for files whose names or content match the task description.
   - Keywords: exact match on filename, grep content for relevant terms
   - If the directory does not exist, skip silently
2. Search `docs/requirements/` for matching files.
   - Same approach as brainstorms
3. **For each match:**
   - Extract the title and a 1-2 sentence relevant excerpt
   - Add to `Requirements Found` list
4. If no matches found, set `Requirements Found` to empty.

### Step 6: Generate the Scoped Context Artifact

Produce a Scoped Context Artifact block (as markdown) with the schema defined in `references/templates/artifacts/scoped-context.md`.

### Step 7: Confirm and Return Scoped Context Artifact

1. Present the assembled Scoped Context Artifact to the user via `ask_user_question` for confirmation.
2. Ask: "Is this context correct? Should I proceed to the research phase?"
3. **If confirmed:** Save the Scoped Context Artifact (markdown block as defined above) to `docs/plans/.scope/<scope-id>.md`.
4. **If corrections needed:** Iterate through Steps 2-5 as needed based on user feedback.
5. **Do not proceed to Research Phase** — Stop here and return the negative confirmation to the Orchestrator skill. The Orchestrator will handle the next steps based on user input.

## Output: Scoped Context Artifact

- Verify that the Scoped Context Artifact is complete and valid, containing all required fields, and it accurately reflects the user's input and any existing plans, learnings, or requirements found.
- Verify that the `interactionMode` value is set correctly based on the user's selection in the Orchestrator skill.
- Verify that the artifact is saved to `docs/plans/.scope/<scope-id>.md` for future reference or reuse.

> Pass the scoped context to `research` (Phase 2) for the research phase.
