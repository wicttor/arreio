**Arreio** (Brazilian word for _harness_) transforms agentic coding workflows into a predictable, safe, and high-quality software delivery pipeline.

By enforcing a **pragmatic**, guardrailed execution, Arreio brings structure to AI-driven development. Master just four core phases to orchestrate a highly reliable development cycle:

**Plan → Work → Review → Learn**

## Installation

Install Arreio as a dependency to enable all skills in your workspace:

```bash
npm install arreio
```

The post-install script will automatically copy all Arreio skills to your project's `.agents/skills/` directory, making them available to your AI coding agent.

> **Note on npm 10+ install scripts:** npm 10+ blocks lifecycle scripts by default and will print a warning like `npm warn install-scripts arreio@x.y.z (postinstall: ...)`. The script is not run automatically until you allow it. Run:
>
> ```bash
> npm install-scripts approve arreio
> ```
>
> If you skip the postinstall, run `/arreio-init` in your AI coding agent — it will install the skills for you.

Then initialize your project to set up the Arreio folder structure and documentation:

```
/arreio-init
```

Run this command in your AI coding agent to:

1. Verify or manually install Arreio skills to `.agents/skills/` (if postinstall was skipped)
2. Create the project structure (`docs/plans/`, `docs/learn/`, etc.)
3. Set up architectural documentation and index files

This makes all six skills available in your AI development environment:

- **arreio-init** - Initialize projects to follow the Arreio workflow
- **plan** - Structure and decompose work into executable tasks
- **work** - Execute tasks with guardrailed implementation
- **review** - Conduct comprehensive code reviews
- **learn** - Capture and refine knowledge from completed work
- **end-session** - Commit the session with a traceable session artifact

## Quick Start

```text
/plan [--deep] Add Redis-backed session storage      # produce a plan (+ optional task files)
/work <plan-id>                                      # execute the plan's tasks, test-first
/review <work-id | git range | description>          # review the changes, get a verdict
/learn <candidate-ref | decision "text">             # keep what the team learned
```

Each skill is invoked by prompt (`/plan`, `/work`, `/review`, `/learn`) and first asks you to choose an interaction mode.

## Skill Based Workflow

**Arreio** orchestrates work through predictable skills that run in sequence:

Use /arreio-init to initialize a new project, to enable the project to follow the four phases of the Arreio workflows.

### Interaction Modes

Every pipeline asks for an interaction mode before it starts:

| Mode          | Behavior                                                                         |
| ------------- | -------------------------------------------------------------------------------- |
| **Detailed**  | Confirm at each phase transition; inspect every artifact. Maximum control.       |
| **Smart**     | Phases run automatically; pause only on risky, destructive, or ambiguous events. |
| **Autopilot** | Phases run automatically; only the final outcome is reported.                    |

Intermediate phase artifacts (scope, research, triage, analyze, etc.) are written to hidden folders **only in Detailed mode**; in Smart/Autopilot they are passed in context. Final deliverables (plans, tasks, reports, learn entries) are always written.

### Plan

Invoke with `/plan [--deep] <task description>`.

| Phase | Module Name  | Purpose                                   |
| ----- | ------------ | ----------------------------------------- |
| 1     | **scope**    | Gather context, validate domain           |
| 2     | **research** | Discover patterns, detect high-risk areas |
| 3     | **design**   | Decompose into implementation units       |
| 4     | **generate** | Select tier, render plan, save to docs    |
| 5     | **tasks**    | Slice plan into executable tasks          |

**Plan tiers.** The Generate phase right-sizes the plan: **Fast** (trivial/low complexity), **Standard** (medium), or **Deep** (high/very high complexity, with alternatives and rollout notes). The tier comes from a complexity score (five dimensions, 0–15) combined with the detected risk level; high risk raises the minimum tier. Choosing `Auto` uses the computed recommendation, which is recorded as `tier_recommended`.

**`--deep`.** Put `--deep` at the start or end of the input to force a Deep plan in any interaction mode (including Autopilot), without the tier question. The algorithm's own recommendation is still recorded in `tier_recommended`, so the override is auditable.

Plan outputs: `docs/plans/YYYY-MM-DD-NNN-<name>.md` (indexed in `docs/plans/index.md`) and, optionally, one task file per acceptance criterion in `docs/tasks/<plan-id>/`.

### Work

Invoke with `/work <plan-id>`, `/work <task file or task-id>`, or `/work <task description>` (ad-hoc). Work runs on its own `work/<short-description>` git branch, executes each task Red → Green → Refactor, and chooses an **execution mode** (inline, serial, or parallel waves) from task priority, risk, and dependencies; HIGH-risk tasks always run inline.

| Phase | Module Name | Purpose                                   |
| ----- | ----------- | ----------------------------------------- |
| 1     | **triage**  | Classify input and extract context        |
| 2     | **prepare** | Set up environment, move task to progress |
| 3     | **execute** | Implement with test-first discipline      |
| 4     | **review**  | Code review, quality gates, move to done  |

### Review

Invoke with `/review <git range | HEAD | branch | paths>`, `/review <work-id>`, or `/review <target description>`. Findings are graded `blocker` / `major` / `minor` / `nit` across quality, security, tests, documentation, integration, and scope creep, and the approval status (`approved` / `changes-requested` / `rejected`) is derived from the findings. Review is local and read-only: reports are written to `docs/review/`, never posted to GitHub.

| Phase | Module Name | Purpose                          |
| ----- | ----------- | -------------------------------- |
| 1     | **scope**   | Classify input and scope review  |
| 2     | **prepare** | Set up review environment        |
| 3     | **analyze** | Execute code review, find issues |
| 4     | **report**  | Derive approval, write report    |

### Learn

| Phase | Module Name  | Purpose                             |
| ----- | ------------ | ----------------------------------- |
| 1     | **capture**  | Extract and capture knowledge entry |
| 2     | **refine**   | Curate and refine the entry         |
| 3     | **index**    | Catalog and index the entry         |
| 4     | **maintain** | Dedup, refresh, and prune entries   |

Invoke with `/learn <decision|pattern|gotcha|workflow> <text>`, `/learn <candidate-ref>` (a Work or Review `learnings-to-capture` item), or `/learn maintain`. Entries live in `docs/learn/<type>/`, are indexed in `docs/learn/index.md`, and are searched by Plan, Work, and Review.

### Project Structure

After `/arreio-init`, generated artifacts live under `docs/`:

```text
docs/
  plans/   final plans + index.md   (hidden .scope/.research/.design/ in Detailed mode)
  tasks/   <plan-id>/ task files + index.md
  learn/   decision/ pattern/ gotcha/ workflow/ + index.md
  review/  index.md + .report/      (other hidden phase folders in Detailed mode)
  archives/
```

Whether to commit `docs/` is your choice; this repository ignores it.

### Supporting Skills

We have designed a set of supporting skills to help you to manage your repository and work.

#### /arreio-init

Initialize a new project, enabling the project to follow the four phases of the Arreio workflows

#### /end-session

Preserve session context with a well-documented commit capturing state, decisions, and next steps — saved as a traceable session artifact (with agent attribution) in `docs/plans/.end-session/`.
