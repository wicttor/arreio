---
title: Interaction Mode Propagation
description: Reference for how `interactionMode` propagates through the Review pipeline (Scope -> Prepare -> Analyze -> Report). Set at the Orchestrator; each phase reads and applies mode-specific behavior. Review has no execution mode — only interactionMode.
type: reference
version: 1.0
timestamp: "2026-08-08"
---

# Interaction Mode Propagation

Reference for how `interactionMode` propagates through the Review pipeline (`Scope → Prepare → Analyze → Report`). Set at the Orchestrator; each phase reads and applies mode-specific behavior.

> `interactionMode` governs **when to pause for the user**. Unlike the Work skill, **Review has no execution mode** — analysis is a single forward pass over the diffs, not a multi-task run, so there is no `executionMode` selector. Only `interactionMode` is carried through every artifact.

## Modes

| Mode          | Behavior                                              | Use Case                             |
| ------------- | ----------------------------------------------------- | ------------------------------------ |
| **Detailed**  | Pause at each phase; present artifacts; require approval | High-stakes or sensitive reviews, unfamiliar changes |
| **Smart**     | Auto-proceed; pause only on HIGH-severity findings (blocker/major) or detected scope creep | Familiar changes with guardrails |
| **Autopilot** | Run all phases auto (Report still presented)           | Routine reviews of well-understood changes |

## Phase Behavior by Mode

| Phase        | Detailed                                         | Smart                                                                                                       | Autopilot                         |
| ------------ | ------------------------------------------------ | ---------------------------------------------------------------------------------------------------------- | --------------------------------- |
| **Scope**    | Present review scope; ask Proceed/Edit/Abort      | Auto-proceed; pause if ad-hoc inferred boundary, ambiguous requirements, or preliminary scope-creep detected | Auto-proceed                      |
| **Prepare**  | Present review kit; ask Proceed/Edit/Abort        | Auto-proceed; pause if partial spec resolution, a no-coverage test gap, or no linter configured            | Auto-proceed                      |
| **Analyze**  | Present findings; ask Proceed/Edit/Abort          | Auto-proceed; pause if any `blocker`/`major` finding, scope-creep confirmed, or creep tally differs from Scope's preliminary count | Auto-proceed                      |
| **Report**   | Present review report; ask Finalize/Edit/Abort   | Auto-proceed; pause if `changes-requested`/`rejected`, or `learnings-to-capture` non-empty                   | Auto-proceed (strips to Smart triggers) |

**Smart mode pauses only on each phase's documented triggers above** (the canonical list lives in each module's confirmation step; this table is a summary).

## Artifact Schema

All phase artifacts include `interactionMode`:

```yaml
interactionMode: detailed | smart | autopilot # Passed from previous phase
status: pending | complete | failed
```

## Implementation

**Each phase must:**

1. Read `interactionMode` from the incoming artifact (or context, for Scope).
2. Apply mode-specific behavior per the table above.
3. Include `interactionMode` in the output artifact.

## Example

**SMART mode on a change-set review:**

- Scope parses a `<base>..<head>` diff (not inferred) → auto-proceeds
- Prepare resolves a present spec fully, finds test coverage and a configured linter → auto-proceeds
- Analyze finds one `major` quality finding and no scope-creep → pauses (major finding trigger)
- User reviews the major finding, confirms it's real (chooses Proceed to Report)
- Report derives `changes-requested`, learnings-to-capture non-empty → pauses (changes-requested + learnings triggers)
- User finalizes; the Report is saved and the registry row appended

**Result:** Paused only for the genuine major finding and the change-requested finalization; faster than Detailed with safety guardrails.

## No Execution Mode (contrast with Work)

Review deliberately has **no** `executionMode`:

- Work's `executionMode` (`inline`/`serial`/`parallel`) governs how multiple independent **tasks** run — Review has no multi-task concept; analysis is a single forward pass over the change boundary.
- The orchestrator's quality gate #2 for Review cross-checks **only** `interactionMode` (not `interactionMode` + `executionMode` as in Work).
- A `blocker`/`major` finding is the Review analog of Work's HIGH-risk flag: it triggers pause behavior, but via `interactionMode`'s Smart triggers, not a separate mode.

## Error Handling

| Scenario                    | Recovery                              |
| --------------------------- | ------------------------------------- |
| Mode missing                | Default to "smart"; log warning       |
| Invalid mode value          | Reject; re-prompt Orchestrator        |
| Artifact missing mode field | Assume "smart"; log warning; continue |
| User selects "Abort"        | Stop immediately; inform Orchestrator |
| Timeout/connection lost     | Pause; ask user to retry or abort     |

## Artifact Persistence

Phase artifacts (Scope, Prepare, Analyze) are **handoff data between phases**, not deliverables. Whether they are written to disk depends on `interactionMode`:

| Mode          | Phase artifacts (`docs/review/.scope/`, `.prepare/`, `.analyze/`)          | Phase handoff                                  |
| ------------- | ---------------------------------------- | ---------------------------------------------- |
| **Detailed**  | Written to the hidden directories (audit trail; creating the directory on first use) | Artifact is written, shown, then passed on     |
| **Smart**     | **Not written**                          | Artifact is held in context and passed in-memory to the next phase |
| **Autopilot** | **Not written**                          | Artifact is held in context and passed in-memory to the next phase |

**Always written, in every mode:** the Review Report in `docs/review/.report/<report-id>.md` and its row in `docs/review/index.md` (a cross-skill handoff read by `/learn`).

**Rules:**

- The artifact schema, quality gates, cross-phase ID checks, and pause triggers are **unchanged** — only the disk write is skipped. Validate and pass the in-memory artifact exactly as you would the file.
- Never create the hidden directories in `smart`/`autopilot`; no placeholder or empty files.
- **ID allocation without files:** Allocate `review-id` NNN by counting today's files in `docs/review/.report/` (+1); `scope-id`/`prepare-id`/`analyze-id` reuse that NNN as in-memory labels.
- If the user switches to `detailed` mid-run, write the artifacts produced so far, then continue writing.
- Because nothing is on disk, **Edit & Retry** reuses the in-memory artifact and its id (no file to overwrite).
