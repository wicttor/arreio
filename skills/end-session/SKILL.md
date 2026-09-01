---
name: end-session
description: "Create a single clear commit at session end capturing state and next steps. Saves a session artifact to docs/plans/.end-session/ and attributes the commit to the agent that made the session's file changes."
argument-hint: "[Optional: reason for ending session or switching tasks]"
disable-model-invocation: true
version: 1.1.0
timestamp: "2026-09-01"
---

# End Session

Create a single well-documented commit when a work session ends, capturing state and providing context for future sessions.

## Purpose

Session-end commits serve as checkpoints in AI-assisted development:

- **Context preservation**: Future sessions can understand what was done and why
- **Audit trail**: Clear attribution via `[AGENT: ...]` trailer derived from session file changes
- **Continuity**: Next steps documented for seamless session transitions
- **Review quality**: Well-documented commits improve code review efficiency

## Usage

```text
/end-session                           # End current session
/end-session "switching to bugfix"     # End with context note
```

## Interaction Method

- Ask the user one structured question at a time (2–4 concrete options) using the agent's interactive question capability; never hardcode a specific tool name.
- If the optional context note is empty, no prompt is needed — the session reason is optional.

Before starting the workflow, ask the user to choose an interaction mode:

- **Detailed** — Confirm at each phase transition; inspect the commit message and session artifact before each write; maximum control.
- **Autopilot** — All phases run automatically; only the final outcome (commit SHA + artifact path) is reported.
- **Smart** — Phases run automatically; pause only on ambiguous attribution, empty commit message, or user-declined completion.

Store in the context object:

```yaml
interactionMode: detailed | smart | autopilot
```

**Propagation:** `interactionMode` is read at the start of each phase and determines whether confirmation steps execute (detailed = confirm every phase; autopilot = run all; smart = pause only on the triggers listed per phase).

## Workflow

### Phase 1: Pre-flight Check

1. Check working tree state:
   - Inspect the working tree for modified, added, and deleted files using the platform's change-detection capability
   - If no changes exist, inform the user and exit
2. Review changed files:
   - Display the list of changed files
   - Ask the user which files to include in the commit
   - Confirm excluded files are intentionally left out
