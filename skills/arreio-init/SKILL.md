---
name: arreio-init
description: "Initialize Arreio workflow system. Use when: setting up a new project for Arreio planning, learning, and task execution; preparing workspace before running plan/learn/work skills; bootstrapping project documentation structure."
argument-hint: "run to initialize workspace"
user-invocable: true
version: 1.1.0
timestamp: "2026-08-13"
---

# Arreio Init

## Purpose

**Arreio Init** bootstraps the complete Arreio workflow system for a project. It creates the required folder structure, index files, and architectural documentation that enable the downstream Arreio skills (plan, learn, work, review) to function correctly.

## When to Use

Run this skill when:

- Setting up a **new project** for Arreio workflows
- **First time** using Arreio in an existing project
- After cloning a repo—to ensure all required files and folders are present
- Before invoking other Arreio skills (plan, learn, work, review)

## Dependencies Enabled

After initialization, the following modules can operate:

- **Plan** (`plan/SKILL.md`) - Creates structured implementation plans
- **Learn** (`learn/SKILL.md`) - Extracts and organizes learnings
- **Work** (`work/SKILL.md`) - Executes implementation tasks
- **Review** (`review/SKILL.md`) - Analyzes code changes

## Workflow

The initialization workflow runs in two phases:

1. **Phase 0: Install Skills (Optional)** — Verify or manually copy Arreio skills to `.agents/skills/` in the project (skills are normally installed via npm postinstall, but this phase can install them as a fallback)
2. **Phase 1: Initialize Project Structure** — Create folders, indexes, and architectural documentation

### Step 1: Install Skills (Optional Fallback)

Verify that Arreio skills are installed to the project's `.agents/skills/` directory. See [modules/install.md](modules/install.md) for detailed instructions.

**Why:** Skills must be available in `.agents/skills/` so your AI coding agent can discover them. Normally, the npm postinstall script handles this automatically when you run `npm install arreio`. This step provides a manual fallback if postinstall was skipped.

**When to run:** Skip this step if npm postinstall has already run. If skills are not yet installed, this phase will copy them from `node_modules/arreio/skills/` to `.agents/skills/`.

**Action:** See [install.md](modules/install.md) for verification and manual installation steps.

### Step 2: Create Core Folder Structure

Creates the organizational spine for Arreio artifacts:

- `docs/plans/` — Stores generated plans and design artifacts
- `docs/learn/` — Stores extracted learnings and insights
- `docs/review/` — Stores review reports and analysis
- `docs/tasks/` — Stores task lists and execution records
- `docs/archives/` — Stores historical artifacts

**Why:** Downstream skills assume these folders exist and will create files within them.

### Step 3: Initialize Root Architecture Document

**File:** `ARCHITECTURE.md` (project root)

**Rationale:** Provides a single source of truth for project structure, principles, and design decisions. Other skills reference this for context.

**Action:** If `ARCHITECTURE.md` doesn't exist, create it using the [Architecture Template](references/architecture-template.md).

### Step 4: Initialize Plans Index

**File:** `docs/plans/index.md`

**Rationale:** Central registry of all plans. The `plan/SKILL.md` module creates plan files and links them here.

**Action:** If `docs/plans/index.md` doesn't exist, create it using the [Plan Index Template](references/plan-index-template.md).

### Step 5: Create Tasks Folder

**Folder:** `docs/tasks/`

**Rationale:** Root folder for task artifacts. The `plan/SKILL.md` Tasks phase will create per-plan subdirectories (`docs/tasks/<plan-id>/`) with their own indexes when tasks are generated.

**Action:** Create the `docs/tasks/` folder if it doesn't exist.

### Step 6: Initialize Learning Index

**File:** `docs/learn/index.md`

**Rationale:** Central knowledge base index. The `learn/SKILL.md` module organizes learnings and cross-links them here.

**Action:** If `docs/learn/index.md` doesn't exist, create it using the [Learn Index Template](references/learn-index-template.md).

### Step 7: Plan Skill Hidden Artifact Directories (not created at init)

**Folders:**

- `docs/plans/.scope/` — Stores Scope phase artifacts
- `docs/plans/.research/` — Stores Research phase artifacts
- `docs/plans/.design/` — Stores Design phase artifacts

**Rationale:** The `plan/SKILL.md` orchestrator writes intermediate phase artifacts to these hidden directories **only when the user picks `detailed` interaction mode**. In `smart`/`autopilot` they are passed in context.

**Action:** Do **not** create them. The plan skill creates them lazily on first `detailed` run.

### Step 8: Work Skill Artifact Directories

**Folders:**

- `docs/plans/.work/.triage/` — Stores Triage phase artifacts
- `docs/plans/.work/.prepare/` — Stores Prepare phase artifacts
- `docs/plans/.work/.execute/` — Stores Execute phase artifacts
- `docs/plans/.work/.review/` — Stores Review phase artifacts

**Rationale:** `.triage/`, `.prepare/`, `.execute/` hold intermediate artifacts written **only in `detailed` mode**. `.review/` holds the Work Report, which is always written (read by `/review` and `/learn`).

**Action:** Create only `docs/plans/.work/.review/`. The work skill creates the other three lazily on first `detailed` run.

### Step 9: Review Skill Artifact Directories and Registry

**Folders:**

