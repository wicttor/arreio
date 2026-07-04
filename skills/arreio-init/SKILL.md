---
name: arreio-init
description: "Initialize Arreio workflow system. Use when: setting up a new project for Arreio planning, learning, and task execution; preparing workspace before running plan/learn/work skills; bootstrapping project documentation structure."
argument-hint: "run to initialize workspace"
user-invocable: true
version: 1.0.1
timestamp: "2026-07-03"
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

### Step 4: Initialize Tasks Index

**File:** `docs/tasks/<plan-id>/index.md`

**Rationale:** Central task registry and execution log. The `work/SKILL.md` module tracks tasks here.

**Action:** If `docs/tasks/<plan-id>/index.md` doesn't exist, create it using the [Tasks Index Template](references/tasks-index-template.md).

### Step 5: Initialize Learning Index

**File:** `docs/learn/index.md`

**Rationale:** Central knowledge base index. The `learn/SKILL.md` module organizes learnings and cross-links them here.

**Action:** If `docs/learn/index.md` doesn't exist, create it using the [Learn Index Template](references/learn-index-template.md).

## Success Criteria

After initialization, verify:

- ✓ All five core folders exist (`plans/`, `learn/`, `reports/`, `tasks/`, `archives/`)
- ✓ `ARCHITECTURE.md` exists at project root
- ✓ All four index files exist:
  - `docs/plans/index.md`
  - `docs/tasks/<plan-id>/index.md`
  - `docs/learn/index.md`
- ✓ You can now run other Arreio skills without setup errors
