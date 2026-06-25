---
type: skill
title: Plan
name: plan
description: Create structured implementation plans with three tiers, Fast, Standard, Deep. Orchestrates scope, research, design, and generation phases.
group: plan
argument-hint: "[task description, requirements doc, or goal to plan]"
tags:
  - planning
  - architecture
  - structured-output
author: "@wicttor"
---

# Plan

Create durable implementation plans that can be handed off for execution. Orchestrates a deterministic pipeline of phases: scope → research → design → generate.

## Purpose

Plans capture decisions, structure, and approach before execution. They enable:

- Clear scope and success criteria
- Identified risks and dependencies
- Concrete implementation units with acceptance criteria
- Knowledge reuse through related learnings
- Confidence that work won't go off the rails

## Phase Summary

Each phase is orchestrated sequentially: the Plan Skill calls the corresponding phase, receives the output artifact, validates it with a quality gate, and passes it to the next phase.

**Phase 1: Scope** ([plan-scope](./phases/plan-scope.md)) — Gather context, validate domain, set interaction mode. Output: Scoped context artifact.

**Phase 2: Research** ([plan-research](./phases/plan-research.md)) — Discover tech stack, local patterns, and risk areas. Output: Research findings artifact.

**Phase 3: Design** ([plan-design](./phases/plan-design.md)) — Decompose into units, map dependencies, assess complexity. Output: Design artifact with unit decomposition.

**Phase 4: Generate** ([plan-generate](./phases/plan-generate.md)) — Select tier, render plan, embed learnings, save to `docs/plans/`. Output: Final plan document.

**Quality Gates:** Run `/phase-checkpoint plan N [artifact-path]` to validate each phase. If the checkpoint command fails or cannot be invoked, halt the pipeline and report: _"Quality gate for Phase [N] could not execute. Verify phase-checkpoint is installed. Do not proceed to Phase [N+1] until the gate passes."_ See _phase-checkpoint/SKILL.md_ for validation rules.

### Interaction Mode Propagation

Interaction mode (detailed or automode) is set in Phase 1 and read at the start of each subsequent phase. Determines whether confirmation steps execute or are skipped. If the interaction mode field is absent or unrecognized in the scope artifact, the phase halts and reports: _"Interaction mode not found or invalid in scope artifact. Re-run Phase 1 or manually set to 'detailed' or 'automode' before retrying."_

## Planning Tiers

| Tier         | Best For                           | Files | Risk | Time      |
| ------------ | ---------------------------------- | ----- | ---- | --------- |
| **FAST**     | Bug fixes, small tweaks            | 1-3   | LOW  | 5-15 min  |
| **STANDARD** | Most features                      | 4-8   | MED  | 30-45 min |
| **DEEP**     | Architecture, security, migrations | 9+    | HIGH | 1-2 hours |

**Tier Selection Tie-Breaking Rule:** When File Count and Risk criteria conflict, **Risk takes precedence**. If still ambiguous, select the higher tier. In detailed mode, ask the user to confirm the selected tier before proceeding to Phase 2. In automode, log the selection rationale in the scope artifact and continue without prompting.

**Inline Tier Criteria Summary:**

- **FAST:** 1-3 files, LOW risk, no architectural trade-offs
- **STANDARD:** 4-8 files, MEDIUM risk, 2-5 key technical decisions
- **DEEP:** 9+ files, HIGH risk, complex architecture/security/migrations/cross-cutting concerns

**Full tier templates and decision matrices:** See _references/planning-tiers.md_. If unavailable, use the inline summary above and ask the user to confirm tier selection.

## Core Principles

Ordered by priority (highest to lowest); trade-offs are resolved by this order.

1. **Deterministic Pipeline** — Phases always execute in sequence (scope → research → design → generate) with no agent switching and no fallback paths. Error conditions halt the pipeline; they do not divert it. Halts are recorded by appending a HALT entry to the current phase artifact, then reported to the user in chat. Recovery is initiated via `/phase-checkpoint plan N [artifact-path]`.

2. **Transparent Artifacts** — Each phase produces an explicit, named output artifact validated via quality gate before passing to the next phase.

3. **Right-Size** — Planning depth matches task complexity. Small tasks → short plans; complex work → more structure. Avoid over-planning trivial changes.

4. **Be Concrete** — Use specific files, components, and dependencies. Reference repository-relative paths only. Avoid generic or vague scoping. For FAST tier tasks, enumerate only the files directly involved; exhaustive path enumeration is not required and would violate Right-Size (principle 3).

5. **Focus on Decisions** — Capture approach, structure, risks, and sequencing. Do not simulate implementation or write pseudo-code during planning.

6. **Separate Planning from Execution** — Plan the work, then execute it. Planning and execution are distinct phases with different success criteria.

## Error Handling & Recovery

**Philosophy:** Fail explicitly, not silently. Errors halt the pipeline and are always reported to the user with recovery suggestions.

**Coverage:** Each phase has predefined error handlers (see _references/phases.yaml_ for error categories and _references/error-handling.md_ for recovery workflows).

Error categories by phase:

