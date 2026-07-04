---
title: Task Artifact
description: Template for the Task Artifact produced by the Tasks phase. Defines the schema for a single executable task file, including goal, steps, dependencies, files, test scenarios, and acceptance criteria.
type: Template
version: 1.0
timestamp: "2026-07-03"
---

# Task Artifact

The product of the **Tasks** phase (Phase 5) is a set of granular, executable task files — one per slice of the finalized plan. Each task file is self-contained enough to execute without re-reading the full plan, and serves as the handoff point to the Work skill (`work/SKILL.md`).

When the **Tasks** phase completes, it produces one task file per slice, saved to `docs/tasks/<plan-id>/`, with this schema:

## Schema

```yaml
---
id: <plan-id>-T<NN>
title: "[Task title]"
plan-id: <plan-id>
unit: U<NN> | U<NN><letter>
tier: fast | standard | deep
status: not-started
priority: P0 | P1 | P2
dependencies: [<task-id>, ...]
files:
  create: [path/to/file, ...]
  modify: [path/to/file, ...]
  test: [path/to/test, ...]
estimated-effort: "<hours or days>"
---

# [Task Title]

## Goal
[What this task accomplishes, inherited from the implementation unit. 1-2 sentences.]

## Steps
1. [Concrete, actionable step]
2. [Concrete, actionable step]
3. [Concrete, actionable step]

## Test Scenarios
- [Scenario]: [Input -> Expected Outcome]
- [Scenario]: [Input -> Expected Outcome]

## Acceptance Criteria
- [ ] [Verifiable criterion 1]
- [ ] [Verifiable criterion 2]
- [ ] [Verifiable criterion 3]

## Dependencies
- [task-id]: [why this task must complete first, or "None"]

## Notes
[Any context, gotchas, references to learnings, or links to related tasks. Optional.]
```

## Validation Rules

- **id:** Required. Format `<plan-id>-T<NN>` where `NN` is zero-padded 2 digits matching dependency order.
- **title:** Required. Short, action-oriented (e.g., "Set up Redis client and session store interface").
- **plan-id:** Required. Must match the Final Plan's `plan-id` for traceability.
- **unit:** Required. The originating implementation unit ID (e.g., `U1`, `U2a`). If a task merges units, list all (e.g., `U3, U4`).
- **tier:** Required. Inherited from the Final Plan (`fast | standard | deep`).
- **status:** Required. Initial value `not-started`. The Work skill updates this to `in-progress`, `completed`, or `blocked`.
- **priority:** Required. `P0` (blocks all), `P1` (critical path), `P2` (deferrable).
- **dependencies:** Required (may be empty list). Must reference task IDs that appear earlier in dependency order.
- **files:** Required. At least one of `create`, `modify`, or `test` must be non-empty. All paths must be repository-relative.
- **estimated-effort:** Required. Rough estimate in hours or days (e.g., "2 hours", "1 day"). Used by the Work phase for sequencing.
- **Goal:** Required. 1–2 sentences, inherited from the unit.
- **Steps:** Required. At least 1 concrete step. Each step must be actionable (not "implement the feature" — break it down).
- **Test Scenarios:** Required for foundation and integration tasks (phases 1–2). Optional for rollout-only tasks. Format: `[Scenario]: [Input -> Expected Outcome]`.
- **Acceptance Criteria:** Required. At least 1 verifiable criterion. Must be checkable without subjective judgment.
- **Notes:** Optional. May reference learnings, gotchas, or related tasks.

## Example

