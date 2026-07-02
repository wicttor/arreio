---
type: Documentation
title: Scope
---

# Phase 1 - Scope & Context Gathering

**Purpose:** Entry point to the planning workflow. Gathers context, checks existing plans and learnings, validates domain, and returns a scoped context object that downstream modules (research, design, generate) consume.

## Workflow

This is the Phase 1 pipeline for the Plan Skill. It orchestrates the following steps:

### Step 1: Check for Existing Plan

1. Search `docs/plans/` for existing plans related to the task.
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
   - Proceed to Step 1.5

---

### Step 1.5: Select Interaction Mode

Ask the user to choose their engagement level for this workflow. Use the platform's `ask_user_question` extension (or equivalent) to present the following three options:

**Question:** "How would you like to proceed with this workflow?"

**Options:**

- **Detailed (Step-by-Step)** — Review and confirm at each phase transition; inspect generated artifacts before proceeding; maximum control. Best for complex work, unfamiliar codebases, and learning.
- **Smart (Risk-gated automation)** — Phases run automatically; pause only when the next phase produces a HIGH-risk operation. v1 simplifies this to a single confirmation prompt at workflow start.
- **Yolo (Full Automation)** — Every phase runs automatically; only the final outcome is reported. Fastest. Best for straightforward, well-understood work and time-sensitive hotfixes.

Store the selection in the scoped context (replacing the placeholder in the schema above):

```yaml
interactionMode: detailed | smart | yolo
```

**Propagation:** The `interactionMode` value flows into `research`, `design`, and `generate` artifacts. Each downstream phase reads the value and adjusts its confirmation behavior:

- **Detailed:** Pause at every phase transition; show generated artifacts; require explicit approval.
- **Smart:** Run phases automatically; pause only at HIGH-risk operations.
- **Yolo:** Run every phase automatically; report only the final outcome.

### Step 2: Domain Validation

- Ask: "Is this a software/code planning task?"
- **If yes:** Set `domain: software`
- **If no:** Set `domain: non-software`
  - Note: Non-software planning is outside plan's scope. Suggest a universal planning approach instead. The downstream skills (research, design, generate) only support software planning.

### Step 3: Bootstrap Problem Context

If no existing context was found (no plan, no brainstorms/requirements), bootstrap from the user:

1. **Problem Frame:** Ask "What problem are you trying to solve? Describe it in 1-2 sentences."
2. **Intended Behavior:** Ask "What should happen after this is implemented? Describe the desired outcome."
3. **Success Criteria:** Ask "How will we know this is complete? What specific outcomes define success?" Collect 1-3 criteria.

If the user already provided rich context in the initial input, extract these from the input text and confirm with the user via `ask_user_question`.

### Step 4: Learnings Index Gate

Search project learnings (in `docs/learnings/INDEX.md`) for entries matching the task description. For details on keyword matching, relevance rating, gap identification, and examples, see **[learnings-gate-logic.md](references/learnings-gate-logic.md)**. Add HIGH and MEDIUM relevance learnings to `Related Learnings`; identify and document any learning gaps.

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

### Step 6: Confirm and Return Scoped Context

1. Present the assembled scoped context to the user via `ask_user_question` for confirmation.
2. Ask: "Is this context correct? Should I proceed to the research phase?"
3. **If confirmed:** Return the scoped context (markdown block as defined above).
4. **If corrections needed:** Iterate through Steps 2-5 as needed based on user feedback.
5. **Do not proceed to research/design/generation** — this skill only gathers context.

## Output: Scoped Context

After completing the workflow, produce a scoped context block (as markdown) with this schema:

```yaml
scope-id: YYYY-MM-DD-NNN-scope
domain: software | non-software
status: confirmed
interactionMode: detailed | smart | yolo

# Scoped Context

## Problem
[Clear statement of the problem frame]

## Intended Behavior
[Description of desired outcome]

## Success Criteria
- [Criterion 1]
- [Criterion 2]

## Existing Plan
path: docs/plans/...md | null
action: resume | review | archive | delete | create-new | none

## Related Learnings
- docs/learnings/XXX.md — [1-line applicability note]
- (List from docs/learnings/INDEX.md; empty list if none)

## Learning Gaps
- [Gap name] — [Follow-up action via /learnings]

## Requirements Found
- docs/brainstorms/XXX.md — [relevant excerpt]
- docs/requirements/XXX.md — [relevant excerpt]
- (Empty list if none found)
```

> This context is passed to `research` (S3) for the research phase.