- `docs/review/.scope/` — Stores Review Scope phase artifacts
- `docs/review/.prepare/` — Stores Review Prepare phase artifacts
- `docs/review/.analyze/` — Stores Review Analyze phase artifacts
- `docs/review/.report/` — Stores Review Report phase artifacts

**File:**

- `docs/review/index.md` — Central registry of all review reports

**Rationale:** `.scope/`, `.prepare/`, `.analyze/` hold intermediate artifacts written **only in `detailed` mode**. `.report/` holds the Review Report (always written). The orchestrator also maintains a central index of all review reports.

**Action:** Create only `docs/review/.report/`; the review skill creates the other three lazily on first `detailed` run. If `docs/review/index.md` doesn't exist, create it with a header:

```markdown
---
type: "index"
title: "Review Reports Index"
description: "Central registry of all code review reports."
timestamp: "2026-07-03"
---

## Overview

This is the index of all review reports for the project. Reports are organized by review-id and linked from this registry.

## Review Reports

<!-- Add new review reports below. Reports are generated by the `/review` skill. -->

_No review reports yet._
```

### Step 10: Learn Skill Hidden Artifact Directories (not created at init)

**Folders:**

- `docs/learn/.capture/` — Stores Capture phase artifacts
- `docs/learn/.refine/` — Stores Refine phase artifacts
- `docs/learn/.index/` — Stores Index phase artifacts
- `docs/learn/.maintain/` — Stores Maintain phase artifacts

**Rationale:** The `learn/SKILL.md` orchestrator writes phase artifacts here **only in `detailed` mode**. Durable entries and the index are always written elsewhere.

**Action:** Do **not** create them. The learn skill creates them lazily on first `detailed` run.

### Step 11: Create End-Session Skill Hidden Artifact Directory

**Folder:**

- `docs/plans/.end-session/` — Stores session-end artifacts

**Rationale:** The `end-session/SKILL.md` skill saves a session artifact here for every session-end commit, providing a traceable record of what was done, why, and by which agent.

**Action:** Create the directory if it doesn't exist.

### Step 12: Create Learn Category Folders

**Folders:**

- `docs/learn/decision/` — Stores decision-type learnings
- `docs/learn/pattern/` — Stores pattern-type learnings
- `docs/learn/gotcha/` — Stores gotcha-type learnings
- `docs/learn/workflow/` — Stores workflow-type learnings

**Rationale:** The `learn/SKILL.md` skill organizes knowledge entries by type. These folders provide category structure for the learnings index.

**Action:** Create all four folders if they don't exist.

## Success Criteria

After initialization, verify:

- ✓ All Arreio skills are installed to `.agents/skills/`:
  - `.agents/skills/plan/`
  - `.agents/skills/work/`
  - `.agents/skills/review/`
  - `.agents/skills/learn/`
  - `.agents/skills/end-session/`
  - `.agents/skills/arreio-init/`
- ✓ All five core folders exist: `docs/plans/`, `docs/learn/`, `docs/review/`, `docs/tasks/`, `docs/archives/`
- ✓ `ARCHITECTURE.md` exists at project root
- ✓ Root-level index files exist:
  - `docs/plans/index.md` (registry of all plans)
  - `docs/learn/index.md` (central knowledge base)
- ✓ Always-written report directories exist:
  - `docs/plans/.work/.review/` (Work Reports), `docs/review/.report/` (Review Reports)
  - `docs/review/index.md` (review reports registry)
- ✓ Intermediate phase-artifact directories (`.scope/`, `.research/`, `.design/`, `.triage/`, `.prepare/`, `.execute/`, `.analyze/`, `.capture/`, `.refine/`, `.index/`, `.maintain/`) are **not** created — skills create them lazily, only in `detailed` interaction mode
- ✓ End-session skill hidden artifact directory exists:
  - `docs/plans/.end-session/`
- ✓ Learn category folders exist:
  - `docs/learn/decision/`, `docs/learn/pattern/`, `docs/learn/gotcha/`, `docs/learn/workflow/`
- ✓ Per-plan task indexes created on-demand by plan skill: `docs/tasks/<plan-id>/index.md` (created when Tasks phase runs)
- ✓ You can now run all four Arreio skills (plan, work, review, learn) without setup errors

## Self-Healing Behavior

Downstream skills (plan, learn, work, review) automatically create missing folders and indexes if arreio-init wasn't explicitly run:

- **plan** skill creates missing `docs/plans/` core folders; creates `docs/plans/.scope/`, `.research/`, `.design/` only in `detailed` mode.
- **work** skill creates `docs/plans/.work/.review/` on first execution; creates `.triage/`, `.prepare/`, `.execute/` only in `detailed` mode.
- **review** skill creates `docs/review/.report/` and the `index.md` registry on first review; creates `.scope/`, `.prepare/`, `.analyze/` only in `detailed` mode.
- **learn** skill creates the `docs/learn/` category folders on first learning capture; creates `.capture/`, `.refine/`, `.index/`, `.maintain/` only in `detailed` mode.
- **end-session** skill creates missing `docs/plans/.end-session/` directory (and the `## Session Ends` section in `docs/plans/index.md`) on first session end.

**However**, running `arreio-init` upfront provides several benefits:

- All directories are created consistently in one pass
- Ensures the project structure is fully initialized before any skill runs
- Provides a clear baseline for verification (no hidden "auto-created" surprises)
- Reduces latency of first skill invocation

Running arreio-init upfront is **recommended** for new projects, but not strictly required.
