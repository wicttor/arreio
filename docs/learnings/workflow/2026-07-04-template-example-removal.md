---
slug: template-example-removal-prevent-drift
type: workflow
domain: documentation
priority: recommended
applicability:
  current_project: 8
  general: 9
tags: [templates, documentation-maintenance, schema-first, drift-prevention]
created_at: "2026-07-04T00:00:00Z"
updated_at: "2026-07-04T00:00:00Z"
source:
  type: commit
  reference: aa21a87
  extracted_at: "2026-07-04T00:00:00Z"
confidence: high
---

# Remove Verbose Examples from Artifact Templates to Prevent Drift

## Problem

The design artifact template (`skills/plan/references/templates/artifacts/design.md`) contained a 93-line full example with mock data (redis-backed session store migration). As the design schema evolved — adding fields, changing status values, refining format — this example became outdated. Developers reading the template would see a conflicting example that didn't match the current schema, creating confusion about which version was authoritative.

## Solution

Remove the embedded example from the template file entirely. Keep only:

1. The frontmatter schema with field descriptions
2. Validation rules and constraints
3. Cross-references to other artifacts

The schema itself is the source of truth. Examples, when needed, should live in separate files or be auto-generated from valid artifacts, never hand-maintained inside the template.

**Result:** Design template dropped from ~165 lines to ~72 lines. The removed 93-line example was the largest source of drift in the template.

## When to Apply

- When an artifact template contains a full worked example that must stay in sync with schema changes
- When the example is long enough (>30 lines) that keeping it current is a maintenance burden
- When alternative documentation (separate example files, live-generated examples) is available

## When Not to Apply

- Short inline snippets (≤5 lines) that illustrate a single field — these are fine
- Templates where the example _is_ the primary documentation (no separate schema doc)

## Related Learnings

- [Templates should include their own full front-matter as self-documentation](../pattern/2026-07-04-templates-self-documenting-front-matter.md) — the schema stays; examples go
- [Strip redundant frontmatter from orchestrator skill files to reduce bloat](../workflow/2026-07-04-strip-redundant-frontmatter-orchestrator.md) — same principle applied to SKILL.md files
