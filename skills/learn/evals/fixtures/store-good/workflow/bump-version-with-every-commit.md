---
slug: bump-version-with-every-commit
type: workflow
domain: release
priority: normal
applicability:
  current_project: 9
  general: 3
tags: [versioning, changelog]
summary: Every commit bumps package.json and adds CHANGELOG notes.
created_at: 2026-10-23T08:00:00Z
updated_at: 2026-10-23T08:00:00Z
source:
  type: user
  reference: "always bump package.json and add CHANGELOG notes with every commit"
  extracted_at: 2026-10-23T08:00:00Z
confidence: high
---

# Bump Version With Every Commit

## Convention
Each commit changes the version in package.json and adds a CHANGELOG entry.

## Why
Installed copies are identified by version, so an unbumped commit is indistinguishable from the previous one.

## How
Edit package.json, add the notes under CHANGELOG.md [Unreleased] or a new version heading, then commit.

## Related Learnings
(none yet)
