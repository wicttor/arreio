**Arreio** (Brazilian word for _harness_) transforms agentic coding workflows into a predictable, safe, and high-quality software delivery pipeline.

By enforcing a **pragmatic**, guardrailed execution, Arreio brings structure to AI-driven development. Master just four core phases to orchestrate a highly reliable development cycle:

**Plan → Work → Review → Learn**

## Installation

Install Arreio as a dependency to enable all skills in your workspace:

```bash
npm install arreio
```

The post-install script will automatically copy all Arreio skills to your `~/.agents/skills/` directory, making them available in VS Code Copilot Chat. (Note: npm may show an advisory about unallowed install scripts—this is informational and won't block the installation.)

Then initialize your project to set up the Arreio folder structure and documentation:

```
/arreio-init
```

Run this command in VS Code Copilot Chat to:

1. Verify or manually install Arreio skills to `~/.agents/skills/` (if postinstall was skipped)
2. Create the project structure (`docs/plans/`, `docs/learn/`, etc.)
3. Set up architectural documentation and index files

This makes all five core skills available in your AI development environment:

- **arreio-init** - Initialize projects to follow the Arreio workflow
- **plan** - Structure and decompose work into executable tasks
- **work** - Execute tasks with guardrailed implementation
- **review** - Conduct comprehensive code reviews
- **learn** - Capture and refine knowledge from completed work

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

Preserve session context with a well-documented commit capturing state, decisions, and next steps — saved as a traceable session artifact (with agent attribution) in `docs/plans/.end-session/`.
