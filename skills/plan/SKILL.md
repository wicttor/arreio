---
type: skill
title: Plan
name: plan
description: Create structured implementation plans with three tiers, Fast, Standard, Deep. Orchestrates scope, research, design, and generation phases.
group: plan
argument-hint: "[task description, requirements doc, or goal to plan]"
tags:
  - planning
  - architecture
  - structured-output
author: "@wicttor"
---

# Plan

Create durable implementation plans that can be handed off for execution. Orchestrates a deterministic pipeline of micro-skills: scope → research → design → generate.

## Purpose

Plans capture decisions, structure, and approach before execution. They enable into the project:

- Remove uncertainty about the implementation
- Clarify ambiguities regarding the request, idea or prompt provided
- Clear scope and success criteria
- Identified risks and dependencies
- Concrete implementation units with acceptance criteria
- Knowledge reuse through related learnings
- Confidence that work won't go off the rails

## Core Workflow: Phased pipeline

```
INPUT (task description)
  ↓
PHASE 1: Scope (plan-scope)
  → Gather context, validate domain, bootstrap requirements
  → Output: Scoped context artifact
  ↓
PHASE 2: Research (plan-research)
  → Discover patterns, identify risks, recommend external research
  → Output: Research findings artifact
  ↓
PHASE 3: Design (plan-design)
  → Decompose into units, map dependencies, assess complexity
  → Output: Design artifact with unit decomposition
  ↓
PHASE 4: Generate (plan-generate)
  → Select tier, render plan, embed learnings, save to docs/plans/
  → Output: Final plan document saved to file
  ↓
OUTPUT (plan file ready for execution)
```

## Workflow

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

- Proceed to Step 2

### Step 2: Domain Validation

- Ask: "Is this a software/code planning task?"
- **If yes:** Set `domain: software`
- **If no:** Set `domain: non-software`

Note: Non-software planning is outside plan's scope. Suggest a universal planning approach instead. The downstream skills (plan-research, plan-design, plan-generate) only support software planning.

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
