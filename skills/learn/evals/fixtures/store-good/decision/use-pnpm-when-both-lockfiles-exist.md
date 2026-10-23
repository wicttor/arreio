---
slug: use-pnpm-when-both-lockfiles-exist
type: decision
domain: tooling
priority: normal
applicability:
  current_project: 8
  general: 6
tags: [package-management, npm, pnpm, lockfiles]
summary: Prefer the lockfile named by package.json's packageManager field when both lockfiles exist.
created_at: 2026-08-08T14:30:00Z
updated_at: 2026-08-08T14:30:00Z
source:
  type: user
  reference: "Use pnpm over npm when both lockfiles exist"
  extracted_at: 2026-08-08T14:30:00Z
confidence: medium
---

# Use pnpm When Both Lockfiles Exist

## Problem
A repository with both package-lock.json and pnpm-lock.yaml gives no signal which one to install from.

## Solution
Install with the package manager named in package.json's packageManager field; ask when it is absent.

## Decision Rationale
The field is the one place the project states its choice, so every phase resolves to the same manager.

## Application
skills/work/modules/prepare.md detects the runner; skills/review/modules/prepare.md reuses the result.

## Related Learnings
(none yet)
