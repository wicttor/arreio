---
plan-id: 2026-09-01-001-fix-end-session-gaps
type: plan
title: Fix end-session Skill Gaps
status: complete
tier: shallow
tier_recommended: shallow
complexity: low
risk: low
scope-id: 2026-09-01-001-scope
research-id: 2026-09-01-001-research
design-id: 2026-09-01-001-design
interactionMode: smart
created: "2026-09-01"
updated: "2026-09-01"
version: "1.0"
---

# Plan: Fix end-session Skill Gaps

## Overview

Rewrite the `end-session` supporting skill to align with Arreio core skill conventions. Add `interactionMode` support, remove version-bump detection, introduce session artifact persistence, implement session-based agent attribution, and create a standard error-handling reference.

## High-Level Design

The skill becomes a three-phase workflow:
1. **Pre-flight Check** — verify working tree state, review changed files
2. **Prepare Commit** — craft subject/body, derive agent attribution from session changes
3. **Create Commit** — stage, commit, capture SHA
4. **Save Session Artifact** — write `docs/plans/.end-session/<session-id>.md`
5. **Post-Commit** — suggest `/learn maintain` for index sync

## Risk Analysis

| Risk | Level | Mitigation |
|------|-------|------------|
| Removing version-bump breaks existing expectations | Low | This is an undocumented edge feature; no other skill references it |
| Agent attribution heuristic may be unreliable | Low | Fallback to current agent name always available |
| New artifact I/O errors | Low | Covered by new error-handling reference with file-system recovery |

## Implementation Units

| Task | Description | Acceptance Criterion |
|------|-------------|---------------------|
| [TASK-01](docs/tasks/2026-09-01-001/TASK-01-add-interactionmode.md) | Add interactionMode support and frontmatter alignment | Frontmatter includes `disable-model-invocation`, `version`, `timestamp`; Interaction Method section offers Detailed/Smart/Autopilot |
| [TASK-02](docs/tasks/2026-09-01-001/TASK-02-remove-version-bump.md) | Remove version-bump detection and changelog logic | Phase 3.5 entirely removed; no CHANGELOG/version/tag references remain |
| [TASK-03](docs/tasks/2026-09-01-001/TASK-03-add-session-artifact.md) | Add session artifact persistence | New Phase 4 writes `docs/plans/.end-session/<session-id>.md` with commit details |
| [TASK-04](docs/tasks/2026-09-01-001/TASK-04-session-agent-attribution.md) | Implement session-based agent attribution | Attribution derived from changed files in session; fallback to current agent |
| [TASK-05](docs/tasks/2026-09-01-001/TASK-05-error-handling-tool-agnostic.md) | Add error-handling reference and tool-agnostic rewrite | `references/error-handling.md` exists; git CLI replaced with capability descriptions |
| [TASK-06](docs/tasks/2026-09-01-001/TASK-06-arreio-init-end-session.md) | Update arreio-init for end-session directories | `arreio-init` creates `docs/plans/.end-session/` and lists it in Success Criteria |

## References

- Scope: `docs/plans/.scope/2026-09-01-001-scope.md`
- Research: `docs/plans/.research/2026-09-01-001-research.md`
- Design: `docs/plans/.design/2026-09-01-001-design.md`
