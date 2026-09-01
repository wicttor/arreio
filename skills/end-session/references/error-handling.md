---
title: Error Handling & Recovery
description: Reference for all end-session phases (Pre-flight, Confirm Completion, Prepare Commit, Create Commit, Save Artifact, Post-Commit). Defines Step 0 verification, error categories, recovery workflow, retry limits, and cross-phase consistency checks.
type: reference
version: 1.0
timestamp: "2026-09-01"
---

# Error Handling & Recovery

This file documents the error handling and recovery strategies shared across all end-session phases. Each phase begins with a **Step 0: Verification** that validates the incoming context; this reference defines the validation rules, recovery actions, and termination conditions.

## Core Principle

**Fail explicitly, never silently.** When the working tree state is unreadable, attribution is ambiguous, or a write fails, the phase must surface a clear error with a recovery suggestion rather than guessing. Silent failures produce misattributed commits and missing session records — exactly what this skill exists to prevent.

Recognized deliberate non-blocks (explicit notes, not silent skips):

- A **missing `docs/plans/.end-session/` directory** is self-healed in Pre-flight (created on first use) — this is a documented recovery, not an error.
- A **missing `## Session Ends` section** in `docs/plans/index.md` is self-healed by creating the section before appending.
- A **missing `docs/plans/index.md` entirely** is self-healed by creating a minimal index with the `## Session Ends` section before appending.

## Step 0: Context Verification

Every phase receives the context object (interactionMode, changed files, commit message draft, session-id). Step 0 validates it before any work begins.

### Verification Procedure

```
1. Confirm interactionMode is present and valid (default to "smart" if missing)
2. Confirm the change list is present and non-empty (Pre-flight output)
3. Confirm the user confirmed session completion (Phase 2 output)
4. Confirm the commit message draft has a subject and body (Phase 3 output)
5. Confirm the commit SHA is present before artifact save (Phase 4 output)
```

## Error Categories

### Category 1: Missing Changes

| Trigger                                        | Recovery Action                                                        | Terminate? |
| ---------------------------------------------- | ---------------------------------------------------------------------- | ---------- |
| Working tree state cannot be inspected         | Log error; ask the user to verify the repository is accessible; retry once | Yes, after 1 retry |
| Working tree is clean (no changes)             | Inform the user; exit gracefully (nothing to commit is not an error state) | Yes (graceful) |
| All candidate files excluded by the user       | Inform the user; exit or continue with artifact-less summary            | Yes (graceful) |

### Category 2: Invalid Input

| Trigger                                              | Recovery Action                                                     | Terminate? |
| ---------------------------------------------------- | ------------------------------------------------------------------- | ---------- |
| User declines session completion (Phase 2)           | List open todos / incomplete work; exit without committing          | Yes (graceful) |
| Commit subject missing or exceeds 50 chars           | Re-draft the subject with the user; never commit with a placeholder | No |
| Commit body empty where context warrants explanation | Ask the user for a one-line rationale; continue                     | No |
| User aborts during message approval                  | Stop immediately; report abort reason; no staging performed         | Yes |

### Category 3: Ambiguous Attribution

| Trigger                                                          | Recovery Action                                                                        | Terminate? |
| ---------------------------------------------------------------- | -------------------------------------------------------------------------------------- | ---------- |
| Changed files were last modified by multiple different agents    | List detected agents; ask the user which to attribute (or accept current-agent fallback) | No |
| Pre-session changes carry no detectable attribution in history   | Fall back to the current agent; log a one-line note in the session artifact            | No |
| Attribution trailers are contradictory across files              | Ask the user; record the resolution in the session artifact                            | No |

### Category 4: File System Errors

