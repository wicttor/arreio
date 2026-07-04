# Learnings Index

All documented learnings from project work.

**Last updated:** 2026-07-04

## By Category

### Gotcha (3)

| File | Title | Domain | Applicability |
|------|-------|--------|---------------|
| [frontmatter-type-field-casing-drift-2026-07-04.md](gotcha/2026-07-04-frontmatter-type-field-casing-drift.md) | Frontmatter `type` field casing drifts across documents in same ecosystem | process | DIRECT |
| [inconsistent-status-terminology-artifact-schemas-2026-07-04.md](gotcha/2026-07-04-inconsistent-status-terminology-artifact-schemas.md) | Inconsistent status terminology across artifact schemas causes confusion | process | DIRECT |
| [stale-cross-references-survive-renames-2026-07-04.md](gotcha/2026-07-04-stale-cross-references-survive-renames.md) | Stale cross-references survive renames unless systematically audited | process | DIRECT |

### Pattern (11)

| File | Title | Domain | Applicability |
|------|-------|--------|---------------|
| [interaction-mode-propagation-2026-07-02.md](pattern/interaction-mode-propagation-2026-07-02.md) | Interaction mode propagation for multi-phase skill pipelines | skill-design | DIRECT |
| [daily-counter-artifact-naming-2026-07-02.md](pattern/daily-counter-artifact-naming-2026-07-02.md) | Daily counter algorithm for unique artifact naming | artifact-naming | DIRECT |
| [user-input-artifact-template-2026-07-02.md](pattern/user-input-artifact-template-2026-07-02.md) | User Input Artifact template for pipeline entry validation | template-design | DIRECT |
| [learnings-gate-logic-2026-07-02.md](pattern/learnings-gate-logic-2026-07-02.md) | Learnings gate logic with keyword matching and relevance scoring | information-retrieval | DIRECT |
| [pipeline-phase-module-template-2026-07-04.md](pattern/pipeline-phase-module-template-2026-07-04.md) | Pipeline phase module template with verification, processing, and confirmation | skill-design | DIRECT |
| [quality-gates-pipeline-orchestration-2026-07-04.md](pattern/quality-gates-pipeline-orchestration-2026-07-04.md) | Quality gates between pipeline phases with schema validation and error recovery | skill-design | DIRECT |
| [cross-phase-id-chaining-2026-07-04.md](pattern/cross-phase-id-chaining-2026-07-04.md) | Cross-phase ID chaining for pipeline traceability | skill-design | DIRECT |
| [specific-field-names-namespace-collisions-2026-07-04.md](pattern/2026-07-04-specific-field-names-namespace-collisions.md) | Use specific field names to avoid namespace collisions with related artifact IDs | skill-design | DIRECT |
| [templates-self-documenting-front-matter-2026-07-04.md](pattern/2026-07-04-templates-self-documenting-front-matter.md) | Templates should include their own full front-matter as self-documentation | process | DIRECT |
| [error-handling-tables-enumerate-required-fields-2026-07-04.md](pattern/2026-07-04-error-handling-tables-enumerate-required-fields.md) | Error-handling reference tables should enumerate all required fields per artifact type | process | DIRECT |
| [artifact-timestamp-standardization-2026-07-04.md](pattern/2026-07-04-artifact-timestamp-standardization.md) | Add timestamp field to all pipeline artifact frontmatter for traceability | skill-design | DIRECT |

### Decision (4)

| File | Title | Domain | Applicability |
|------|-------|--------|---------------|
| [complexity-assessment-framework-2026-07-04.md](decision/complexity-assessment-framework-2026-07-04.md) | Five-dimension complexity assessment framework for implementation planning | planning | DIRECT |
| [plan-tier-selection-algorithm-2026-07-04.md](decision/plan-tier-selection-algorithm-2026-07-04.md) | Plan tier selection algorithm with complexity defaults, risk floors, and user preference | planning | DIRECT |
| [critical-risk-tier-security-payments-2026-07-04.md](decision/2026-07-04-critical-risk-tier-security-payments.md) | CRITICAL risk tier above HIGH for security/payments areas | planning | DIRECT |
| [per-plan-task-indexing-2026-07-04.md](decision/2026-07-04-per-plan-task-indexing.md) | Use per-plan task indexes co-located with plans instead of a single global index | task-management | DIRECT |

