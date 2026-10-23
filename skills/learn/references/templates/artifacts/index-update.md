---
title: Index Update Artifact
description: Template for the Index Update Artifact produced by the Index phase. Carries the entry-path, the resolved slug, the derived index-applicability enum, the index-action (created/updated/merged), the index-coherence flag, and any merge de-index performed. The authoring run's final artifact; the entry is now durable at docs/learn/<type>/<slug>.md and indexed in docs/learn/index.md.
type: template
version: 1.0
timestamp: "2026-08-08"
---

# Index Update Artifact

The product of the **Index** phase is the authoring run's final artifact. Index **writes** the entry file at `docs/learn/<type>/<slug>.md` (upsert on `slug`), derives the index-record `applicability` enum from the per-entry numeric scores per [index-format.md](../../index-format.md), and **upserts** `docs/learn/index.md` (YAML `entries:` block record plus By Category / By Domain markdown rows). On a merge resolution, Index de-indexes the analog (removes its index record), writes `superseded-by` into the analog's file, and adds the analog's `slug` to the canonical's `related` — keeping the analog's file (lineage preserved, never deleted). Index is the only authoring-phase writer of the entry file and the index.

## Schema

```yaml
index-id: YYYY-MM-DD-NNN-index
refine-id: YYYY-MM-DD-NNN-refine
capture-id: YYYY-MM-DD-NNN-capture
learn-id: YYYY-MM-DD-NNN
input-shape: explicit | candidate
interactionMode: detailed | smart | autopilot
status: complete
timestamp: ISO-8601 timestamp

entry-path: "docs/learn/<type>/<slug>.md"      # where the entry file was written
slug: "<resolved-slug>"                       # the upsert key (matches the entry's frontmatter slug)
type: decision | pattern | gotcha | workflow  # the entry's type

index-applicability: DIRECT | RECOMMENDED | CONTEXTUAL | HISTORICAL | INFORMATIONAL
                                              # DERIVED per index-format.md from the frontmatter's numeric scores

index-action: created | updated | merged      # what Index did
                                              # created: new slug written
                                              # updated: existing slug overwritten (update-existing resolution)
                                              # merged: merge-into-canonical — the existing canonical entry rewritten with the draft folded in; no new file

merge:                                        # present ONLY when index-action == merged
  canonical-slug: <the existing entry that was rewritten>
  also-seen-in-added: "<the draft's source.reference>"   # appended to the canonical's also-seen-in
  tags-after: [tag-1, ...]                     # the canonical's tags after the union (cap 6)
  new-file-written: false                      # always false: the draft never becomes a file

index-coherent: true                          # check-learn.py printed PASS: the YAML entries: length == active entry-file count;
                                              # per-type (N) counts consistent; no duplicate rows; the orchestrator's gate #5

source-candidate: <carried through> | null

entry-written: true                           # the entry file was written (false only on a failed-write recovery; would be status: failed)
index-updated: true                           # docs/learn/index.md was upserted
```

In `detailed` mode only, also save the Index Update Artifact to `docs/learn/.index/<index-id>.md`. In `smart`/`autopilot` mode, do not write it; pass it to the next phase in context.

## Validation Rules

- **index-id:** Required. Format `YYYY-MM-DD-NNN-index` per [id-generation.md](../../id-generation.md).
- **refine-id, capture-id, learn-id, input-shape:** Required, inherited (cross-phase consistency).
- **interactionMode:** Required, identical across the authoring chain.
- **status:** Required. `complete`.
- **entry-path:** Required. Repo-relative, of the form `docs/learn/<type>/<slug>.md`; the directory `docs/learn/<type>/` created if missing.
- **slug:** Required. The resolved slug (matches the entry's frontmatter).
- **type:** Required. One of the four.
- **index-applicability:** Required. The **derived** enum, per [index-format.md](../../index-format.md) (not re-encoded inline here; the artifact records the result of applying the derivation rule to the frontmatter's numeric scores).
- **index-action:** Required. `created` (new slug), `updated` (existing slug overwritten via `update-existing`), or `merged` (`merge-into-canonical` executed).
- **merge:** Required when `index-action: merged`; absent otherwise. On a merge:
  - `also-seen-in-added` — the draft's reference was appended to the canonical entry's `also-seen-in`.
  - `new-file-written: false` — a Refine-time merge never creates a file and never de-indexes anything.
  - No file is deleted (lineage preservation per [dedup-rules.md](../../dedup-rules.md)).
- **index-coherent:** Required. `true` — the post-upsert invariants hold (YAML length == active entry-file count; per-type counts consistent; no duplicate rows). If `false`, Index reconciled in-place (non-destructive) and flagged it; the orchestrator's quality gate #5 requires `true` to finalize the run.
- **entry-written, index-updated:** Required. `true` on success; `status: failed` would cover a write failure.

## Example (created — new decision entry)

```yaml
index-id: 2026-08-08-001-index
refine-id: 2026-08-08-001-refine
capture-id: 2026-08-08-001-capture
learn-id: 2026-08-08-001
input-shape: explicit
interactionMode: smart
status: complete
timestamp: 2026-08-08T14:34:00Z
entry-path: docs/learn/decision/use-pnpm-when-both-lockfiles-exist.md
slug: use-pnpm-when-both-lockfiles-exist
type: decision
index-applicability: DIRECT                  # current_project=8, general=6 → RECOMMENDED; refine higher if any
index-action: created
index-coherent: true
source-candidate: null
entry-written: true
index-updated: true
```

## Example (merged — canonical updated, draft folded in)

```yaml
index-id: 2026-08-08-002-index
refine-id: 2026-08-08-002-refine
capture-id: 2026-08-08-002-capture
learn-id: 2026-08-08-002
input-shape: candidate
interactionMode: smart
status: complete
timestamp: 2026-08-08T14:42:00Z
entry-path: docs/learn/gotcha/redis-ttl-set-vs-expire.md
slug: redis-ttl-set-vs-expire
type: gotcha
index-applicability: DIRECT                  # current_project=8, general=7 → DIRECT
index-action: merged
merge:
  canonical-slug: redis-ttl-set-vs-expire
  also-seen-in-added: "2026-07-10-001-review#2026-07-10-001-T02a:green"
  tags-after: [redis, ttl, session-store, caching]
  new-file-written: false
index-coherent: true
source-candidate:
  title: "Redis TTL must be propagated to the SET command"
  domain: data-storage
  key: "2026-07-10-001-review#2026-07-10-001-T02a:green"
  summary: "TTL test failed because SET ... EX must carry the TTL."
  type: gotcha
entry-written: true
index-updated: true
```

## Notes

- Index is the **sole authoring-phase writer** of the entry file and the index; the upsert on `slug` is idempotent (a re-author overwrites, never duplicates).
- The `index-applicability` enum is **derived** from the frontmatter's numeric scores per [index-format.md](../../index-format.md); the artifact records the **result** of that derivation — it does not re-encode the derivation rule (no second formula).
- A `merged` action rewrites the existing canonical entry only. Base-wide merges of two existing entries (which de-index the analog and keep its file with `superseded-by`) are Maintain's, recorded in the Maintain Log.
- `index-coherent: true` is the orchestrator's quality gate #5; the Index phase is responsible for leaving the index coherent (the YAML block, the per-type `(N)` counts, and the By Domain bullets are all in lockstep with the on-disk file tree).
- This artifact is the authoring run's **final** output. The Orchestrator marks the run complete; the durable knowledge entry now lives at `entry-path` and is discoverable via `docs/learn/index.md` (the source-of-truth index Plan/Work/Review search).