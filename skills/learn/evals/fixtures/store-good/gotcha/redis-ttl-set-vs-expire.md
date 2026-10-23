---
slug: redis-ttl-set-vs-expire
type: gotcha
domain: data-storage
priority: important
applicability:
  current_project: 8
  general: 7
tags: [redis, ttl, session-store, caching]
summary: Pass the TTL on SET ... EX; a separate EXPIRE is lost when the key is overwritten.
created_at: 2026-07-10T00:00:00Z
updated_at: 2026-08-08T14:40:00Z
source:
  type: commit
  reference: "9f3c2ab"
  extracted_at: 2026-07-10T00:00:00Z
confidence: high
related: [ttl-must-propagate-to-redis-set]
also-seen-in: ["2026-07-10-001-review#2026-07-10-001-T02a:green"]
---

# Redis TTL Must Propagate to the SET Command

## Problem
The session-store TTL test failed after the green gate.

## Trap
Setting the TTL with a separate EXPIRE loses it the next time the key is overwritten by SET.

## Solution
Pass the TTL on SET with EX; do not issue a separate EXPIRE.

## Prevention
Assert in the acceptance test that the TTL is observable on the next read after an overwrite.

## Related Learnings
- ttl-must-propagate-to-redis-set: earlier wording of the same trap, superseded.

## Source
Commit 9f3c2ab, session store TTL test.
