---
type: skill
title: plan
description: Create structured implementation plans with three tiers, Fast, Standard, Deep. Orchestrates scope, research, design, and generation phases.
group: plan
argument-hint: "[task description, requirements doc, or goal to plan]"
tags:
  - planning
  - architecture
  - structured-output
aliases: torquem-plan
author: "@wicttor"
zed:
  disable-model-invocation: false
  when-to-use: User requests a plan for implementing a feature, refactoring work, or solving a technical problem
cursor:
  user-invocable: true
  instructions-context: Use pwrl-plan-scope, pwrl-plan-research, pwrl-plan-design, and pwrl-plan-generate substeps
claude:
  instructions-context: Gathers context, performs research, creates technical design, then generates final plan
  output-format: structured markdown with YAML frontmatter
pi:
  disable-model-invocation: false
  metadata:
    workflow-type: multi-phase-pipeline
    primary-tools:
      - file-read
      - file-write
      - grep
copilot:
  user-invocable: true
  instructions-context: Create implementation plan with tiered approaches (Fast/Standard/Deep)
  output-format: markdown with clear sections and action items
  integration-hints:
    - github-issues
    - project-management
    - pull-requests
---
