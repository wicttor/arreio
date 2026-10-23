---
title: Research
description: Research the task and gather relevant information, requirements, and constraints. Produces a Research Findings Artifact for downstream phases.
type: module
version: 1.2
timestamp: "2026-10-23"
---

# Phase 2 - Research

**Purpose:** Second step in the planning workflow. Performs local codebase research, detects high-risk areas, and determines if external research is needed. Returns [research findings](../references/templates/artifacts/research-findings.md) that inform the design phase.

## Workflow

This is the Phase 2 pipeline for the Plan Skill. It orchestrates the following steps:

### Step 0: Verification

Run the **[Step 0 verification](../references/error-handling.md)**. Required input: a valid **Scoped Context Artifact** from Scope carrying `scope-id`, `domain`, `Problem`, `Intended Behavior`, `Success Criteria`, and `interactionMode`.

### Step 1: Local Pattern Discovery

1. **Read the scoped context** to understand the task and extract key terms (domain, feature, technology area).

2. **Detect tech stack** from config files in repository root:
   - Check for: `package.json` (Node.js), `pyproject.toml` (Python), `go.mod` (Go), `Cargo.toml` (Rust), `Gemfile` (Ruby), `composer.json` (PHP), `pom.xml` (Java), `build.gradle` (Java/Kotlin), `*.uproject` / `*.Build.cs` / `CMakeLists.txt` (C++/Unreal), `*.sln` / `*.csproj` (C#/.NET)
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
   | C++ / Unreal | "UCLASS", "Subsystem", "AttributeSet", "GameplayEffect" | "Interface", "Delegate", "Seam", "Port" |
   | C# / .NET  | "interface", "service", "middleware"               | "controller", "handler", "repository"         |

4. **Search in two phases** (hybrid approach):

   **Phase A — Pattern search (literal):**
   - Search common directories: `src/`, `app/`, `lib/`, `services/`, `api/`, `controllers/`, `handlers/`
   - Use tech-stack-specific queries from table above
   - Also search for: `architecture.md`, `design.md`, `ARCHITECTURE.md`, `DESIGN.md` at repo root and in `docs/`, `design/`, `architecture/` subdirectories
   - **Collect all unique file paths found** (count across all Phase A searches; deduplicate)
   - Record total count and note which queries yielded matches

   **Phase B — Pattern gap detection (meaning-based, conditional):**
   - **Decision rule:** If Phase A found fewer than 3 unique file paths, proceed to Phase B
   - Run a meaning-based search using the task description as the query
   - Example: "How is authentication implemented in this codebase?" or "Where are API endpoints defined?"
   - Captures conceptual patterns missed by literal pattern search
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

### Step 1b: Codebase Trace

Pattern search finds look-alikes; it does not show what the change touches. Trace the real code **before** Design decomposes anything. This step is required in every mode and does not depend on the pattern confidence from Step 1.

For each Source Inventory item (or each Success Criterion when `source: prompt`):

1. **Locate the touch points by symbol, not by keyword.** Search for the exact types, functions, assets or config keys the item names or implies, then open each hit and read the relevant region. Do not infer a file's role from its name.
2. **Record, with `path` (and line when useful):**
   - **Touches:** existing files the item must change, and the call sites that must feed or consume the new behavior (e.g. where damage is applied, where an entity dies, where input is bound, where state is saved).
   - **Layer and allowed direction:** the module or layer each file belongs to and which layers may depend on which, read from the architecture document or the build files (module dependency lists, workspace manifests, import rules, lint rules). State the rule you found and where.
   - **Overlaps:** existing types or files with the same job as something the item introduces (name both and their relation: replace, wrap, or coexist).
   - **Data and content files:** schemas, assets, generated or binary files, baked or imported data, and config the item changes. Note how they may be edited (tooling, locks, regeneration) when the project says so.
   - **Source file lists:** where the source names files, check each exists (to be modified) or not (to be created) and record every discrepancy.
3. **Mark gaps honestly.** A touch point you could not find is recorded as `not found`; Design turns it into an Open Decision. Never fill it with a plausible guess.
4. **Keep it a table of facts** (`item | touches | layer | overlaps | data/content | discrepancies`); no design opinions here.

Output: the `Codebase Trace` section of the Research Findings Artifact.

### Step 2: High-Risk Area Detection

1. **Nominate:** scan the task description and scoped context for high-risk keywords across six areas: Security, Payments, APIs, Migrations, Complex Logic, and Infrastructure.
2. **Confirm or dismiss every candidate** by the real consequence of failure, with one line of cited evidence (a file, a requirement quote, or a named external system). A keyword hit alone (e.g., "transaction" for an in-process state change, "session" for a game session) is dismissed, not counted.
3. **Assign `risk_level` from the confirmed areas only.** Critical needs cited evidence of real consequence; without it, dismiss or downgrade.
4. Record all candidates with `confirmed`/`dismissed` and the reason in `High-Risk Detection`.

For the keyword table, confirmation rules, and the risk-level logic, see **[high-risk-detection.md](../references/high-risk-detection.md)**.

### Step 3: External Research Decision

1. Look up the external-research decision in the **risk × patterns matrix** in [high-risk-detection.md](../references/high-risk-detection.md) ("Mapping to Research Decision") using the detected **risk level** (Step 2) and the **patterns found count** (Step 1).
2. If the matrix returns "Recommend external": provide specific web search guidance (Step 4). If it returns "Skip external", record `External Research: skipped` and proceed to Step 5.
3. If it returns "Optional external": provide guidance only when interaction is detailed/smart or risk is HIGH/CRITICAL.

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

1. **Assign a `research-id`** per [id-generation.md](../references/id-generation.md) (format `YYYY-MM-DD-NNN-research`, saved to `docs/plans/.research/`). Reuse it if the user later picks **Edit & Retry**.

2. Produce a **Research Findings Artifact** block (as markdown) following the schema in [research-findings.md](../references/templates/artifacts/research-findings.md):
   - Include the generated `research-id` and the inherited `scope-id`.
   - Include the `Codebase Trace` from Step 1b.
   - Write a 2–3 sentence **Findings Summary** overview of the Patterns Found, risk level, and constraints.

### Step 7: Present, Confirm, and Save

Apply the **[phase confirmation behavior](../references/interaction-mode-propagation.md)** for the current `interactionMode`, using these research-specific **Smart pause triggers**:

- Confirmed risk level is HIGH or CRITICAL **and** fewer than 3 patterns found (external research recommended), or
- Zero patterns found in the codebase, or
- The Codebase Trace has a `not found` touch point or a source file-list discrepancy that affects 3+ source items.

- **Detailed:** present the Research Findings Artifact and ask one question with options *(1) Proceed to Design, (2) Edit & Retry, (3) Abort*. On **Edit & Retry**, loop back through Steps 1–6 reusing the `research-id`. On **Abort**, stop and inform the Orchestrator.
- **Smart:** pause only when a pause trigger above is true; otherwise auto-proceed.
- **Autopilot:** auto-proceed (no confirmation).

On any proceed/skip path: in `detailed` mode only, save the artifact to `docs/plans/.research/<research-id>.md` (ensure `interactionMode` is included), then return the artifact and `interactionMode` to the Orchestrator for the transition to Phase 3 (Design). In `smart` and `autopilot` mode, do **not** write the file; pass the artifact to the next phase in context (see [Artifact Persistence](../references/interaction-mode-propagation.md#artifact-persistence)).

## Output: Research Findings Artifact

- Verify that the Research Findings Artifact is complete and valid, containing all required fields, and it accurately reflects the user's input and any existing plans, learnings, or requirements found.
- Verify that the `Codebase Trace` has a row for every Source Inventory item, that each cited path was opened (not inferred), and that every `not found` is listed for Design.
- Verify that the `interactionMode` value is set correctly based on the user's selection in the Orchestrator skill.
- Verify that, in `detailed` mode, the artifact is saved to `docs/plans/.research/<research-id>.md`; in `smart`/`autopilot` mode, verify that **no** file was written and the artifact was passed to the next phase in context.

> Pass the research findings to `design` (Phase 3) for the design phase.