3. Confirm the session artifact directory exists (`docs/plans/.end-session/`); if missing, create it (self-healing — allows this skill to run even if `arreio-init` wasn't explicitly run)

**Mode behavior:** Detailed = present the change list and wait for approval; Smart/Autopilot = proceed with all detected changes unless the user has excluded files.

### Phase 2: Confirm Completion

1. Ask the user to confirm the session is complete:
   - Present a clear yes/no question
   - If the user declines, check for open todos or incomplete work
2. If not complete:
   - List any open todos from the task tracker
   - Summarize incomplete work
   - Exit without committing
   - Suggest completing remaining work first

**Mode behavior:** This phase always asks, in every mode — ending a session is a user decision, never inferred.

### Phase 3: Prepare Commit Message

1. Craft commit subject line:
   - Use imperative mood: "Add feature" not "Added feature"
   - Keep to 50 characters or less
   - No trailing period
   - Clear and descriptive
2. Write commit body:
   - Wrap lines at ~72 characters
   - Explain **why** changes were made, not just what
   - Include context based on work type:
     - **Plan-based work**: Reference the plan document used
     - **Task switching**: Explain reason and next steps
     - **Partial work**: Document current state and what remains
     - **Fixes**: Describe the issue and resolution approach
     - **Features**: Explain feature value and key decisions
     - **Refactors**: State what changed and rationale
     - **Reverts**: Explain what was reverted and why
   - List skills used during the session (e.g., "Used: -plan, -work")
   - Note any cross-session context if changes span multiple sessions
3. Determine agent attribution from session changes:
   - **Files changed during this session** (edited by the current agent): attribute the current agent
   - **Files changed before the session started** (uncommitted work carried in): inspect the recent change history of those files for agent attribution trailers; if a single other agent is detected, surface it and confirm with the user
   - If attribution is mixed or cannot be determined, ask the user which agent to attribute (Smart pause trigger; Detailed always confirms)
   - The current agent name is always the safe fallback
4. Add agent attribution:
   - Append `[AGENT: {AGENT_NAME}]` as the last line of the commit message
   - Use the agent name determined in step 3 (e.g., "Claude", "GitHub Copilot")
   - This trailer is mandatory for all session-end commits
5. Present for approval:
   - Show the complete commit message (subject + body) to the user
   - Request confirmation or edits
   - Apply user revisions if requested

**Mode behavior:** Detailed = full message review + attribution confirmation; Smart = confirm only when attribution is ambiguous or mixed; Autopilot = present the final message for approval before creating the commit (commit creation is never silent).

### Phase 4: Create Commit

1. Stage the approved files (verify staging state before committing)
2. Create the commit with the prepared message; capture the resulting commit identifier (SHA)
3. Confirm and report:
   - Display the commit SHA to the user
   - Confirm the commit was created successfully
   - Remind the user that changes are not pushed (pushing is a manual user action — never performed by this skill)

### Phase 5: Save Session Artifact

Persist a session record so future sessions (and the user) can trace what happened and why.

1. Allocate a `session-id`:
   - Format: `YYYY-MM-DD-NNN` (today's date + sequential counter)
   - Count existing `docs/plans/.end-session/YYYY-MM-DD-*.md` files for that date; start at `001`
2. Write the artifact to `docs/plans/.end-session/<session-id>.md`:

````markdown
---
type: session
session-id: 2026-09-01-001
timestamp: "2026-09-01T14:30:00"
interactionMode: smart
commit-sha: "<short sha>"
agent: "<attributed agent name>"
files-changed: <count>
status: complete
---

# Session End: <commit subject>

## Reason

<the optional context note from the invocation, or "session complete">

## Changed Files

- <repository-relative path> (added | modified | deleted)

## Commit Message

<verbatim subject + body>

## Skills Used

- <skill names invoked during the session>

## Next Steps

<open todos, incomplete work, or "none">
````

3. Idempotency: if a re-run produces the same `session-id` (same date, same counter position), overwrite the artifact — never duplicate.
4. Registration: append a one-line entry to `docs/plans/index.md` under a `## Session Ends` section (create the section if missing): `<session-id> — <subject> — link to artifact`.

**Mode behavior:** Detailed = show the artifact content before writing; Smart/Autopilot = write and report the path.

### Phase 6: Post-Commit Learnings Sync

1. Suggest a learnings index check:
   - Recommend the user run `/learn maintain` to reconcile `docs/learn/index.md` with the knowledge base on disk (dedup/refresh/prune are included in a maintain pass)
   - This skill does not write `docs/learn/` directly and does not invoke other skills — the user runs `/learn` as a separate step (per the architecture rule: orchestration happens through the agent harness, not skill-to-skill invocation)
2. Final summary:
   - Include the commit SHA
   - Include the session artifact path
   - Remind the user `/learn maintain` is available if learnings were touched this session

## Session Artifact Reference

- **Location:** `docs/plans/.end-session/<session-id>.md`
- **ID format:** `YYYY-MM-DD-NNN` (sequential per date, allocated in Phase 5)
- **Index:** one-line registration in `docs/plans/index.md` under `## Session Ends`
- **Self-healing:** the directory and the `## Session Ends` index section are created on first use if missing

## Commit Message Examples

**Feature work:**

```
Add user authentication system

Implement JWT-based authentication with refresh tokens.
Follows plan docs/plans/2026-05-01-001-auth.md.

Key decisions:
- JWT tokens with 15min expiry
- Refresh tokens stored in httpOnly cookies
- Redis for token blacklist

Used: -plan, -work

[AGENT: Claude]
```

**Partial work:**

```
WIP: Add authentication middleware

Implemented JWT validation middleware and tests.
Auth controller and routes remain for next session.

Next steps:
- Complete auth controller (login, logout, refresh)
- Add integration tests
- Update API documentation

Used: -work

[AGENT: Claude]
```

**Bug fix:**

```
Fix race condition in async state updates

User profile updates were sometimes lost due to race
condition when multiple requests modified same user.

Solution: Add optimistic locking with version field.
Tests added to verify concurrent update handling.

Used: -work

[AGENT: Claude]
```

## Rules

- **Verify working tree** before starting (check for changes)
- **Commit partial work** if the session ends mid-task; document state and next steps clearly
- **Agent trailer mandatory**: every commit must include `[AGENT: ...]` as the last line, attributed to the agent that made the session's changes (fallback: current agent)
- **No automatic push**: never push to a remote; the user controls when to push
- **User approval required**: always present the commit message for confirmation before committing, in every interaction mode
- **No cross-skill invocation**: suggest `/learn maintain` in the final summary; never invoke it directly (per the architecture rule — orchestration happens through the agent harness)
- **Artifact required**: a session artifact must be saved to `docs/plans/.end-session/` for every successful commit; self-heal the directory and index section if missing
- **Tool-agnostic**: describe capabilities ("stage files", "create the commit"), never specific command-line invocations; each agent maps these to its native tools

## Acceptance Criteria

- **Input**: user confirms session completion and there are changes to commit
- **Output**: created commit containing the `[AGENT: ...]` trailer derived from session file changes, with a descriptive body
- **Artifact**: session artifact saved to `docs/plans/.end-session/<session-id>.md` and registered in `docs/plans/index.md`
- **Verification**: commit SHA displayed; session artifact path displayed; `/learn maintain` suggested in the final summary

## References

| Reference                                                                     | Used By                                   |
| ----------------------------------------------------------------------------- | ----------------------------------------- |
| [error-handling.md](references/error-handling.md)                             | All phases (Step 0 verification, recovery) |

## Core Principles

- **Checkpoint, Not Ledger:** One commit per session end captures the state; the session artifact carries the detail. No incremental session logs.
- **Attribution Follows the Work:** The `[AGENT: ...]` trailer reflects who actually changed the files in the session — the current agent by default, verified against change history when pre-session work is present.
- **User Owns the Boundary:** Ending a session is always a user decision; this skill never infers completion and never pushes.
- **Traceable Artifacts:** Every session end produces a persistent, self-describing artifact with a stable ID, registered in the plan index.
- **Fail Explicitly:** Missing trees, ambiguous attribution, or failed writes surface clear errors with recovery suggestions (see [error-handling.md](references/error-handling.md)) — never silent no-ops.
- **Tool-Agnostic:** Steps describe required capabilities; each agent maps them to its native tools.
- **Stay Portable:** Use repository-relative paths only (`docs/plans/.end-session/`, `docs/plans/index.md`).