| Trigger                                              | Recovery Action                                                       | Terminate? |
| ---------------------------------------------------- | --------------------------------------------------------------------- | ---------- |
| `docs/plans/.end-session/` does not exist            | Create it (`mkdir -p`); treat counter as 0; start from 001            | No |
| `docs/plans/index.md` missing                        | Create a minimal index with `## Session Ends`; append the entry       | No |
| Counter directory exists but no files match the date | Start counter at 001                                                  | No |
| File write permission denied (artifact or index)     | Log error; ask the user to check permissions; retry once              | Yes, after 1 retry |
| Session artifact write fails after the commit exists | Log error; provide the commit SHA + message so the user can save manually; suggest re-running Phase 5 | No |

### Category 5: Git / Commit Errors

| Trigger                                              | Recovery Action                                                        | Terminate? |
| ---------------------------------------------------- | ---------------------------------------------------------------------- | ---------- |
| Staging fails (locked index, permission)             | Log error; retry once; then ask the user to resolve and retry manually | Yes, after 1 retry |
| Commit creation fails (identity not configured, hook rejection) | Log the failure reason; do not fabricate a SHA; suggest fixes (identity config, hook bypass decision) | Yes |
| Commit succeeds but SHA cannot be captured           | Ask the user to confirm the commit landed; proceed to artifact save with user-supplied SHA | No |

### Category 6: Interaction Mode Errors

| Trigger                                  | Recovery Action                                            | Terminate? |
| ---------------------------------------- | ---------------------------------------------------------- | ---------- |
| Mode missing from context                | Default to "smart"; log warning; continue                  | No |
| Mode value is not in the enum            | Reject; re-prompt the user to set a valid mode             | Yes |
| User selects "Abort" during confirmation | Stop immediately; report abort with reason                 | Yes |
| User does not respond (timeout)          | Pause; ask the user to retry or abort                      | No |

## Recovery Workflow

When a verification failure is detected in Step 0, apply this workflow:

```
1. Identify the error category (1-6) from the tables above
2. Look up the specific trigger to find the recovery action
3. Execute the recovery action:
   - If recovery is "ask user": ask one question with clear options (2-4 concrete choices)
   - If recovery is "default and continue": apply default, log warning, proceed
4. If terminate = Yes: stop and inform the user with:
   - Error category and trigger
   - Recovery action attempted
   - Reason for termination
5. If terminate = No: after recovery, continue to the next step of the phase
```

## Retry Limits

- **Maximum retries per error:** 1
- **Maximum total retries per phase:** 2
- After exhausting retries, terminate with a clear error explaining what failed and suggesting the user resolve the underlying issue and re-run `/end-session`.

## Error Reporting Format

When reporting an error to the user, use this format:

```yaml
error:
  phase: pre-flight | confirm-completion | prepare-commit | create-commit | save-artifact | post-commit
  step: 0 | 1 | 2 | ...
  category: 1 | 2 | 3 | 4 | 5 | 6
  trigger: "[specific trigger description]"
  recovery_attempted: "[action taken]"
  outcome: recovered | terminated
  suggestion: "[next step for the user]"
```

## Cross-Phase Consistency Checks

| Check                                                                 | Action on Failure                                      |
| --------------------------------------------------------------------- | ------------------------------------------------------ |
| `interactionMode` is identical across all phases                      | Log warning; use the earliest non-default value        |
| Change list in Phase 3/4 matches the Pre-flight list (no silent additions) | Reject; return to Pre-flight                     |
| Session artifact `commit-sha` matches the commit reported in Phase 4  | Reject the artifact; re-run Phase 5 with the correct SHA |
| Session artifact `agent` matches the attribution confirmed in Phase 3 | Reject the artifact; re-run Phase 5                    |
| `session-id` date matches today's date                                | Reject; re-allocate the session-id                     |

## Notes

- All errors and warnings should be logged with a timestamp for debugging.
- Graceful exits (clean tree, user-declined completion) are **not** failures — they are valid outcomes of Phases 1–2 and must be reported as such.
- The skill is not resume-safe by design: a failed session end is re-run from Phase 1 with a fresh look at the working tree. The only idempotent write is the session artifact (overwrite on the same `session-id`, never duplicate).
- This reference is shared by all six phases; phase-specific handling is documented inline in the SKILL.md workflow.
