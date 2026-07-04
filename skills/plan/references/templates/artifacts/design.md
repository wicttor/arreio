---
title: Design Artifact
description: Template for the Design Artifact produced by the Design phase. Captures the chosen approach, implementation units, complexity assessment, and alternatives considered for downstream generation.
type: Template
version: 1.0
timestamp: "2026-07-03"
---

# Design Artifact

The product of the **Design** phase (Phase 3) is a structured design object that the **Generate** phase consumes to render the final plan. It captures the chosen approach, the implementation unit decomposition, the complexity assessment, and the alternatives considered (and why they were rejected).

When the **Design** phase completes, it produces a design block (as markdown) with this schema:

## Schema

```yaml
type: design
design-id: YYYY-MM-DD-NNN-design
scope-id: YYYY-MM-DD-NNN-scope        # Inherited from Scope phase; traceability link
research-id: YYYY-MM-DD-NNN-research  # Inherited from Research phase
status: confirmed
interactionMode: detailed | smart | autopilot
complexity: TRIVIAL | LOW | MEDIUM | HIGH | VERY_HIGH
tier_recommendation: fast | standard | deep

# Design

## Approach
[1-3 sentence summary of the chosen approach and why it fits the scoped context and research findings]

## High-Level Technical Design
[ONE of: Mermaid diagram, pseudo-code sketch, or data-flow map — directional guidance, not implementation specification]

## Implementation Units (Phased)

### Phase 1: Foundation
- U1. **[Unit Name]**
  - Goal: [What this unit accomplishes]
  - Dependencies: None
  - Files:
    - Create: `path/to/file`
    - Test: `path/to/test`
  - Test Scenarios:
    - [Scenario]: [Input -> Expected Outcome]

- U2. **[Unit Name]**
  - Goal: [What this unit accomplishes]
  - Dependencies: U1
  - Files:
    - Create: `path/to/file`
  - Test Scenarios:
    - [Scenario]: [Input -> Expected Outcome]

### Phase 2: Integration
- U3. **[Unit Name]**
  - Goal: [What this unit accomplishes]
  - Dependencies: U1, U2
  - Files:
    - Modify: `path/to/file`
  - Test Scenarios:
    - [Scenario]: [Input -> Expected Outcome]

### Phase 3: Rollout (if applicable)
- U4. **[Unit Name]**
  - Goal: [What this unit accomplishes]
  - Dependencies: U3
  - Files:
    - Modify: `path/to/file`

## Complexity Assessment
- scope_breadth: 0-3
- integration_surface: 0-3
- risk_level: LOW | MEDIUM | HIGH | CRITICAL   # Inherited from Research phase
- novelty: 0-3
- data_migration: 0-3
- total: [sum]
- complexity: TRIVIAL | LOW | MEDIUM | HIGH | VERY_HIGH

## Alternative Approaches Considered
- **[Approach Name]**: [Description] → **Rejected because:** [Rationale]
- **[Approach Name]**: [Description] → **Rejected because:** [Rationale]

## Related Learnings
- docs/learnings/XXX.md — [1-line applicability note]
- (List from docs/learnings/index.md; empty list if none)

## Learning Gaps
- [Gap name] — [Follow-up action via /learn]
```

Also save the design artifact to `docs/plans/.design/<design-id>.md` for future reference or reuse. The `interactionMode` and `complexity` values flow into the Generate artifact for tier selection.

## Validation Rules

- **Approach:** Required. Must reference the scoped context and research findings (not invented in isolation).
- **High-Level Technical Design:** Required. Must be ONE of: Mermaid diagram, pseudo-code sketch, or data-flow map. Directional only — not an implementation specification.
- **Implementation Units:** Required. At least one unit (U1). Each unit must have a Goal, Dependencies, and Files. Test Scenarios required for units in phases 1–2; optional for rollout-only units.
- **Complexity Assessment:** Required. All five dimensions scored 0–3; `total` must equal the sum; `complexity` must match the threshold mapping.
- **Alternative Approaches:** Required for MEDIUM+ complexity; at least 1 alternative. For HIGH/VERY_HIGH, at least 2 alternatives. For TRIVIAL/LOW, may be empty.
- **Related Learnings:** Required (may be empty list). Must reference `docs/learnings/index.md`.
- **Learning Gaps:** Required (may be empty list). Inherited from Scope phase; updated if design reveals new gaps.
- **scope-id / research-id:** Required. Must match the upstream artifacts for cross-phase consistency (see [error-handling.md](../../error-handling.md)).

## Example

