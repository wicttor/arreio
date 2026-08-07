---
title: "Describe required capabilities, not tool names, in portable skills"
timestamp: "2026-08-07"
category: pattern
domain: skill-design
tags: [portability, agent-agnostic, tooling, skills, prompts]
severity: important
source: commit 40b4808
applicability:
  current_project: 9
  general: 10
related:
  - pipeline-phase-module-template-2026-07-04
---

# Describe Required Capabilities, Not Tool Names, in Portable Skills

## Problem

A skill that aims to be code-agent-agnostic hardcoded specific tool names:

- `grep_search` / `semantic_search` (Cursor/Cline-specific search tools) in the Research phase.
- `ask_user_question` (a single harness's interactive-question extension) as the sole interaction mechanism, spelled out in 8 files.

On an agent without those exact tools (Claude Code, Aider, plain shell, etc.), the steps become non-executable: the agent either invents the tool or stalls.

## Solution

Describe the **required capability**, then let each agent map to its native tool:

| Don't write                       | Write instead                                                                   |
| --------------------------------- | ------------------------------------------------------------------------------- |
| Run `grep_search` for "auth"      | Search the codebase for the literal pattern "auth"                              |
| Run `semantic_search`             | Run a meaning-based search using the task description as the query              |
| Ask the user via `ask_user_question` | Ask the user one question with 2–4 concrete options                          |

The capability description is stable; the tool mapping is the agent's concern. Include a single short statement of the interaction contract ("ask one question at a time, 2–4 concrete options") in the orchestrator rather than naming a tool in every phase.

## Prevention

- Audit skill text for tool-name tokens (`_search`, tool identifiers, harness-specific extensions) before declaring a skill "agent-agnostic."
- Keep tool names, if any, in a side "capabilities assumed" note, never in the main step instructions.
- Prefer imperative capability phrases ("search by pattern", "ask one question") over product nouns.

## Source

- `skills/plan/modules/research.md` (programmatic tool names removed) · `skills/plan/SKILL.md` (interaction described, not named)
- Commit `40b4808`