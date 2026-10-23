---
slug: atomic-config-write
type: pattern
domain: file-io
applicability:
  current_project: 4
  general: 6
tags: [config, filesystem, durability]
summary: Write config to a temp file in the same directory, then rename it over the target.
created_at: 2026-08-01T09:00:00Z
updated_at: 2026-08-01T09:00:00Z
source:
  type: commit
  reference: "3a7d9e1"
  extracted_at: 2026-08-01T09:00:00Z
---

# Atomic Config Write

## Problem
A crash during a config write leaves a truncated file that the next start cannot parse.

## Pattern
Write to a temp file beside the target, flush it, then rename it over the target.

## When to Apply
Any file another process reads while the tool may be killed mid-write.

## Example
scripts/postinstall.js writes the settings file this way.

## Related Learnings
(none yet)