```yaml
type: design
design-id: 2026-07-03-001-design
scope-id: 2026-07-03-001-scope
research-id: 2026-07-03-001-research
status: confirmed
interactionMode: smart
complexity: HIGH
tier_recommendation: standard

# Design

## Approach
Introduce a Redis-backed session store behind the existing session interface, then swap the in-memory implementation for the Redis one in middleware. This reuses the existing session abstraction (HIGH-confidence pattern) and isolates the new dependency to a single client module.

## High-Level Technical Design

**Session Lifecycle:**

1. Request arrives with session cookie (JWT)
2. Middleware validates JWT signature and expiration
3. Extract session ID, fetch from Redis
4. Attach session object to request context

## Implementation Units (Phased)

### Phase 1: Foundation
- U1. **Redis Client and Session Store Interface**
  - Goal: Create Redis client wrapper and session storage interface
  - Dependencies: None
  - Files:
    - Create: `src/lib/redis-client.ts`
    - Create: `src/lib/session-store.ts`
    - Test: `src/lib/redis-client.test.ts`
  - Test Scenarios:
    - Store/retrieve session: store {id, data} -> retrieve returns same
    - TTL expiration: store with 1s TTL -> after 1s, get returns null
    - Connection error: drop connection -> get throws with retryable error

- U2. **Redis Session Store Implementation**
  - Goal: Implement the session-store interface against Redis
  - Dependencies: U1
  - Files:
    - Create: `src/lib/redis-session-store.ts`
    - Test: `src/lib/redis-session-store.test.ts`
  - Test Scenarios:
    - Save session: save(session) -> get(id) returns session
    - Delete session: delete(id) -> get(id) returns null

### Phase 2: Integration
- U3. **Session Middleware Refactor**
  - Goal: Integrate Redis session store into existing middleware
  - Dependencies: U1, U2
  - Files:
    - Modify: `src/middleware/session.ts`
    - Test: `src/middleware/session.test.ts`
  - Test Scenarios:
    - Valid JWT loads session: valid token -> request.session populated
    - Invalid JWT rejected: expired token -> 401 response

### Phase 3: Rollout
- U4. **Dual-Write and Cutover**
  - Goal: Ship behind feature flags with dual-write validation
  - Dependencies: U3
  - Files:
    - Modify: `src/middleware/session.ts`
    - Modify: `src/config/flags.ts`

## Complexity Assessment
- scope_breadth: 2
- integration_surface: 2
- risk_level: HIGH
- novelty: 1
- data_migration: 1
- total: 8
- complexity: HIGH

## Alternative Approaches Considered
- **PostgreSQL**: Rejected — slower latency for session reads on critical path
- **Stateless JWT-Only**: Rejected — cannot revoke sessions, increases cookie size
- **Sticky Sessions**: Rejected — limits horizontal scaling, poor failover

## Related Learnings
- docs/learnings/pattern/daily-counter-artifact-naming-2026-07-02.md — ID generation for this design artifact
- docs/learnings/pattern/interaction-mode-propagation-2026-07-02.md — Smart mode pause logic for HIGH complexity

## Learning Gaps
- Redis failover patterns in production — document post-implementation via /learn
```

## Usage in Workflow

1. **Design Phase** produces this artifact from the Scoped Context and Research Findings
2. **Design Phase Step 0** validates the incoming Scoped Context and Research Findings (see [error-handling.md](../../error-handling.md))
3. **Generate Phase** reads the `complexity` and `tier_recommendation` fields to select the plan tier (see [plan-tier-selection.md](../../plan-tier-selection.md))
4. **Generate Phase** renders the final plan from the units and alternatives captured here

## Missing Field Recovery

If the Design Artifact is incomplete at validation, use this recovery workflow:

| Field                       | Validation                       | Recovery                                                                                           |
| --------------------------- | -------------------------------- | -------------------------------------------------------------------------------------------------- |
| Approach                    | Non-empty, references context    | Re-run Design phase; ask user to clarify approach                                                  |
| High-Level Technical Design | One of three formats present     | Ask user to choose diagram, pseudo-code, or data-flow map                                          |
| Implementation Units        | At least U1 with Goal/Files      | Re-run Design decomposition step                                                                   |
| Complexity Assessment       | All 5 dimensions + total + level | Recompute from units; see [design-complexity-assessment.md](../../design-complexity-assessment.md) |
| Alternative Approaches      | Count matches complexity tier    | Ask user for additional alternatives if below threshold                                            |
| scope-id / research-id      | Matches upstream artifacts       | Reject; ask Orchestrator to re-run from the mismatched phase                                       |

**Note:** If the Approach or Implementation Units cannot be produced, abort planning and ask the user to revisit the research phase — the scoped context may be insufficient for design.
