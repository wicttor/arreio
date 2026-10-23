---
title: Interaction Mode Propagation
description: Reference for how `interactionMode` propagates through the Plan pipeline (Scope → Research → Design → Generate → Tasks). Set at Orchestrator; each phase reads and applies mode-specific behavior.
type: reference
version: 1.2
timestamp: "2026-10-23"
---

# Interaction Mode Propagation

Reference for how `interactionMode` propagates through the Plan pipeline (Scope → Research → Design → Generate → Tasks). Set at Orchestrator; each phase reads and applies mode-specific behavior.

## Modes

| Mode          | Behavior                                              | Use Case                             |
| ------------- | ----------------------------------------------------- | ------------------------------------ |
| **Detailed**  | Pause at each phase; show artifacts; require approval | Complex work, unfamiliar codebases   |
| **Smart**     | Auto-proceed; pause only on HIGH-risk flags           | Familiar codebases with guardrails   |
| **Autopilot** | Run all phases auto (except Tasks, which always asks) | Straightforward work, time-sensitive |

## Phase Behavior by Mode

| Phase        | Detailed                                         | Smart                                                                                                  | Autopilot                         |
| ------------ | ------------------------------------------------ | ------------------------------------------------------------------------------------------------------ | --------------------------------- |
| **Scope**    | Present artifact; ask Proceed/Edit/Abort         | Auto-proceed; pause if 3+ learning gaps, non-software domain, conflicting requirements, or the source of truth had to be asked | Auto-proceed (still asks if the source of truth is unclear) |
| **Research** | Show findings; ask Proceed/Edit/Abort           | Auto-proceed; pause if HIGH/CRITICAL risk with <3 patterns, or zero patterns found                    | Auto-proceed                      |
| **Design**   | Show units; ask Proceed/Edit/Abort              | Auto-proceed; pause if VERY_HIGH complexity, HIGH risk + <3 patterns, 3+ scope gaps, Novelty=3, unit count over the coverage cap, or Open Decisions blocking 3+ units | Auto-proceed; announces the coverage line |
| **Generate** | Show plan; ask Proceed/Edit/Skip/Abort          | Auto-proceed; pause if tier=Deep (not when forced by `--deep`), tier preference conflicts with risk floor, or CRITICAL risk          | Auto-proceed                      |
| **Tasks**    | Ask Create/Review/No (full file content shown)  | Ask Create/Review/No (summary shown)                                                                   | Ask Create/Review/No (always asks) |

**Smart mode pauses only on each phase's documented triggers above** (the canonical list lives in each module's confirmation step; this table is a summary).

## `--deep` Flag

`/plan --deep <task>` sets `force_deep: true` in the Orchestrator context. It is orthogonal to `interactionMode`: in every mode the Generate phase selects the Deep tier without asking about tier. It does not add pauses and removes the Smart-mode "tier is Deep" pause. See [plan-tier-selection.md](plan-tier-selection.md#deep-override---deep).

## Artifact Schema

All phase artifacts (Scope 1-4) include:

```yaml
type: scope | research | design | plan
scope-id: 2026-07-02-001-scope
interactionMode: detailed | smart | autopilot # Passed from previous phase
status: pending | complete | failed
```

## Implementation

**Each phase must:**

1. Read `interactionMode` from incoming artifact (or context for Scope)
2. Apply mode-specific behavior per table above
3. Include `interactionMode` in output artifact

**Phase 5 (Tasks):** Always ask user about task slicing, even in Autopilot mode.

## Example

**SMART mode on complex codebase task:**

- Scope detects 3 learning gaps → pauses (HIGH-risk)
- User approves → Research runs
- Research detects unfamiliar framework → pauses (HIGH-risk)
- User approves → Design runs
- Design complexity MEDIUM → auto-proceeds
- Generate renders → auto-proceeds
- Tasks asks user → user chooses yes

**Result:** Paused only for critical decisions; faster than Detailed with safety guardrails.

## Error Handling

| Scenario                    | Recovery                              |
| --------------------------- | ------------------------------------- |
| Mode missing                | Default to "smart"; log warning       |
| Invalid mode value          | Reject; re-prompt Orchestrator        |
| Artifact missing mode field | Assume "smart"; log warning; continue |
| Timeout/connection lost     | Pause; ask user to retry or abort     |

## Artifact Persistence

Phase artifacts (Scope, Research, Design) are **handoff data between phases**, not deliverables. The Scope and Design artifacts are also the audit trail for scope drift (what the plan was supposed to cover, and how that became units), so they are small and always kept. Whether each is written depends on the phase and `interactionMode`:

| Artifact | Detailed | Smart | Autopilot |
| -------- | -------- | ----- | --------- |
| **Scope** (`docs/plans/.scope/`) | Written, shown, then passed on | **Written**, then passed on | **Written**, then passed on |
| **Research** (`docs/plans/.research/`) | Written, shown, then passed on | **Not written**; held in context | **Not written**; held in context |
| **Design** (`docs/plans/.design/`) | Written, shown, then passed on | **Written**, then passed on | **Written**, then passed on |

**Always written, in every mode:** the Scope and Design artifacts, the final plan in `docs/plans/` (+ `docs/plans/index.md`), and any task files in `docs/tasks/<plan-id>/`.

**Rules:**

- The artifact schema, quality gates, cross-phase ID checks, and pause triggers are **unchanged** — only the disk write is skipped. Validate and pass the in-memory artifact exactly as you would the file.
- Never create `docs/plans/.research/` in `smart`/`autopilot`; no placeholder or empty files. `.scope/` and `.design/` are created on first use in every mode.
- **ID allocation without files:** Allocate the plan-id `YYYY-MM-DD-NNN` once at Scope by counting today's final plan files in `docs/plans/` (excluding hidden dirs); every phase id is `<plan-id>-<phase>` (e.g. `2026-09-02-001-scope`).
- If the user switches to `detailed` mid-run, write the Research artifact produced so far, then continue writing.
- **Edit & Retry** reuses the artifact's id and overwrites its file (Scope and Design in every mode, Research in `detailed`) or reuses the in-memory artifact (Research in `smart`/`autopilot`).
