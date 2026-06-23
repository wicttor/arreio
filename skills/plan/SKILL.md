---
type: skill
title: Plan
name: plan
description: Create structured implementation plans with three tiers, Fast, Standard, Deep. Orchestrates scope, research, design, and generation phases.
group: plan
argument-hint: "[task description, requirements doc, or goal to plan]"
tags:
  - planning
  - architecture
  - structured-output
author: "@wicttor"
---

# Plan

Create durable implementation plans that can be handed off for execution. Orchestrates a deterministic pipeline of micro-skills: scope → research → design → generate.

## Purpose

Plans capture decisions, structure, and approach before execution. They enable into the project:

- Remove uncertainty about the implementation
- Clarify ambiguities regarding the request, idea or prompt provided
- Clear scope and success criteria
- Identified risks and dependencies
- Concrete implementation units with acceptance criteria
- Knowledge reuse through related learnings
- Confidence that work won't go off the rails

## Core Workflow: Phased pipeline

```
INPUT (task description)
  ↓
PHASE 1: Scope (pwrl-plan-scope)
  → Gather context, validate domain, bootstrap requirements
  → Output: Scoped context artifact
  ↓
PHASE 2: Research (pwrl-plan-research)
  → Discover patterns, identify risks, recommend external research
  → Output: Research findings artifact
  ↓
PHASE 3: Design (pwrl-plan-design)
  → Decompose into units, map dependencies, assess complexity
  → Output: Design artifact with unit decomposition
  ↓
PHASE 4: Generate (pwrl-plan-generate)
  → Select tier, render plan, embed learnings, save to docs/plans/
  → Output: Final plan document saved to file
  ↓
OUTPUT (plan file ready for execution)
```
