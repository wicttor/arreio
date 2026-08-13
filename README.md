---
Title: Arreio
Type: Documentation
---

**Arreio** (Brazilian word for _harness_) transforms agentic coding workflows into a predictable, safe, and high-quality software delivery pipeline.

By enforcing a **pragmatic**, guardrailed execution, Arreio brings structure to AI-driven development. Master just four core phases to orchestrate a highly reliable development cycle:

**Plan → Work → Review → Learn**

## Skill Based Workflow

**Arreio** orchestrates work through predictable skills that run in sequence:

Use /arreio-init to initialize a new project, to enable the project to follow the four phases of the Arreio workflows.

### Plan

| Phase | Module Name  | Purpose                                   |
| ----- | ------------ | ----------------------------------------- |
| 1     | **scope**    | Gather context, validate domain           |
| 2     | **research** | Discover patterns, detect high-risk areas |
| 3     | **design**   | Decompose into implementation units       |
| 4     | **generate** | Select tier, render plan, save to docs    |
| 5     | **tasks**    | Slice plan into executable tasks          |

### Work

| Phase | Module Name | Purpose                                   |
| ----- | ----------- | ----------------------------------------- |
| 1     | **triage**  | Classify input and extract context        |
| 2     | **prepare** | Set up environment, move task to progress |
| 3     | **execute** | Implement with test-first discipline      |
| 4     | **review**  | Code review, quality gates, move to done  |

### Review

| Phase | Module Name | Purpose                          |
| ----- | ----------- | -------------------------------- |
| 1     | **scope**   | Classify input and scope review  |
| 2     | **prepare** | Set up review environment        |
| 3     | **analyze** | Execute code review, find issues |
| 4     | **report**  | Report verdict                   |

### Learn

| Phase | Module Name  | Purpose                             |
| ----- | ------------ | ----------------------------------- |
| 1     | **capture**  | Extract and capture knowledge entry |
| 2     | **refine**   | Curate and refine the entry         |
| 3     | **index**    | Catalog and index the entry         |
| 4     | **maintain** | Dedup, refresh, and prune entries   |

### Supporting Skills

We have designed a set of supporting skills to help you to manage your repository and work.

#### /arreio-init

Initialize a new project, enabling the project to follow the four phases of the Arreio workflows

#### /end-session

Preserve session context with a well-documented commit capturing state, decisions, and next steps.
