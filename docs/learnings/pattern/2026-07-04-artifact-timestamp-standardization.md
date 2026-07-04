---
slug: artifact-timestamp-standardization
type: pattern
domain: skill-design
priority: recommended
applicability:
  current_project: 9
  general: 8
tags: [metadata, frontmatter, traceability, pipeline-artifacts, audit]
created_at: "2026-07-04T00:00:00Z"
updated_at: "2026-07-04T00:00:00Z"
source:
  type: commit
  reference: aa21a87
  extracted_at: "2026-07-04T00:00:00Z"
confidence: high
---

# Add Timestamp Field to All Pipeline Artifact Frontmatter

## Problem

Pipeline artifacts (design, research findings, task files) carried rich frontmatter with IDs, status, and cross-references, but lacked a creation timestamp. Without a timestamp:

- Sorting artifacts by recency requires filesystem timestamps (fragile across environments)
- Correlating artifacts with events (other commits, deployments) is imprecise
- Rebuilding a timeline of pipeline execution requires git log inspection

## Solution

Add a `timestamp` field to every artifact frontmatter, using ISO-8601 format:

```yaml
timestamp: 2026-07-04T14:30:00Z
```

This was added to three artifact templates:

| Artifact | Template File |
|----------|--------------|
| Design | `skills/plan/references/templates/artifacts/design.md` |
| Research Findings | `skills/plan/references/templates/artifacts/research-findings.md` |
| Task | `skills/plan/references/templates/artifacts/task.md` |

The final plan template already had `created` and `updated` fields; the timestamp field complements these by recording the exact moment the artifact was produced.

## Prevention

- When designing a new pipeline artifact schema, include `timestamp` as a required frontmatter field from the start
- Use ISO-8601 with UTC (`Z`) to avoid timezone ambiguity
- The generating phase should set the timestamp at artifact creation time, not leave it as a template placeholder

## Application

- Pipeline phases set `timestamp` when emitting artifacts
- Tooling can sort artifacts chronologically without filesystem metadata
- Timestamps enable `git log`-style artifact histories

## Related Learnings

- [Cross-phase ID chaining for pipeline traceability](../pattern/cross-phase-id-chaining-2026-07-04.md) — timestamp complements ID chaining for full traceability
