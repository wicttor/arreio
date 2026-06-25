# Planning Tiers: Fast, Standard, Deep

This document describes the three planning tiers and when to use each.

---

## Overview

plan supports three tiers of planning detail:

| Tier         | Complexity | Risk   | Time      | Units | Use Case                                          |
| ------------ | ---------- | ------ | --------- | ----- | ------------------------------------------------- |
| **Fast**     | Low        | Low    | 5-15 min  | 1-3   | Small tweaks, bug fixes, well-understood tasks    |
| **Standard** | Medium     | Medium | 30-45 min | 4-8   | Most features, moderate complexity                |
| **Deep**     | High       | High   | 1-2 hours | 9+    | Architecture, security, migrations, cross-cutting |

---

## Fast Tier

**Best for:** Small, well-bounded tasks with clear scope and low risk.

### Characteristics

- **File Scope:** 1-3 files affected
- **Decision Complexity:** None or minimal
- **Risk Level:** LOW
- **Examples:** Bug fix, small feature, configuration tweak, documentation update
- **Time to Plan:** 5-15 minutes

### Template Sections

```markdown
# [Title] (Fast)

**Date:** [YYYY-MM-DD] | **Status:** active

## Goal

[One sentence description of the outcome]

## Implementation Units

- U1. **[Name]**
  - **Files:** `path/to/file`
  - **Approach:** [Brief technical note]
  - **Verification:** [How to confirm it works]

- U2. **[Name]**
  - **Files:** `path/to/file`
  - **Approach:** [Brief technical note]
  - **Verification:** [How to confirm it works]

## Related Learnings

[Relevant learnings; empty if none]

## Learning Gaps

[Identified gaps; empty if none]
```

### Decision Criteria

Choose **Fast** if:

- ✅ 1-3 files total
- ✅ No architectural decisions needed
- ✅ Approach is clear and straightforward
- ✅ No security, payment, or infrastructure concerns
- ✅ Can be completed in under 2 hours

---

## Standard Tier

**Best for:** Most software features with moderate complexity and moderate risk.

### Characteristics

- **File Scope:** 4-8 files affected
- **Decision Complexity:** 2-5 key technical decisions
- **Risk Level:** MEDIUM (1 high-risk area with 3+ local examples, OR multiple medium-risk areas)
- **Examples:** New feature, API integration, data migration, authentication flow
- **Time to Plan:** 30-45 minutes

### Template Sections

```markdown
# [Title] (Standard)

**Date:** [YYYY-MM-DD] | **Status:** active

## Overview

[2-3 sentence overview of the work]

## Key Technical Decisions

- **[Decision Topic]**: [Decision] — _Reason:_ [Rationale]
- **[Decision Topic]**: [Decision] — _Reason:_ [Rationale]

## Implementation Units

- U1. **[Name]**
  - **Scope:** [What this unit accomplishes]
  - **Dependencies:** [None or U1, U2]
  - **Files:** Create/modify/test
  - **Approach:** [Technical approach]
  - **Test Scenarios:** [How to verify]

- U2. **[Name]**
  - [Similar structure]

## System-Wide Impact

- API compatibility implications
- Database or state changes
- Performance considerations
- Security or compliance notes

## Related Learnings

[Relevant learnings from docs/learnings/INDEX.md]

## Learning Gaps

[Identified gaps for post-implementation documentation]
```

### Decision Criteria

Choose **Standard** if:

- ✅ 4-8 files affected OR 1-3 files with complexity
- ✅ 2-5 key technical decisions needed
- ✅ One high-risk area with sufficient local examples
- ✅ OR multiple medium-risk areas
- ✅ Can be completed in 2-6 hours

---

## Deep Tier

**Best for:** Complex, high-risk work requiring extensive design and alternatives analysis.

### Characteristics

- **File Scope:** 9+ files affected
- **Decision Complexity:** 5+ key technical decisions or significant architectural impact
- **Risk Level:** HIGH (2+ high-risk areas, security/payment/infrastructure, or major migration)
- **Examples:** Authentication system overhaul, payment integration, infrastructure migration, major refactor, security audit implementation
- **Time to Plan:** 1-2 hours

### Template Sections

```markdown
# [Title] (Deep)

**Date:** [YYYY-MM-DD] | **Status:** active

## Overview

[Comprehensive overview of work and impact]

## Key Technical Decisions

- **[Decision Topic]**: [Decision] — _Reason:_ [Rationale]
- **[Decision Topic]**: [Decision] — _Reason:_ [Rationale]
- [5+ decisions]

## High-Level Technical Design

> **Note:** This is directional guidance for review, not an implementation specification to copy.

[Mermaid diagram or pseudo-code or data-flow description]

## Alternative Approaches Considered

- **[Approach]**: [Description] → **Rejected because:** [Rationale]
- **[Approach]**: [Description] → **Rejected because:** [Rationale]

## Risk Analysis & Mitigation

| Risk               | Impact   | Mitigation         |
| ------------------ | -------- | ------------------ |
| [Risk description] | High/Med | [Mitigation steps] |

## System-Wide Impact

- API compatibility
- Database migrations
- Performance baselines
- Security implications
- Monitoring/alerting needs

## Operational / Rollout Notes

- Feature flags
- Monitoring setup
- Data migration steps
- Rollback plan
- Success metrics

## Implementation Units

- U1. **[Name]**
  - [Full unit specification]

- U2. **[Name]**
  - [Full unit specification]

- [9+ units]

## Related Learnings

[Relevant learnings]

## Learning Gaps

[Identified gaps]
```

### Decision Criteria

Choose **Deep** if:

- ✅ 9+ files affected
- ✅ 5+ key technical decisions OR architectural impact
- ✅ 2+ high-risk areas OR security/payment/infrastructure concerns
- ✅ Cross-service or cross-team impact
- ✅ Requires alternatives analysis or risk mitigation planning
- ✅ Estimated >6 hours of work

---

## Tier Selection Heuristic

### Step 1: Count Implementation Units

- **1-3 units:** Candidate for Fast
- **4-8 units:** Candidate for Standard
- **9+ units:** Must be Deep

### Step 2: Assess Risk Level

Scan task description for high-risk keywords:

| Area           | Keywords                                  | Risk Level |
| -------------- | ----------------------------------------- | ---------- |
| Security       | auth, jwt, oauth, session, encryption     | HIGH       |
| Payments       | payment, billing, stripe, checkout        | HIGH       |
| APIs           | api, rest, graphql, endpoint, integration | MEDIUM     |
| Migrations     | migration, upgrade, data, schema, version | MEDIUM     |
| Complex Logic  | algorithm, analysis, processing, compute  | MEDIUM     |
| Infrastructure | deploy, kubernetes, docker, scaling       | HIGH       |

### Step 3: Apply Heuristic

| Units | Risk               | Tier     |
| ----- | ------------------ | -------- |
| 1-3   | LOW                | Fast     |
| 1-3   | MEDIUM or HIGH     | Standard |
| 4-8   | any                | Standard |
| 9+    | any                | Deep     |
| any   | 2+ high-risk areas | Deep     |

---

## Overriding Tier Selection

Users can override the recommended tier in the plan generation phase:

- **Upgrade to Standard/Deep:** If more detail or confidence is needed
- **Downgrade to Fast:** If simpler than heuristic suggests (rare)

All overrides are documented in the plan for future reference.
