---
title: Install Skills
description: Install Arreio skills to the user's .agents/skills directory, making them available in VS Code Copilot Chat.
type: module
version: 1.0
timestamp: "2026-09-01"
---

# Phase 0 - Install Skills

**Purpose:** Copy Arreio skills from the installed npm package to the user's `~/.agents/skills/` directory, making them available for discovery and invocation in VS Code Copilot Chat. This ensures all Arreio workflows (plan, work, review, learn, end-session) are accessible after initialization.

## Workflow

This is the Phase 0 pipeline for the Arreio Init Skill. It orchestrates the following steps before creating project structure.

### Step 1: Verify Installation Context

Verify that the prerequisites are met:

1. Arreio is installed as an npm package in the current project (`node_modules/arreio/` exists).
2. The skills directory exists in the package: `node_modules/arreio/skills/` contains subdirectories for each skill.
3. The user's home directory is accessible (required to create `~/.agents/skills/`).

If any verification fails:

- **Missing package:** Suggest running `npm install arreio` first.
- **Missing skills:** Report a package integrity error (the skills/ directory is missing from the installed package).
- **No home access:** Report an environment error (unable to determine home directory).

### Step 2: Create Target Directory

Create the destination directory hierarchy:

1. If `~/.agents/` does not exist, create it.
2. If `~/.agents/skills/` does not exist, create it.
3. Log: `✓ Created ~/.agents/skills/`

### Step 3: Copy Skills from Package

Copy each skill directory from `node_modules/arreio/skills/` to `~/.agents/skills/`:

**Skills to copy:**

- `plan` — Planning and decomposition
- `work` — Task execution with guardrails
- `review` — Code review and analysis
- `learn` — Knowledge capture and indexing
- `end-session` — Session documentation
- `arreio-init` — Workspace initialization (this skill itself, for re-runs)

**Copy algorithm:**

For each skill:

1. Read the source directory: `node_modules/arreio/skills/<skill-name>/`
2. Copy recursively to destination: `~/.agents/skills/<skill-name>/`
3. Verify the destination directory was created and contains the expected files (`SKILL.md`, `modules/`, `references/`).
4. Log: `✓ Copied <skill-name>`

If any copy operation fails:

- Log the error and the source/destination paths.
- Ask the user to manually verify the source exists and the destination is writable.
- Do not proceed to the next phase.

### Step 4: Verify Installation Success

After all skills are copied, verify that the expected skill files are present:

For each skill, check:

- `~/.agents/skills/<skill-name>/SKILL.md` exists
- Directory structure is intact (modules/, references/ subdirs if present)

If verification passes, log:

```
✓ Arreio skills installed successfully
  - plan
  - work
  - review
  - learn
  - end-session
  - arreio-init

Skills are now available in VS Code Copilot Chat.
```

If verification fails for any skill, report which skills failed and suggest manual verification.

### Step 5: Log Installation Summary

Provide the user with confirmation and next steps:

```
Installation complete. Arreio skills are now available:

Next step: Project structure will be initialized in Step 1 of arreio-init.

You can now use:
  /plan    — Create implementation plans
  /work    — Execute tasks with guardrails
  /review  — Conduct code reviews
  /learn   — Capture and organize knowledge
```

## Success Criteria

After this phase completes:

- ✓ `~/.agents/skills/` directory exists
- ✓ All six skills are copied to `~/.agents/skills/`:
  - `~/.agents/skills/plan/`
  - `~/.agents/skills/work/`
  - `~/.agents/skills/review/`
  - `~/.agents/skills/learn/`
  - `~/.agents/skills/end-session/`
  - `~/.agents/skills/arreio-init/`
- ✓ Each skill directory contains `SKILL.md` and expected subdirectories
- ✓ Skills are ready for discovery by VS Code Copilot Chat

## Error Handling

Refer to [error-handling.md](../references/error-handling.md) for category classification and resolution strategies. Common errors:

- **Category 1 (Missing context):** Arreio package not installed; suggest `npm install arreio`.
- **Category 2 (Routing error):** Skills directory missing from package; report package integrity issue.
- **Category 3 (Environment issue):** Cannot write to `~/.agents/`; insufficient permissions or home dir unavailable.

## Notes

- This phase runs **before** project structure initialization (Phase 1 → Create Core Folders).
- Skills are copied to the user's home directory (`~/.agents/`), not the project directory. This allows skills to be reused across all projects once installed.
- The copy is non-destructive; if skills already exist in `~/.agents/skills/`, they are overwritten with the latest version from the installed package. This supports package updates.
- This phase is idempotent; running it multiple times produces the same result.
