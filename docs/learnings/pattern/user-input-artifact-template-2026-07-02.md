---
title: "User Input Artifact template for pipeline entry validation"
timestamp: "2026-07-02"
category: pattern
domain: template-design
tags: [skill-design, input-validation, artifact-schema, pipeline-entry]
severity: recommended
source: commit 3943146
---

# User Input Artifact Template for Pipeline Entry Validation

## Problem

Pipeline skills need a well-defined input format to validate completeness before processing. Without a schema, input can be ambiguous or incomplete, causing downstream phases to make incorrect assumptions or fail silently.

## Solution

Define a YAML-frontmatter + markdown template as the contract between the orchestrator and the first phase. Include required fields, optional fields, validation rules, and recovery workflows for each missing field.

### Required Fields

- **Task Description** — non-empty, < 500 chars, 1-3 sentences
- **Intended Behavior** — observable outcome description
- **Context Source** — one of: `user-prompt`, `saved-prompt`, `document`, `previous-plan`, `hybrid`

### Optional Fields

- **Goals & Objectives** — 1-3 specific success outcomes
- **Constraints & Limitations** — hard constraints
- **Additional Context** — freeform notes, links, references

### Recovery Workflow

| Field              | If Missing                                           |
| ------------------ | ---------------------------------------------------- |
| Task Description   | Ask: "What problem are you trying to solve?"         |
| Intended Behavior  | Ask: "What should happen after this is implemented?" |
| Goals & Objectives | Ask: "What specific outcomes define success?" (1-3)  |
| Constraints        | Ask: "Are there any hard constraints?"               |
| Context Source     | Infer from origin; ask if ambiguous                  |
| Additional Context | Skip if empty                                        |

## Application

- Use as the entry point artifact for any multi-phase pipeline
- First phase validates completeness before enrichment
- Abort if Task Description or Intended Behavior cannot be provided — ask user to return with more context

## Source

- `skills/plan/references/templates/artifacts/user-input.md` — Full template with schema, example, and recovery table
- Commit `3943146`