### Workflow (4)

| File | Title | Domain | Applicability |
|------|-------|--------|---------------|
| [remove-dead-commented-docs-2026-07-02.md](workflow/remove-dead-commented-docs-2026-07-02.md) | Remove dead commented-out documentation blocks | documentation | INFORMATIONAL |
| [strip-redundant-frontmatter-orchestrator-2026-07-04.md](workflow/2026-07-04-strip-redundant-frontmatter-orchestrator.md) | Strip redundant frontmatter from orchestrator skill files to reduce bloat | process | DIRECT |
| [task-slicing-heuristics-2026-07-04.md](workflow/task-slicing-heuristics-2026-07-04.md) | Task slicing heuristics for decomposing implementation units into executable tasks | task-management | DIRECT |
| [template-example-removal-2026-07-04.md](workflow/2026-07-04-template-example-removal.md) | Remove verbose examples from artifact templates to prevent drift | documentation | DIRECT |

## By Domain

- **artifact-naming:** [daily-counter-artifact-naming-2026-07-02.md](pattern/daily-counter-artifact-naming-2026-07-02.md)
- **documentation:** [remove-dead-commented-docs-2026-07-02.md](workflow/remove-dead-commented-docs-2026-07-02.md), [template-example-removal-2026-07-04.md](workflow/2026-07-04-template-example-removal.md)
- **information-retrieval:** [learnings-gate-logic-2026-07-02.md](pattern/learnings-gate-logic-2026-07-02.md)
- **planning:** [complexity-assessment-framework-2026-07-04.md](decision/complexity-assessment-framework-2026-07-04.md), [plan-tier-selection-algorithm-2026-07-04.md](decision/plan-tier-selection-algorithm-2026-07-04.md), [critical-risk-tier-security-payments-2026-07-04.md](decision/2026-07-04-critical-risk-tier-security-payments.md)
- **skill-design:** [interaction-mode-propagation-2026-07-02.md](pattern/interaction-mode-propagation-2026-07-02.md), [pipeline-phase-module-template-2026-07-04.md](pattern/pipeline-phase-module-template-2026-07-04.md), [quality-gates-pipeline-orchestration-2026-07-04.md](pattern/quality-gates-pipeline-orchestration-2026-07-04.md), [cross-phase-id-chaining-2026-07-04.md](pattern/cross-phase-id-chaining-2026-07-04.md), [specific-field-names-namespace-collisions-2026-07-04.md](pattern/2026-07-04-specific-field-names-namespace-collisions.md), [artifact-timestamp-standardization-2026-07-04.md](pattern/2026-07-04-artifact-timestamp-standardization.md)
- **task-management:** [task-slicing-heuristics-2026-07-04.md](workflow/task-slicing-heuristics-2026-07-04.md), [per-plan-task-indexing-2026-07-04.md](decision/2026-07-04-per-plan-task-indexing.md)
- **process:** [inconsistent-status-terminology-artifact-schemas-2026-07-04.md](gotcha/2026-07-04-inconsistent-status-terminology-artifact-schemas.md), [stale-cross-references-survive-renames-2026-07-04.md](gotcha/2026-07-04-stale-cross-references-survive-renames.md), [frontmatter-type-field-casing-drift-2026-07-04.md](gotcha/2026-07-04-frontmatter-type-field-casing-drift.md), [templates-self-documenting-front-matter-2026-07-04.md](pattern/2026-07-04-templates-self-documenting-front-matter.md), [error-handling-tables-enumerate-required-fields-2026-07-04.md](pattern/2026-07-04-error-handling-tables-enumerate-required-fields.md), [strip-redundant-frontmatter-orchestrator-2026-07-04.md](workflow/2026-07-04-strip-redundant-frontmatter-orchestrator.md)
- **template-design:** [user-input-artifact-template-2026-07-02.md](pattern/user-input-artifact-template-2026-07-02.md)
