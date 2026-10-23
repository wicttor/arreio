---
slug: ttl-must-propagate-to-redis-set
type: gotcha
domain: data-storage
priority: important
applicability:
  current_project: 8
  general: 7
tags: [redis, ttl, session-store, caching]
summary: Pass the TTL on SET ... EX.
created_at: 2026-07-12T00:00:00Z
updated_at: 2026-08-08T14:40:00Z
source:
  type: commit
  reference: "1ee04e2"
  extracted_at: 2026-07-12T00:00:00Z
confidence: medium
superseded-by: redis-ttl-set-vs-expire
status: obsolete
---

# TTL Must Propagate to Redis SET

## Problem
The TTL was lost after an overwrite.

## Trap
A separate EXPIRE is not part of SET.

## Solution
Use SET ... EX.

## Prevention
Assert the TTL after an overwrite.

## Related Learnings
- redis-ttl-set-vs-expire: canonical entry.
