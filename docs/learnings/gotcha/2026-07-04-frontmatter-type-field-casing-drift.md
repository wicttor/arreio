---
slug: frontmatter-type-field-casing-drift
type: gotcha
domain: process
priority: important
applicability:
  current_project: 9
  general: 7
tags: [documentation, consistency, frontmatter, skill-design, intermediate]
created_at: "2026-07-04T00:00:00Z"
updated_at: "2026-07-04T00:00:00Z"
source:
  type: commit
  reference: d626cd9
  extracted_at: "2026-07-04T00:00:00Z"
confidence: high
---

# Frontmatter `type` Field Casing Drifts Across Documents

## Problem

When a skill ecosystem contains multiple document categories (orchestrator SKILL.md, module docs, artifact templates), the `type` frontmatter field naturally drifts toward inconsistent casing over time. In the plan skill, modules used `type: Documentation` while templates used `type: Template` — both capitalized, non-standard values. This mirrors the same root cause as the `status: confirmed` vs `status: complete` inconsistency: different documents created at different times by different agents without a canonical reference.

Affected 11 files across `skills/plan/`: 5 modules + 6 template artifacts.

## Solution

1. **Pick a canonical format** — lowercase, category-appropriate values (`module`, `template`, `skill`, `artifact`, `reference`)
2. **Audit with grep**: search for all `type:` fields across the entire skill directory
3. **Replace** every non-conforming value with the canonical equivalent
4. **Document the convention** in the skill's primary reference (e.g., SKILL.md or a schema reference doc)

## Prevention

- Define the set of valid `type` values in a single reference document and reference it from every template
- Add a CI/lint check that flags unknown or non-canonical `type` values
- When creating a new document category, add its `type` value to the canonical list immediately

## Related Learnings

- [Inconsistent status terminology across artifact schemas](2026-07-04-inconsistent-status-terminology-artifact-schemas.md) — same root cause (field value drift), different field (`status` instead of `type`)
- [Templates should include their own full front-matter](../pattern/2026-07-04-templates-self-documenting-front-matter.md) — establishing frontmatter as a contract
