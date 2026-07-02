---
title: "Remove dead commented-out documentation blocks"
date: 2026-07-02
category: workflow
domain: documentation
tags: [maintenance, cleanup, markdown, skill-files]
severity: informational
source: commit 3943146
---

# Remove Dead Commented-Out Documentation Blocks

## Problem

Large HTML-commented sections in markdown skill files accumulate over time as documentation moves to dedicated reference files. These dead blocks make the file harder to navigate, add visual noise, and often become stale or contradictory to current docs.

## Solution

When a skill file has an HTML comment block (`<!-- ... -->`) that documents sections now living in separate reference docs, remove the dead comments entirely. Keep only active content and cross-references like `**See:** [references/error-handling.md](references/error-handling.md)`.

### When to Remove

- The commented content has a dedicated reference file elsewhere
- The commented content is outdated or contradicts current documentation
- The commented content is purely historical/transitional

### When to Keep

- The comment is an active TODO or FIXME
- The content is a temporary note for ongoing work
- The comment serves as inline documentation for active code

## Application

- Apply during refactoring sessions when skill files grow too large
- Run as part of periodic maintenance sweeps
- Ensure cross-references remain intact after removal

## Source

- `skills/plan/SKILL.md` — 22 lines of commented-out section removed
- Commit `3943146`