- Phase 1 (Scope): Empty input, non-software domain, missing context
- Phase 2 (Research): Codebase analysis failures, high-risk areas requiring human input
- Phase 3 (Design): Circular dependencies, unit count exceeding tier limits
- Phase 4 (Generate): Filename collisions, file write failures, missing output directory

**Cross-Phase Errors:**

- **Missing Reference Files:** If required reference files (_references/planning-tiers.md_, _references/phases.yaml_, _references/error-handling.md_) are unavailable, apply file-specific fallback. For _planning-tiers.md_, use inline tier criteria (see Planning Tiers section). For other files, halt and report: _"Required reference file [filename] not found. Planning cannot proceed without it."_
- **Phase Availability:** If a referenced phase skill file cannot be located or invoked, halt and report: _"Phase [N] skill file not found. Please verify the skill is installed and retry."_ Do not attempt to infer or substitute phase behavior inline.
- **Missing Output Directory:** If `docs/plans/` does not exist at Phase 4, attempt to create it. If creation fails, halt and report: _"Output directory docs/plans/ could not be created. Please create it manually and retry."_
- **Invalid Interaction Mode:** If the interaction mode field is absent or unrecognized in the scope artifact at the start of any phase, halt and report: _"Interaction mode not found or invalid in scope artifact. Re-run Phase 1 or manually set to 'detailed' or 'automode' before retrying."_

## Key Outputs

Each plan includes outputs based on tier:

**FAST Tier:**

- Problem & Scope — Clear problem frame and intended behavior
- Success Criteria — 1-3 specific conditions for completion
- Implementation Units — 1-3 named U-IDs with files, approach, and verification steps

**STANDARD Tier (includes all FAST + these):**

- Related Learnings — Linked learning files with applicability notes
- Risk Analysis — Identified risks and mitigation strategies
- Alternatives — Alternative approaches considered and rationale for final choice

**DEEP Tier (includes all STANDARD + these):**

- Learning Gaps — Areas requiring post-implementation documentation
- Rollout Notes — Sequencing, rollback procedures, monitoring
- Security & Infrastructure Considerations — If applicable

## Interaction Method

**Tool Priority (use first available in this order):**

1. `vscode/askQuestions` (VS Code native)
2. `ask_user_question` (platform-agnostic fallback)
3. `ask_user` (last resort)

If none are available, pause and notify user with specific question.

**Guidelines:**

- Ask one question at a time
- Use multiple-choice questions when possible
- If input is empty, ask: "What would you like to plan? Describe the task or project."
- Provide clear recovery suggestions when errors occur

## Phase Invocation Contract

The Plan orchestrator calls four phase skills in sequence. Each phase is invoked with specific inputs and returns a named artifact.

**Calling Convention:**
Each phase skill is invoked as a subagent or skill call with these parameters:

- **Input:** Prior artifact path (if resuming) + raw user input + interaction_mode setting
- **Return:** Named markdown artifact saved to `docs/plans/` with standardized format

**Phase-Specific Contract:**

1. **Phase 1 (Scope):** Input: raw user input; Output: `docs/plans/.scope.md` (problem frame, success criteria, interaction_mode field)
2. **Phase 2 (Research):** Input: prior scope artifact path + interaction_mode; Output: `docs/plans/.research.md` (tech stack, patterns, risks, learnings)
3. **Phase 3 (Design):** Input: prior research artifact path + interaction_mode; Output: `docs/plans/.design.md` (units, dependencies, complexity, risk)
4. **Phase 4 (Generate):** Input: prior design artifact path + interaction_mode; Output: final plan document to `docs/plans/[name]-[tier].md`

If a phase returns an artifact that cannot be parsed or validated, the pipeline halts and reports the parsing error. Do not attempt to infer missing fields.

## Pipeline Resume

If invoked with an existing artifact path (e.g., `phase 3 docs/plans/.design.md`), the orchestrator may resume from that phase instead of restarting from Phase 1. To resume:

1. Validate the provided artifact by running `/phase-checkpoint plan [N-1] [artifact-path]` (checkpoint the prior phase to confirm it passed)
2. If validation passes, skip all prior phases and start execution at Phase N
3. If validation fails, report which prior phase must be re-run and do not proceed
4. Resume mode is supported only in detailed interaction mode; automode requires full pipeline re-execution

## Architecture

```
plan orchestrator
├── 1. Call plan-scope with user input → get scope artifact
├── 2. Call plan-research with scope artifact → get research artifact
├── 3. Call plan-design with research artifact → get design artifact
└── 4. Call plan-generate with design artifact → save plan file
```

**Optional resume path:** If invoked with an existing phase artifact, skip prior phases and resume from Phase N (see Pipeline Resume).

**Benefits:**

- ✅ Simpler to understand (single code path)
- ✅ Easier to test (no branching logic)
- ✅ More maintainable (phases independently testable)
- ✅ More composable (phases reusable in other workflows)
- ✅ Better error handling (explicit at each phase)

## Frequently Asked Questions

(To be populated with real FAQs as usage patterns emerge)
