---
title: "Error-handling reference tables should enumerate all required fields per artifact type"
timestamp: "2026-07-04"
category: pattern
domain: process
tags: [documentation, error-handling, validation, schema-design, intermediate]
severity: important
source: commit 36e656c
applicability:
  current_project: 10
  general: 7
related:
  - quality-gates-pipeline-orchestration-2026-07-04
---

# Error-Handling Reference Tables Should Enumerate All Required Fields

## Problem

The error-handling reference table in the plan skill listed required fields per artifact type, but it was incomplete:

- The **research** row was missing `scope-id` (needed for cross-phase validation)
- The **design** row was missing `research-id` (needed for traceability)
- The **plan** row listed only 4 fields when the actual template requires 14+

Phase checkpoint validators that rely on this table to determine what to validate would silently skip missing fields, allowing malformed artifacts to pass quality gates.

## Solution

Maintain a single source-of-truth table where every artifact type's row is an exact mirror of the template's front-matter fields:

| Artifact Type | Required Fields |
| ------------- | --------------- |
| `user-input`  | `type`, `timestamp`, `source`, `status`, Task Description, Intended Behavior |
| `scope`       | `type`, `scope-id`, `domain`, `status`, `interactionMode`, Problem, Intended Behavior, Success Criteria |
| `research`    | `research-id`, `scope-id`, `status`, `interactionMode`, Patterns Found, High-Risk Detection, Tech Stack |
| `design`      | `design-id`, `scope-id`, `research-id`, `status`, `interactionMode`, Approach, Implementation Units, Complexity |
| `plan`        | `plan-id`, `type`, `title`, `status`, `tier`, `tier_recommended`, `complexity`, `risk`, `scope-id`, `research-id`, `design-id`, `interactionMode`, `created`, `updated`, `version`, High-Level Design, Implementation Units, Risk Analysis |

## Prevention

- When a template gains a new field, update the error-handling reference table **in the same commit**
- Add a CI validation that cross-checks template front-matter fields against the reference table
- Document the table as the canonical source for validators — not the templates themselves

## Related Learnings

- [Quality gates between pipeline phases](../pattern/quality-gates-pipeline-orchestration-2026-07-04.md) — defines the schema validation gate that depends on this table
