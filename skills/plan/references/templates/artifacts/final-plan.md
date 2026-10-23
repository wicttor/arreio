---
title: Final Plan Artifact
type: template
version: 1.2
timestamp: "2026-10-23"
---

# Plan Templates

This document contains the planning template supported by the Plan skill. Render **only** the sections below, in this order; do not add sections of your own (no "contract review", "baseline", or "execution rules" sections). Doubts go to `Open Decisions`.

### Template

````markdown
---
plan-id: YYYY-MM-DD-NNN
type: plan
title: "[Plan title]"
status: complete
source: path/to/doc.mdx#section-anchor | prompt
tier: fast | standard | deep
tier_recommended: fast | standard | deep
complexity: TRIVIAL | LOW | MEDIUM | HIGH | VERY_HIGH
risk: Low | Medium | High | Critical
scope-id: YYYY-MM-DD-NNN-scope
research-id: YYYY-MM-DD-NNN-research
design-id: YYYY-MM-DD-NNN-design
interactionMode: detailed | smart | autopilot
created: YYYY-MM-DD
updated: YYYY-MM-DD
version: 1.0
---

# [Title]

## Overview

[1-2 sentence summary: what the plan delivers and why it matters]

**Out of scope:** [exclusions copied from the source, with their source references]

## Source Coverage

| Source item | Title | Units / Outcome |
| --- | --- | --- |
| [source ID] | [source title] | U1 |
| [source ID] | [source title] | U2, U3 |
| [source ID] | [source title] | Excluded — [reason quoted from the source] |

Justification: [only when the unit cap is exceeded or a source item is split across units]

## High-Level Technical Design

> **Note:** This is directional guidance for review, not an implementation specification to copy. The implementation phase will determine specific naming, abstractions, and code structure.

[Provide ONE of these:]

**Mermaid Diagram:**

```mermaid
sequenceDiagram
    participant A as Component A
    participant B as Service B
    A->>B: request
    B-->>A: response
```

**OR Pseudo-Code Sketch:**

```
on user_action:
  validate input
  if valid:
    process and store
    trigger event
  else:
    return error
```

**OR Data-Flow Map:**

```
User Input → Validation → Processing → Storage → Event Bus → Notification
```

## Implementation Units (Phased)

### Phase 1: Foundation

- U1. **[Unit Name]**
  - **Source:** [source item ID]
  - **Goal:** [What this unit accomplishes]
  - **Dependencies:** None
  - **Files:**
    - Create: `path/to/file`
    - Test: `path/to/test`
  - **Acceptance Criteria:**
    - [Single, verifiable criterion — each criterion later becomes exactly one task and one test]
  - **Test Scenarios:**
    - [Scenario]: [Input -> Expected Outcome]

- U2. **[Unit Name]**
  - **Source:** [source item ID]
  - **Goal:** [What this unit accomplishes]
  - **Dependencies:** U1
  - **Files:**
    - Create: `path/to/file`
  - **Acceptance Criteria:**
    - [Single, verifiable criterion]
  - **Test Scenarios:**
    - [Scenario]: [Input -> Expected Outcome]

### Phase 2: Integration

- U3. **[Unit Name]**
  - **Source:** [source item ID]
  - **Goal:** [What this unit accomplishes]
  - **Dependencies:** U1, U2
  - **Files:**
    - Modify: `path/to/file`
  - **Acceptance Criteria:**
    - [Single, verifiable criterion]
  - **Test Scenarios:**
    - [Scenario]: [Input -> Expected Outcome]

### Phase 3: Rollout (if applicable)

- U4. **[Unit Name]**
  - **Source:** [source item ID]
  - **Goal:** [What this unit accomplishes]
  - **Dependencies:** U3
  - **Files:**
    - Modify: `path/to/file`
  - **Acceptance Criteria:**
    - [Single, verifiable criterion]

## Alternative Approaches Considered

- **[Approach Name]**: [Description] → **Rejected because:** [Rationale for not choosing this approach]
- (Only real alternatives; if the source fixes the approach, say so in one line)

## Risk Analysis & Mitigation

| Risk                        | Impact | Mitigation                                    |
| --------------------------- | ------ | --------------------------------------------- |
| [Specific risk description] | High   | [Concrete step to prevent or recover from it] |
| [Another risk]              | Medium | [Mitigation strategy]                         |

## Operational / Rollout Notes

[Include if applicable; otherwise one line: `Not applicable — <reason>`]

- Feature flags: `feature.new_system` controls activation
- Monitoring: Add metrics for [key operations]
- Data migration: [Steps to migrate existing data]
- Rollback plan: [How to safely revert if issues arise]
- Performance baseline: [Expected throughput, latency targets]

## Open Decisions

- **OD1:** [question the source does not settle] — Recommended: [default and why] — Affects: U3
- (`None.` when empty)

## Related Learnings

- **[Learning Title]** — `docs/learn/XXX.md` — [1-line applicability note]
- (List relevant entries from `docs/learn/index.md`; if none apply, state "No relevant learnings found")

## Learning Gaps

- [Any gap identified during planning that should be documented after implementation via `/learn`]
````

### Example

