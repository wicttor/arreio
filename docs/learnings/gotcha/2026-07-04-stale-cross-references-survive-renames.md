---
title: "Stale cross-references survive renames unless systematically audited"
timestamp: "2026-07-04"
category: gotcha
domain: process
tags: [documentation, cross-references, maintenance, refactoring, intermediate]
severity: important
source: commit 36e656c
applicability:
  current_project: 9
  general: 9
related:
  - remove-dead-commented-docs-2026-07-02
---

# Stale Cross-References Survive Renames

## Problem

When a skill, command, or module is renamed, textual references to the old name persist in template docs, module descriptions, and inline comments. Manual find-and-replace is error-prone — some occurrences get missed. In the plan skill:

- `/pwrl-learnings` was renamed to `/learn` but the old reference remained in `final-plan.md`
- `pwrl-plan-design (S4)` was renamed to `design (Phase 3)` but the old reference remained in `research-findings.md`
- `Scoped Context Artifact` should have been `Research Findings Artifact` in `research.md`'s description

These stale references create broken mental links for readers and, in the case of command references, broken execution paths.

## Solution

After any rename, run a systematic audit:

```bash
# Find all references to old name
grep -rn "old-name" --include="*.md" .

# For command renames, also check code references
grep -rn "/old-command" --include="*.md" .

# For module renames, check descriptions and inline references
grep -rn "old-module-name" --include="*.md" .
```

Update every occurrence. Don't rely on memory — grep is exhaustive where humans are not.

## Prevention

- Document renaming as a checklist item in the skill authoring workflow
- Use consistent reference formats (e.g., always use backtick-wrapped paths) so grep patterns are predictable
- Consider adding a CI lint that flags references to deprecated/renamed commands

## Related Learnings

- [Remove dead commented-out documentation blocks](../workflow/remove-dead-commented-docs-2026-07-02.md) — stale references and dead comments are two sides of the same documentation maintenance debt