```yaml
---
id: 2026-07-03-001-T01
title: "Set up Redis client and session store interface"
plan-id: 2026-07-03-001
unit: U1
tier: standard
status: not-started
priority: P0
dependencies: []
files:
  create:
    - src/lib/redis-client.ts
    - src/lib/session-store.ts
  test:
    - src/lib/redis-client.test.ts
estimated-effort: "4 hours"
---

# Set up Redis client and session store interface

## Goal
Create a Redis client wrapper and define the session storage interface that the Redis-backed implementation will satisfy. This is the foundation unit — all later session work depends on it.

## Steps
1. Add `ioredis` dependency to `package.json`
2. Create `src/lib/redis-client.ts` exporting a configured Redis client with connection retry logic
3. Define `SessionStore` interface in `src/lib/session-store.ts` with `get`, `save`, `delete` methods
4. Write `src/lib/redis-client.test.ts` covering connection, TTL, and error scenarios

## Test Scenarios
- Store/retrieve session: store {id, data} -> retrieve returns same data
- TTL expiration: store with 1s TTL -> after 1s, get returns null
- Connection error: drop connection -> get throws retryable error

## Acceptance Criteria
- [ ] `SessionStore` interface exported with `get`, `save`, `delete` methods
- [ ] Redis client connects using `REDIS_URL` env var with retry on failure
- [ ] All test scenarios pass
- [ ] No existing tests broken

## Dependencies
- None

## Notes
- Reuse the connection retry pattern from `docs/learnings/pattern/redis-retry-2026-07-02.md` if it exists
- Keep the client wrapper thin — business logic belongs in the session store implementation (T02)
- Feature flag `feature.redis_sessions` should be added in T04, not here
```

## File-Naming Convention

Task files are named and stored as:

```
docs/tasks/<plan-id>/T<NN>-<kebab-case-name>.md
```

**Example:**

```
docs/tasks/2026-07-03-001/
  T01-redis-client-setup.md
  T02-redis-session-store.md
  T03-session-middleware-refactor.md
  T04-dual-write-cutover.md
```

## Usage in Workflow

1. **Tasks Phase** reads the Final Plan's Implementation Units and slices them into tasks per [task-slicing-rules.md](../../task-slicing-rules.md)
2. Each task file is saved to `docs/tasks/<plan-id>/T<NN>-<name>.md`
3. **Tasks Phase** updates `docs/tasks/index.md` with a checklist of all tasks for the plan
4. **Work skill** (`work/SKILL.md`) reads task files, executes them in dependency order, and updates `status` and the index checklist

## Index Entry Format

After saving all task files, append a section to `docs/tasks/index.md`:

```markdown
## 2026-07-03-001 — Migrate Session Storage to Redis

- [ ] T01 — Set up Redis client and session store interface — `docs/tasks/2026-07-03-001/T01-redis-client-setup.md`
- [ ] T02 — Redis session store implementation — `docs/tasks/2026-07-03-001/T02-redis-session-store.md`
- [ ] T03 — Session middleware refactor — `docs/tasks/2026-07-03-001/T03-session-middleware-refactor.md`
- [ ] T04 — Dual-write and cutover — `docs/tasks/2026-07-03-001/T04-dual-write-cutover.md`
```

The `- [ ]` (unchecked) markers are updated to `- [x]` by the Work skill as tasks complete.

## Missing Field Recovery

If a task file is incomplete at validation, use this recovery workflow:

| Field               | Validation                  | Recovery                               |
| ------------------- | --------------------------- | -------------------------------------- |
| id                  | Matches `<plan-id>-T<NN>`   | Regenerate from dependency order       |
| unit                | References a plan unit      | Ask user to map the task to a unit     |
| files               | At least one path non-empty | Ask user which files the task touches  |
| Goal                | Non-empty, from unit        | Inherit from the originating unit      |
| Steps               | At least 1 actionable step  | Ask user to break down the unit's goal |
| Test Scenarios      | Present for phases 1–2      | Inherit from the unit's test scenarios |
| Acceptance Criteria | At least 1 checkable item   | Derive from test scenarios             |
| dependencies        | References earlier task IDs | Re-run dependency ordering algorithm   |

**Note:** If a task cannot be produced because the plan has no Implementation Units, abort the Tasks phase and ask the user to re-run the Generate phase — the plan is incomplete.
