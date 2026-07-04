---
title: Research
description: Research the task and gather relevant information, requirements, and constraints. Produces a Research Findings Artifact for downstream phases.
type: module
version: 1.0
timestamp: "2026-07-02"
---

# Phase 2 - Research

**Purpose:** Second step in the planning workflow. Performs local codebase research, detects high-risk areas, and determines if external research is needed. Returns [research findings](../references/templates/artifacts/research-findings.md) that inform the design phase.

## Workflow

This is the Phase 2 pipeline for the Plan Skill. It orchestrates the following steps:

### Step 0: Verification

Before starting the **Research** phase, verify that the Orchestrator skill has provided a valid **Scoped Context Artifact** from the previous phase, **Scope**. If the artifact is missing or invalid, use the **Error Handling & Recovery workflow** to recover or terminate the plan.

### Step 1: Local Pattern Discovery

1. **Read the scoped context** to understand the task and extract key terms (domain, feature, technology area).

2. **Detect tech stack** from config files in repository root:
   - Check for: `package.json` (Node.js), `pyproject.toml` (Python), `go.mod` (Go), `Cargo.toml` (Rust), `Gemfile` (Ruby), `composer.json` (PHP), `pom.xml` (Java), `build.gradle` (Java/Kotlin)
   - Record detected tech stack and versions for Step 5
   - If multiple tech stacks detected, prioritize primary language
   - **If NO config files match:** Record "Unknown/Multi-language" and proceed to Step 3 using generic search queries (e.g., "architecture", "pattern", "implementation") instead of tech-specific table. Note: This may result in broader matches and lower confidence.

3. **Define tech-stack-specific search queries** based on detected stack and task domain:

   | Tech Stack | Example Query (Auth Pattern)                       | Example Query (API Pattern)                   |
   | ---------- | -------------------------------------------------- | --------------------------------------------- |
   | Node.js    | "middleware", "passport", "jwt", "express auth"    | "router", "express", "endpoint", "middleware" |
   | Python     | "decorator", "authenticate", "middleware", "flask" | "route", "flask", "endpoint", "blueprint"     |
   | Go         | "middleware", "handler", "auth", "gin"             | "handler", "route", "gin", "endpoint"         |
   | Rust       | "middleware", "guard", "auth", "actix"             | "handler", "route", "actix", "endpoint"       |
   | Java       | "filter", "interceptor", "security", "spring"      | "controller", "endpoint", "spring", "mapping" |

4. **Search in two phases** (hybrid approach):

   **Phase A — Quick pattern match (grep_search):**
   - Search common directories: `src/`, `app/`, `lib/`, `services/`, `api/`, `controllers/`, `handlers/`
   - Use tech-stack-specific queries from table above
   - Also search for: `architecture.md`, `design.md`, `ARCHITECTURE.md`, `DESIGN.md` at repo root and in `docs/`, `design/`, `architecture/` subdirectories
   - **Collect all unique file paths found** (count across all Phase A searches; deduplicate)
   - Record total count and note which queries yielded matches

   **Phase B — Pattern gap detection (semantic_search, conditional):**
   - **Decision rule:** If Phase A found fewer than 3 unique file paths, proceed to Phase B
   - Run semantic search with task description
   - Example: "How is authentication implemented in this codebase?" or "Where are API endpoints defined?"
   - Captures conceptual patterns missed by grep
   - **If Phase A found 3+ files:** Skip Phase B; proceed to Step 5 with existing matches

5. **Count confidence levels** based on total unique file matches:
   - **HIGH:** 3 or more files with pattern examples
   - **MEDIUM:** 1–2 file examples found
   - **LOW (or 0):** No pattern examples in codebase

6. **For each pattern found, record:**
   - File path(s)
   - Pattern name and brief description
   - Confidence level (HIGH/MEDIUM/LOW)
   - Relevant code snippet or line range (if available)

7. **Output:** Compile patterns found into `Patterns Found` section of Research Findings Artifact with confidence levels.

### Step 2: High-Risk Area Detection

