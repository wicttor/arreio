---
title: "Inconsistent status terminology across artifact schemas causes confusion"
timestamp: "2026-07-04"
category: gotcha
domain: process
tags: [documentation, consistency, schemas, pipeline-architecture, intermediate]
severity: important
source: commit 36e656c
applicability:
  current_project: 10
  general: 7
related:
  - quality-gates-pipeline-orchestration-2026-07-04
---

# Inconsistent Status Terminology Across Artifact Schemas

## Problem

When a pipeline has multiple artifact types (scope, research, design, plan), the `status` field must use a single canonical value across all templates, module docs, and reference tables. In the plan skill pipeline, `status` was `confirmed` in some files and `complete` in others — quality gate check #3 looked for `confirmed`, but downstream templates used `complete`, creating a mismatch that could cause valid artifacts to fail schema validation.

This affected 5 files across the plan skill: SKILL.md, design.md template, interaction-mode-propagation.md, scoped-context.md template, and generate.md module.

## Solution

Pick one canonical value (`complete`) and audit every occurrence:

1. **Grep for all `status:` field values** across the entire skill directory
2. **Replace** every `confirmed` with `complete` in templates, module docs, and reference files
3. **Verify** quality gates and validators reference the same canonical value
4. **Add to error-handling table** so the validator's accepted values list stays in sync

## Prevention

- Define status values in a single constants/reference doc and import/reference them everywhere
- Add a CI lint rule that checks for `status: confirmed` as a disallowed pattern
- When adding a new artifact type, check the validator's accepted values match the template

## Related Learnings

- [Quality gates between pipeline phases](../pattern/quality-gates-pipeline-orchestration-2026-07-04.md) — defines the status check gate that was affected by this inconsistency