```markdown
---
plan-id: 2026-05-01-001
type: plan
title: "Migrate Session Storage from In-Memory to Redis"
status: complete
source: prompt
tier: deep
tier_recommended: deep
complexity: HIGH
risk: High
scope-id: 2026-05-01-001-scope
research-id: 2026-05-01-001-research
design-id: 2026-05-01-001-design
interactionMode: smart
created: 2026-05-01
updated: 2026-05-01
version: 1.0
---

# Migrate Session Storage from In-Memory to Redis

## Overview

Move session storage to Redis so sessions survive restarts and scale horizontally.

**Out of scope:** changing the session cookie format.

## Source Coverage

| Source item | Title | Units / Outcome |
| --- | --- | --- |
| SC1 | Sessions are stored in Redis behind a store interface | U1 |
| SC2 | Middleware loads and validates sessions from Redis | U2 |

## High-Level Technical Design

**Session Lifecycle:**

1. Request arrives with session cookie (JWT)
2. Middleware validates JWT signature and expiration
3. Extract session ID, fetch from Redis
4. Attach session object to request context

## Implementation Units (Phased)

### Phase 1: Foundation

- U1. **Redis Client and Session Store Interface**
  - **Source:** SC1
  - **Goal:** Create Redis client wrapper and session storage interface
  - **Dependencies:** None
  - **Files:**
    - Create: `src/lib/redis-client.ts`
    - Test: `src/lib/redis-client.test.ts`
  - **Acceptance Criteria:**
    - `SessionStore` interface with `get`/`save`/`delete` backs a Redis client that connects from `REDIS_URL` and retries on failure
  - **Test Scenarios:**
    - Store/retrieve session, TTL expiration, connection errors

### Phase 2: Integration

- U2. **Session Middleware Refactor**
  - **Source:** SC2
  - **Goal:** Integrate Redis session store into middleware
  - **Dependencies:** U1
  - **Files:**
    - Modify: `src/middleware/session.ts`
    - Test: `src/middleware/session.test.ts`
  - **Acceptance Criteria:**
    - Middleware loads a valid JWT-backed session from Redis and rejects invalid/expired sessions
  - **Test Scenarios:**
    - Valid JWT loading, invalid JWT rejection, store errors

## Alternative Approaches Considered

- **PostgreSQL**: Rejected — slower latency for session reads on critical path
- **Stateless JWT-Only**: Rejected — cannot revoke sessions, increases cookie size

## Risk Analysis & Mitigation

| Risk                    | Impact | Mitigation                                     |
| ----------------------- | ------ | ---------------------------------------------- |
| Redis outage            | High   | HA mode (sentinel/cluster), monitoring, alerts |
| Performance degradation | Medium | Benchmark latency <2ms p99, connection pooling |

## Operational / Rollout Notes

- Feature flags: `feature.redis_sessions_dual_write`, `feature.redis_sessions_only`
- Monitoring: Redis latency and error-rate metrics on the session path
- Data migration: Not applicable — sessions expire naturally
- Rollback plan: Flip `feature.redis_sessions_only` off to return to dual-write
- Performance baseline: p99 session read < 2 ms

## Open Decisions

- **OD1:** Session TTL is not specified — Recommended: keep the current 24 h TTL — Affects: U1

## Related Learnings

No relevant learnings found.

## Learning Gaps

- Document session architecture decisions and Redis failover patterns
```

---

## Template Usage Rules

### Required Sections

Which sections a plan includes is **tier-driven**, not fixed. See [plan-tier-selection.md](../../plan-tier-selection.md) and the Generate phase ([generate.md](../../../modules/generate.md)) for the Fast/Standard/Deep section matrix. `Source Coverage` and `Open Decisions` are required in every tier. Do not render a section the tier marks optional and empty.

### Source Coverage Rules

- `source:` in the frontmatter names the source of truth (`path#anchor`) or `prompt`.
- Every unit has a `Source:` field; every source item is covered by a unit or excluded with a reason.
- Unit count ≤ 1.5 × covered source items unless `Justification:` explains it. See [plan-coverage-rules.md](../../plan-coverage-rules.md).
- The plan must pass `scripts/check-plan.py` before it is registered in the index.

### File Path Requirements

- All file paths in plans must be **repository-relative** (e.g., `src/main.js`, `docs/plans/YYYY-MM-DD-NNN-name.md`)
- Never use absolute paths (e.g., `/home/user/project/src/main.js`)
- Use backtick inline code formatting for file paths: `` `path/to/file` ``
- Paths are exact. Never write "as needed", "if required", or "etc."

### Learnings Embedding Rules

- Every plan **must** include a `## Related Learnings` section
- Scan `docs/learn/index.md` for relevant entries
- Include file path and a 1-line applicability rationale per learning
- If no relevant learnings exist, state: "No relevant learnings found"
- Add a `## Learning Gaps` section for areas where knowledge is missing but needed
- Learning gaps should include a follow-up action to document via `/learn`

### Naming Convention

- Plan files: `docs/plans/YYYY-MM-DD-NNN-<kebab-case-name>.md`
- U-ID format: `U1`, `U2`, ... in ascending document order; letter suffixes are reserved for the Tasks phase
- Frontmatter required fields: see the Final Plan frontmatter in the template above and [error-handling.md](../../error-handling.md) — `plan-id`, `type`, `title`, `status`, `source`, `tier`, `tier_recommended`, `complexity`, `risk`, `scope-id`, `research-id`, `design-id`, `interactionMode`, `created`, `updated`, `version`
