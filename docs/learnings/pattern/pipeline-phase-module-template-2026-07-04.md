---
title: "Pipeline phase module template with verification, processing, and confirmation"
timestamp: "2026-07-04"
category: pattern
domain: skill-design
tags: [pipeline-architecture, module-template, phase-structure, orchestration]
severity: recommended
source: commit 3c17d20
---

# Pipeline Phase Module Template

## Problem

Multi-phase skill pipelines (like the Plan skill) need each phase module to follow a consistent structure for reliability and maintainability. Without a template, modules drift in style, forget verification steps, or handle user interaction inconsistently.

## Solution

Every phase module follows the same 3-section template:

### 1. Step 0: Verification

Before starting any work, verify that the upstream phase produced valid artifacts. Check:
- Artifact exists and is non-empty
- Required fields are present (phase-specific)
- Cross-phase IDs match upstream artifacts
- Interaction mode is present (default to `smart` if missing)

On failure: use the shared error-handling workflow to recover or terminate.

### 2. Processing Steps (Step 1–N)

Each step is a single, clear action:
- **Read inputs** from upstream artifacts or user
- **Apply rules** from reference files (not inline)
- **Delegate complexity** to dedicated reference docs (e.g., complexity scoring lives in `design-complexity-assessment.md`, not in `design.md`)

### 3. Confirmation and Return (Final Steps)

- Read `interactionMode` to determine confirmation behavior
- In **detailed** mode: present artifact, ask user to confirm/edit/abort
- In **smart** mode: auto-proceed unless pause triggers fire
- In **autopilot** mode: auto-proceed (except Tasks phase which always asks)
- Save artifact and return to orchestrator

## Application

- Use this template when creating new phase modules for any skill pipeline
- Keep reference algorithms in separate files; modules should be thin orchestrators
- Every module must include Step 0 verification — never skip input validation

## Concrete Example

All three modules in this commit follow this template:
- `skills/plan/modules/design.md` — Phase 3
- `skills/plan/modules/generate.md` — Phase 4
- `skills/plan/modules/tasks.md` — Phase 5

## Source

- `skills/plan/modules/design.md`
- `skills/plan/modules/generate.md`
- `skills/plan/modules/tasks.md`
- Commit `3c17d20`
