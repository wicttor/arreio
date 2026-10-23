# Knowledge Index

The project's durable knowledge base. Source of truth for decisions, patterns,
gotchas, and workflows. Plan/Work/Review search this index via the YAML block.

**Last updated:** 2026-10-23T08:05:00Z

## Entries

```yaml
entries:
  - filename: docs/learn/decision/use-pnpm-when-both-lockfiles-exist.md
    domain: tooling
    tags: [package-management, npm, pnpm, lockfiles]
    applicability: RECOMMENDED
    summary: Prefer the lockfile named by package.json's packageManager field when both lockfiles exist.
  - filename: docs/learn/gotcha/redis-ttl-set-vs-expire.md
    domain: data-storage
    tags: [redis, ttl, session-store, caching]
    applicability: RECOMMENDED
    summary: Pass the TTL on SET ... EX; a separate EXPIRE is lost when the key is overwritten.
  - filename: docs/learn/pattern/atomic-config-write.md
    domain: file-io
    tags: [config, filesystem, durability]
    applicability: CONTEXTUAL
    summary: Write config to a temp file in the same directory, then rename it over the target.
  - filename: docs/learn/workflow/bump-version-with-every-commit.md
    domain: release
    tags: [versioning, changelog]
    applicability: HISTORICAL
    summary: Every commit bumps package.json and adds CHANGELOG notes.
  - filename: docs/learn/workflow/bump-version-with-every-commit.md
    domain: release
    tags: [versioning, changelog]
    applicability: HISTORICAL
    summary: Every commit bumps package.json and adds CHANGELOG notes.
```

## By Category

### Decision (1)

| File | Title | Domain | Applicability |
|------|-------|--------|---------------|
| [use-pnpm-when-both-lockfiles-exist.md](decision/use-pnpm-when-both-lockfiles-exist.md) | Use pnpm When Both Lockfiles Exist | tooling | RECOMMENDED |

### Pattern (2)

| File | Title | Domain | Applicability |
|------|-------|--------|---------------|
| [atomic-config-write.md](pattern/atomic-config-write.md) | Atomic Config Write | file-io | CONTEXTUAL |

### Gotcha (1)

| File | Title | Domain | Applicability |
|------|-------|--------|---------------|
| [redis-ttl-set-vs-expire.md](gotcha/redis-ttl-set-vs-expire.md) | Redis TTL Must Propagate to the SET Command | data-storage | DIRECT |

### Workflow (1)

| File | Title | Domain | Applicability |
|------|-------|--------|---------------|
| [bump-version-with-every-commit.md](workflow/bump-version-with-every-commit.md) | Bump Version With Every Commit | release | HISTORICAL |

## By Domain

- **tooling:** use-pnpm-when-both-lockfiles-exist
- **data-storage:** redis-ttl-set-vs-expire
- **file-io:** atomic-config-write