- Scan the task description and scoped context for high-risk keywords across six areas: Security, Payments, APIs, Migrations, Complex Logic, and Infrastructure.
- For details on the risk keyword table, area definitions, and heuristics for assigning risk levels, see **[high-risk-detection.md](../references/high-risk-detection.md)**.

### Step 3: External Research Decision

1. Apply the decision rule:
   ```
   should_run_external_research = high_risk_detected AND patterns_found_count < 3
   ```
2. If `should_run_external_research` is true:
   - Provide specific web search guidance with query.

### Step 4: External Research Guidance (if needed)

Generate targeted web search queries when external research is recommended.
For query templates, formatting guidance, and examples for each high-risk area, see **[external-research-guidance.md](../references/external-research-guidance.md)**.

### Step 5: Technical Constraints Gathering

1. Document all technical constraints found:
   - Framework and language versions from config files
   - Performance requirements or implications
   - Compatibility notes (e.g., "must support IE11", "must work with existing auth")
   - Deployment constraints (e.g., "must run on AWS Lambda")
   - Integration constraints (e.g., "must use existing logging framework")

### Step 6: Generate the Research Findings Artifact

1. **Generate a unique `research-id`** using the daily counter algorithm:
   - Format: `YYYY-MM-DD-NNN-research` where `NNN` is a zero-padded 3-digit counter
   - **Algorithm:**
     - Get current date in UTC (e.g., 2026-07-02)
     - Check existing research files in `docs/plans/.research/` for today's date
     - Count existing files matching `2026-07-02-*.md`
     - Set `NNN = (count + 1)` formatted as zero-padded 3 digits (001, 002, 010, etc.)
     - Example: If two plans created today, next one gets `research-id: 2026-07-02-003-research`
   - **Error handling:** If `docs/plans/.research/` does not exist, create it; treat count as 0 and start from 001

2. Produce a **Research Findings Artifact** block (as markdown) with the schema defined in `../references/templates/artifacts/research-findings.md`.
   - Include the generated `research-id` in the artifact

### Step 7: Present and Confirm

1. Read the `interactionMode` value from the context (set by Orchestrator; see **[interaction-mode-propagation.md](../references/interaction-mode-propagation.md)** for details).

2. **If `interactionMode = detailed`:**
   - Present the assembled Research Findings Artifact to the user via `ask_user_question` for explicit confirmation
   - Ask: "Are these research findings sufficient to proceed to design?"
   - Options: (1) Proceed to Design, (2) Edit & Retry, (3) Abort
   - If user selects "Edit & Retry," iterate through Steps 1-5 as needed
   - If user selects "Abort," stop and inform Orchestrator of abort
   - If user selects "Proceed," continue to Step 3 below

3. **If `interactionMode = smart`:**
   - Check for HIGH-risk flags in the Research Findings:
     - Are there 3+ learning gaps?
     - Did domain validation flag non-software task?
     - Are requirements conflicting?
   - If HIGH-risk flag present: Pause and show artifact with risk description; ask "Should I proceed anyway?"
   - If no HIGH-risk flag: Auto-proceed (no confirmation)

4. **If `interactionMode = autopilot`:**
   - Auto-proceed immediately to save and return (no confirmation needed)

5. **Save the artifact:**
   - Save the Research Findings Artifact (markdown block) to `docs/plans/.research/<research-id>.md`
   - Verify that `interactionMode` is included in the saved artifact (for downstream phases to read)

6. **Return to Orchestrator:**
   - Return the Research Findings Artifact and `interactionMode` value to the Orchestrator skill
   - Orchestrator will handle transition to Phase 3 (Design) or abort based on confirmation result

## Output: Research Findings Artifact

- Verify that the Research Findings Artifact is complete and valid, containing all required fields, and it accurately reflects the user's input and any existing plans, learnings, or requirements found.
- Verify that the `interactionMode` value is set correctly based on the user's selection in the Orchestrator skill.
- Verify that the artifact is saved to `docs/plans/.research/<research-id>.md` for future reference or reuse.

> Pass the research findings to `design` (Phase 3) for the design phase.
