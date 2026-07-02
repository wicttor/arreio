# Error Handling & Recovery — PWRL Plan

**Philosophy:** Fail explicitly, not silently. Each phase has clear error handling with recovery suggestions.

## Phase 1 (Scope) Errors

### Empty Input

**Error:** User provides no task description.

**Recovery:** Prompt user with: "What would you like to plan? Describe the task or project." Retry after user input.

### Non-Software Domain

**Error:** Validation detects task is non-software (e.g., content marketing, legal review).

**Recovery:** Return error message suggesting alternative tool or workflow. Abort planning.

### Ambiguous Input

**Error:** Task description is unclear or spans multiple unrelated domains.

**Recovery:** Ask clarifying questions (e.g., "Which component is the priority?" "What's the deployment environment?"). Bootstrap scope from user responses. Retry after clarification.

### Missing Directories

**Error:** `docs/plans/`, `docs/learnings/INDEX.md`, `docs/requirements/`, or `docs/brainstorms/` do not exist.

**Recovery:**

- If `docs/plans/` does not exist, treat it as an empty directory and continue.
- If `docs/learnings/INDEX.md`, `docs/requirements/`, or `docs/brainstorms/` do not exist, skip those lookup steps and note in the scope artifact: "No prior context found for [directory]."

### Resume Operation

**Error:** User selects "Resume" on an existing plan but no clear entry point is specified.

**Recovery:** Ask user: "Which phase would you like to resume from? (1=Scope, 2=Research, 3=Design, 4=Generate)". Load the most recent artifact from the last completed phase and continue the pipeline from the selected phase, skipping earlier phases.

**User Actions:** User can retry, provide clarification, resume from a checkpoint, or abort.

---

## Phase 2 (Research) Errors

### Codebase Analysis Fails

**Error:** Repository structure is unusual, unrecognized tech stack, or codebase is inaccessible.

**Recovery:** Continue with minimal tech stack information (e.g., "JavaScript detected from package.json"). Proceed to next phase. Recommend manual tech stack review if needed.

### High-Risk Area Identified

**Error:** Analysis detects security, performance, distributed systems, or compliance concerns.

**Recovery:** Recommend external research (e.g., "Consider reviewing OWASP guidelines for this authentication flow"). User can approve research, skip, or manually investigate. Pipeline continues regardless.

**User Actions:** User can approve research, skip, or manually investigate.

---

## Phase 3 (Design) Errors

### Circular Dependency Detected

**Error:** Topological sort detects a cycle in the unit dependency graph (e.g., U1 → U2 → U3 → U1).

**Recovery:** Report the cycle path clearly (e.g., "Circular dependency detected: U1 → U2 → U3 → U1"). Halt pipeline and prompt user:

1. Review the dependency graph
2. Refactor to break the cycle (e.g., move a dependency to a separate pre-unit, merge units, or reorder phases)
3. Once refactored, ask: "Ready to continue with updated units?" and proceed to confirmation step

Do not proceed to Phase 4 until cycle is resolved.

### Too Many Units (15+)

**Error:** Design produces 15 or more implementation units, exceeding recommended complexity threshold.

**Recovery:**

1. Warn user: "This plan contains [N] units, exceeding the recommended maximum of 15. Consider consolidating related units or splitting into sub-plans."
2. If user acknowledges but does not consolidate, add prominent note at the top of the generated plan (Phase 4):
   ```
   WARNING — This plan contains [N] units, which exceeds the recommended maximum of 15.
   Consider splitting into sub-plans before execution.
   ```
3. Pipeline continues; warning persists in final plan document.

### Insufficient Detail

**Error:** A unit lacks acceptance criteria, test scenarios, or clear approach.

**Recovery:** Prompt user to add missing detail:

- "Unit U3 needs acceptance criteria. Please specify what 'done' looks like."
- Offer to split unit if too large: "Would you like to split U3 into smaller units?"

**User Actions:** User can refactor, consolidate, or proceed with awareness of incomplete detail.

---

## Phase 4 (Generate) Errors

### Filename Collision

**Error:** Generated filename already exists in `docs/plans/`.

**Recovery:** Offer user options:

1. **Update:** Overwrite the existing plan (with confirmation)
2. **Increment:** Auto-generate new filename by incrementing sequence number (e.g., `2026-06-24-001-foo.md` → `2026-06-24-002-foo.md`)
3. **Cancel:** Abort file write and return to Phase 3

User selects option and pipeline proceeds or halts accordingly.

### Tier Selection Ambiguous

**Error:** Two or more tier criteria (unit count, complexity, effort) point to different tiers.

**Example:** Unit count = 3 (FAST), complexity = HIGH (DEEP), effort = 8 hours (STANDARD)

**Recovery:** Present the conflict to user:

```
Tier criteria conflict detected:
- Unit count: 3 (FAST tier)
- Complexity: HIGH (DEEP tier)
- Effort: 8 hours (STANDARD tier)

Which tier do you prefer? (FAST / STANDARD / DEEP)
```

User selects tier; pipeline proceeds with that tier. Tier selection is not automatic.

### Failed File Write

**Error:** File write fails due to permissions, disk space, or invalid path.

**Recovery:**

1. Check permissions on `docs/plans/` directory
2. Verify disk space available
3. If persistent, suggest manual options:
   - "Try saving to a different location first, then move to `docs/plans/`"
   - Offer to output plan content to console for manual copy-paste

**User Actions:** User can resolve permissions, retry, or save manually.

---

## Precedence & Interaction Mode

All phase confirmations (e.g., "Confirm decomposition?", "Select tier?") are gated by `interaction_mode` set in Phase 1:

- **Detailed mode:** Execute all confirmation steps as specified above. Wait for user input.
- **Yolo mode:** Skip all mid-phase confirmations and proceed automatically (except error recovery pauses like circular dependencies, tier ambiguity).

**Exception:** Error recovery steps (circular dependency refactoring, tier conflict resolution) always pause the pipeline and require user action, regardless of interaction mode.

---

## Recovery Philosophy

- **Explicit over Silent:** All errors are reported with clear recovery options. No silent failures.
- **User Agency:** Where possible, offer choices (refactor / consolidate / proceed) rather than blocking.
- **Graceful Degradation:** Phase 2 codebase analysis failing doesn't block Phase 3; instead proceed with minimal info.
- **Final Warnings:** Critical issues (too many units, tier conflicts) are captured in plan output or final confirmation, not silently suppressed.
