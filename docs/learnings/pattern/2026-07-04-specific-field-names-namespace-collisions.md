---
slug: specific-field-names-namespace-collisions
type: pattern
domain: skill-design
priority: important
applicability:
  current_project: 9
  general: 7
tags: [naming, schema-design, frontmatter, intermediate, consistency]
created_at: "2026-07-04T00:00:00Z"
updated_at: "2026-07-04T00:00:00Z"
source:
  type: commit
  reference: d626cd9
  extracted_at: "2026-07-04T00:00:00Z"
confidence: high
---

# Use Specific Field Names to Avoid Namespace Collisions

## Problem

When an artifact references multiple related artifacts via cross-phase IDs, a generic field name like `id` becomes ambiguous. The plan artifact contains its own `id` alongside `scope-id`, `research-id`, and `design-id` — all different identifiers in the same namespace. Using `id` for the plan's own identifier creates confusion about which ID is which, especially when templates and validation rules reference these fields.

## Solution

Use a disambiguated field name (`plan-id` instead of `id`) that makes the field's purpose immediately clear:

```yaml
# Before (ambiguous)
id: 2026-07-04-001

# After (self-documenting)
plan-id: 2026-07-04-001
```

This follows the existing pattern of the cross-phase IDs themselves (`scope-id`, `research-id`, `design-id`) — they all use descriptive prefixes. The plan's own identifier should follow the same convention.

## Prevention

- When designing an artifact schema, list all identifiers the artifact carries (its own + cross-references)
- If there are 2+ identifiers, give each a specific, descriptive name
- Prefer compound names (`plan-id`, `task-ref`) over bare `id` when multiple IDs coexist in the same frontmatter block

## Related Learnings

- [Cross-phase ID chaining for pipeline traceability](cross-phase-id-chaining-2026-07-04.md) — establishes the `-id` suffix convention for all cross-phase IDs
