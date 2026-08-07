---
title: "Extract repeated doc blocks into a shared reference to deduplicate"
timestamp: "2026-08-07"
category: workflow
domain: process
tags: [dry, deduplication, references, context-window, maintainability]
severity: recommended
source: commit 40b4808
applicability:
  current_project: 9
  general: 8
related:
  - strip-redundant-frontmatter-orchestrator-2026-07-04
  - template-example-removal-2026-07-04
  - remove-dead-commented-docs-2026-07-02
---

# Extract Repeated Doc Blocks Into a Shared Reference to Deduplicate

## Problem

The same multi-line block was duplicated verbatim across 4–5 module files:

- The daily-counter ID algorithm appeared 4× (scope/research/design/generate), ~8 lines each.
- The Step 0 verification intro and the Present-and-Confirm trichotomy appeared 5× (one per phase).

Each duplication bloats the context window and is a drift risk: fix the algorithm in one place and the other three go stale. Removing content (the `strip-*` / `template-example-removal` learnings) reduces bloat only for things you delete — it cannot consolidate things you must keep.

## Solution

For content that must be kept AND repeats across files, extract it to one shared reference and link:

- Created `skills/plan/references/id-generation.md` holding the daily-counter algorithm (once). The 4 phases link it ("Assign an id per id-generation.md") instead of inlining it.
- Step 0 / Confirm behavior live once in `error-handling.md` / `interaction-mode-propagation.md`; phases keep only their phase-specific Smart pause triggers (1–3 lines) and link the rest.

Net result: the shared source-of-truth is edited once; phases stay slim. The repository can keep ability without paying the duplication cost in every consumer.

## Application

- Trigger: a block appears 3+ times across files with no per-site variation. Extract.
- Keep the per-site variation at the call site (e.g., phase-specific pause triggers) and move the invariant to the reference.
- Link with relative paths so refactors survive; the reference is the single source, consumers cite it.

## Related Learnings

- `strip-redundant-frontmatter-orchestrator` / `template-example-removal` / `remove-dead-commented-docs` — removing bloat; this learning is the complement: when you cannot delete it, consolidate it.

## Source

- `skills/plan/references/id-generation.md` (new); `skills/plan/modules/*.md` (inlined blocks replaced with links)
- Commit `40b4808`