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

### Step 1: Create Core Folder Structure

Creates the organizational spine for Arreio artifacts:

- `docs/plans/` — Stores generated plans and design artifacts
- `docs/learn/` — Stores extracted learnings and insights
- `docs/reports/` — Stores review reports and analysis
- `docs/tasks/` — Stores task lists and execution records
- `docs/archives/` — Stores historical artifacts

**Why:** Downstream skills assume these folders exist and will create files within them.

### Step 2: Initialize Root Architecture Document

**File:** `ARCHITECTURE.md` (project root)

**Rationale:** Provides a single source of truth for project structure, principles, and design decisions. Other skills reference this for context.

**Action:** If `ARCHITECTURE.md` doesn't exist, create it using the [Architecture Template](references/architecture-template.md).

### Step 3: Initialize Plans Index

**File:** `docs/plans/index.md`

**Rationale:** Central registry of all plans. The `plan/SKILL.md` module creates plan files and links them here.

**Action:** If `docs/plans/index.md` doesn't exist, create it using the [Plan Index Template](references/plan-index-template.md).

### Step 4: Create Tasks Folder

**Folder:** `docs/tasks/`

**Rationale:** Root folder for task artifacts. The `plan/SKILL.md` Tasks phase will create per-plan subdirectories (`docs/tasks/<plan-id>/`) with their own indexes when tasks are generated.

**Action:** Create the `docs/tasks/` folder if it doesn't exist.

### Step 5: Initialize Learning Index

**File:** `docs/learn/index.md`

**Rationale:** Central knowledge base index. The `learn/SKILL.md` module organizes learnings and cross-links them here.

**Action:** If `docs/learn/index.md` doesn't exist, create it using the [Learn Index Template](references/learn-index-template.md).

### Step 6: Create Reports Folder

**Folder:** `docs/reports/`

**Rationale:** Stores review reports and analysis artifacts. The `review/SKILL.md` module generates reports here.

**Action:** Create the `docs/reports/` folder if it doesn't exist.

### Step 7: Create Plan Skill Hidden Artifact Directories

**Folders:**

- `docs/plans/.scope/` — Stores Scope phase artifacts
- `docs/plans/.research/` — Stores Research phase artifacts
- `docs/plans/.design/` — Stores Design phase artifacts

**Rationale:** The `plan/SKILL.md` orchestrator saves intermediate phase artifacts in these hidden directories to preserve the planning trail and enable recovery/resumption.

**Action:** Create all three directories if they don't exist.

### Step 8: Create Work Skill Hidden Artifact Directories

**Folders:**

- `docs/plans/.work/.triage/` — Stores Triage phase artifacts
- `docs/plans/.work/.prepare/` — Stores Prepare phase artifacts
- `docs/plans/.work/.execute/` — Stores Execute phase artifacts
- `docs/plans/.work/.review/` — Stores Review phase artifacts

**Rationale:** The `work/SKILL.md` orchestrator saves phase artifacts here during task execution to track work progress and decisions.

**Action:** Create all four directories if they don't exist.

### Step 9: Create Review Skill Hidden Artifact Directories and Registry

**Folders:**

- `docs/plans/.review/.scope/` — Stores Review Scope phase artifacts
- `docs/plans/.review/.prepare/` — Stores Review Prepare phase artifacts
- `docs/plans/.review/.analyze/` — Stores Review Analyze phase artifacts
- `docs/plans/.review/.report/` — Stores Review Report phase artifacts

**File:**

- `docs/plans/.review/index.md` — Central registry of all review reports

**Rationale:** The `review/SKILL.md` orchestrator saves phase artifacts in these hidden directories and maintains a central index of all review reports.

**Action:** Create all four directories if they don't exist. If `docs/plans/.review/index.md` doesn't exist, create it with a header:

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

### Step 10: Create Learn Skill Hidden Artifact Directories

**Folders:**

- `docs/plans/.learn/.capture/` — Stores Capture phase artifacts
- `docs/plans/.learn/.refine/` — Stores Refine phase artifacts
- `docs/plans/.learn/.index/` — Stores Index phase artifacts
- `docs/plans/.learn/.maintain/` — Stores Maintain phase artifacts

**Rationale:** The `learn/SKILL.md` orchestrator saves phase artifacts in these hidden directories to preserve the knowledge entry authoring trail.

**Action:** Create all four directories if they don't exist.

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

- ✓ All five core folders exist: `docs/plans/`, `docs/learn/`, `docs/reports/`, `docs/tasks/`, `docs/archives/`
- ✓ `ARCHITECTURE.md` exists at project root
- ✓ Root-level index files exist:
  - `docs/plans/index.md` (registry of all plans)
  - `docs/learn/index.md` (central knowledge base)
- ✓ Plan skill hidden artifact directories exist:
  - `docs/plans/.scope/`, `docs/plans/.research/`, `docs/plans/.design/`
- ✓ Work skill hidden artifact directories exist:
  - `docs/plans/.work/.triage/`, `docs/plans/.work/.prepare/`, `docs/plans/.work/.execute/`, `docs/plans/.work/.review/`
- ✓ Review skill hidden artifact directories exist:
  - `docs/plans/.review/.scope/`, `docs/plans/.review/.prepare/`, `docs/plans/.review/.analyze/`, `docs/plans/.review/.report/`
  - `docs/plans/.review/index.md` (review reports registry)
- ✓ Learn skill hidden artifact directories exist:
  - `docs/plans/.learn/.capture/`, `docs/plans/.learn/.refine/`, `docs/plans/.learn/.index/`, `docs/plans/.learn/.maintain/`
- ✓ End-session skill hidden artifact directory exists:
  - `docs/plans/.end-session/`
- ✓ Learn category folders exist:
  - `docs/learn/decision/`, `docs/learn/pattern/`, `docs/learn/gotcha/`, `docs/learn/workflow/`
- ✓ Per-plan task indexes created on-demand by plan skill: `docs/tasks/<plan-id>/index.md` (created when Tasks phase runs)
- ✓ You can now run all four Arreio skills (plan, work, review, learn) without setup errors

## Self-Healing Behavior

Downstream skills (plan, learn, work, review) automatically create missing folders and indexes if arreio-init wasn't explicitly run:

- **plan** skill creates missing `docs/plans/` core folders, and allocates `docs/plans/.scope/`, `.research/`, `.design/` directories on first use.
- **work** skill creates missing `docs/plans/.work/` directories (`.triage/`, `.prepare/`, `.execute/`, `.review/`) on first execution.
- **review** skill creates missing `docs/plans/.review/` directories and `index.md` registry on first review.
- **learn** skill creates missing `docs/plans/.learn/` directories and `docs/learn/` category folders on first learning capture.
- **end-session** skill creates missing `docs/plans/.end-session/` directory (and the `## Session Ends` section in `docs/plans/index.md`) on first session end.

**However**, running `arreio-init` upfront provides several benefits:

- All directories are created consistently in one pass
- Ensures the project structure is fully initialized before any skill runs
- Provides a clear baseline for verification (no hidden "auto-created" surprises)
- Reduces latency of first skill invocation

Running arreio-init upfront is **recommended** for new projects, but not strictly required.
