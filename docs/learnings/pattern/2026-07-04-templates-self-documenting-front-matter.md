---
title: "Templates should include their own full front-matter as self-documentation"
timestamp: "2026-07-04"
category: pattern
domain: process
tags: [documentation, templates, front-matter, schema-design, intermediate]
severity: important
source: commit 36e656c
applicability:
  current_project: 10
  general: 8
related:
  - user-input-artifact-template-2026-07-02
---

# Templates Should Include Their Own Full Front-Matter

## Problem

Artifact templates that only show a `# [Title]` heading with no YAML front-matter force downstream authors to look up required fields in separate reference docs — or worse, omit them entirely. The `final-plan.md` template was missing all 14 identifying fields (`id`, `type`, `status`, `tier`, `complexity`, `risk`, all cross-phase IDs, `interactionMode`, timestamps, and `version`). Similarly, `research-findings.md` was missing `type`, `scope-id`, and `interactionMode`.

This creates a documentation gap where the template and the validation rules disagree on what constitutes a valid artifact.

## Solution

Every artifact template should include its complete YAML front-matter as a copy-paste-ready scaffold:

```yaml
---
id: YYYY-MM-DD-NNN
type: plan
title: "[Plan title]"
status: complete
tier: fast | standard | deep
tier_recommended: fast | standard | deep
complexity: TRIVIAL | LOW | MEDIUM | HIGH | VERY_HIGH
risk: Low | Medium | High
scope-id: YYYY-MM-DD-NNN-scope
research-id: YYYY-MM-DD-NNN-research
design-id: YYYY-MM-DD-NNN-design
interactionMode: detailed | smart | autopilot
created: YYYY-MM-DD
updated: YYYY-MM-DD
version: 1.0
---
```

The template serves double duty: documentation of required fields AND a working scaffold.

## Prevention

- When adding a new field to an artifact schema, update the template in the same commit
- Use the template's front-matter as the canonical field list for validation reference tables
- Include both a blank template and a filled-in example in each template doc

## Related Learnings

- [User Input Artifact template for pipeline entry validation](../pattern/user-input-artifact-template-2026-07-02.md) — establishes the YAML frontmatter contract pattern for pipeline entry
