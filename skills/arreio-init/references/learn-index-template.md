---
title: Learn Index Template
description: Seed for docs/learn/index.md. Matches the empty index seed that the learn skill defines in learn/references/index-format.md, so the first /learn run upserts into a file it can parse.
type: Template
version: 1.1
timestamp: "2026-10-23"
---

# Learn Index Template

Write this to `docs/learn/index.md` when it does not exist, replacing `<ISO-8601>` with the current UTC time. The `entries: []` block is valid and empty; the learn skill's first upsert turns it into a block list. The canonical definition is [index-format.md](../../learn/references/index-format.md#empty-index-seed); keep the two identical.

````markdown
# Knowledge Index

The project's durable knowledge base. Source of truth for decisions, patterns,
gotchas, and workflows. Plan/Work/Review search this index via the YAML block.

**Last updated:** <ISO-8601>

## Entries

```yaml
entries: []
```

## By Category

### Decision (0)

### Pattern (0)

### Gotcha (0)

### Workflow (0)

## By Domain
````
