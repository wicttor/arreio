---
slug: strip-redundant-frontmatter-orchestrator
type: workflow
domain: process
priority: nice_to_know
applicability:
  current_project: 8
  general: 6
tags: [documentation, maintenance, frontmatter, cleanup, beginner]
created_at: "2026-07-04T00:00:00Z"
updated_at: "2026-07-04T00:00:00Z"
source:
  type: commit
  reference: d626cd9
  extracted_at: "2026-07-04T00:00:00Z"
confidence: high
---

# Strip Redundant Frontmatter from Orchestrator Skill Files

## Problem

Orchestrator skill files (SKILL.md) accumulate YAML frontmatter fields over time that duplicate information already available elsewhere. The plan skill's SKILL.md had `title`, `type`, `version`, `timestamp`, and `user-invocable` — all either derivable from the skill registry, file metadata, or conveyed by the `name` and `description` fields. This bloat increases maintenance burden: every field must be kept in sync manually.

## Solution

Periodically audit SKILL.md frontmatter and remove fields that are:

- **Redundant with the skill registry** (e.g., `title` duplicates `name`, `user-invocable` is a registry property)
- **Derivable from file metadata** (e.g., `timestamp` is in git history)
- **Not consumed by tooling** (e.g., `version` if no version-aware tooling reads it)

Keep only fields with runtime significance: `name`, `description`, `argument-hint`, `disable-model-invocation`.

## Prevention

- When adding a new frontmatter field to a SKILL.md, ask: "Is this consumed by any tool, or is it purely documentation?"
- If purely documentation, put it in a `## Metadata` section in the body instead of YAML frontmatter
- Run a periodic cleanup pass across all skill SKILL.md files

## Related Learnings

- [Templates should include their own full front-matter](../pattern/2026-07-04-templates-self-documenting-front-matter.md) — inverse relationship: templates *should* carry full frontmatter, orchestrator SKILL.md should *not* carry redundant fields
