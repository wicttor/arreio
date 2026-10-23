---
title: Refined Entry Artifact
description: Template for the Refined Entry Artifact produced by the Refine phase. Carries the validated entry (frontmatter + body conforming to entry-schema), the resolved slug (may differ from Capture's proposal after a conflict), the dup-status (exact/analog/none) + the chosen resolution, and a lineage block when a merge occurred; consumed by Index.
type: template
version: 1.0
timestamp: "2026-08-08"
---

# Refined Entry Artifact

The product of the **Refine** phase is a validated, conflict-resolved entry: frontmatter and body conforming to the authoritative [entry-schema.md](../../entry-schema.md) (which Refine validates against, never re-encodes), the **resolved** `slug` (may differ from Capture's proposal after a duplicate/analog conflict), the `dup-status` + `resolution` chosen by the user, and a `lineage` block when a merge occurred. Index consumes it to write the entry file and upsert the index. Refine validates and reconciles; it does not write.

## Schema

```yaml
refine-id: YYYY-MM-DD-NNN-refine
capture-id: YYYY-MM-DD-NNN-capture
learn-id: YYYY-MM-DD-NNN
input-shape: explicit | candidate
interactionMode: detailed | smart | autopilot
status: complete
timestamp: ISO-8601 timestamp

type: decision | pattern | gotcha | workflow    # validated
slug: "<resolved-kebab-case-slug>"             # validated; may differ from Capture's proposal (new-slug case)

frontmatter:                                   # validated per entry-schema.md; Refine does not coerce silently
  type: <same as type>
  slug: <same as slug>
  domain: <primary-domain>
  priority: important | normal
  applicability: { current_project: <0-10>, general: <0-10> }
  tags: [tag-1, ..., tag-6]                     # 2-6 tags validated
  summary: <1-2 sentences>                      # validated: non-empty, <= 240 characters
  created_at: ISO-8601                          # preserved from Capture
  updated_at: ISO-8601                          # stamp of Refine's validation
  source: { type, reference, extracted_at }
  confidence: high | medium | low

body: |                                         # per-type section template validated present (Refine does not auto-fill)
  # <Title>

  ## Problem
  ...
  ## ... remaining sections for the type ...

dup-status: exact | analog | none               # the ref result of Refine Step 3 against existing entries
matched-slug: <existing-slug> | null            # the entry Refine matched (exact or analog); null when none
match-evidence: | null                          # the shared signals (slug match, or domain+tags+type+conclusion)
resolution: update-existing | new-slug | merge-into-canonical | keep-separate | none
                                               # chosen by the user per dedup-rules.md; none when dup-status==none

lineage:                                        # set ONLY when resolution == merge-into-canonical
  merged-into: <existing canonical slug>        # the existing entry is the canonical one; same as `slug` above
  also-seen-in-added: <source.reference>        # the draft's reference, appended to the canonical's also-seen-in
  rationale: "<why merge, in one line>"

preserved:                                      # set ONLY for update-existing / revive: carried over from the existing file
  created_at: ISO-8601
  related: [<slug>, ...]
  migrated-from: <path> | null
  also-seen-in: [<source.reference>, ...]

source-candidate: <carried from Capture> | null
```

In `detailed` mode only, also save the Refined Entry Artifact to `docs/learn/.refine/<refine-id>.md`. In `smart`/`autopilot` mode, do not write it; pass it to the next phase in context.

## Validation Rules

- **refine-id:** Required. Format `YYYY-MM-DD-NNN-refine` per [id-generation.md](../../id-generation.md).
- **capture-id, learn-id, input-shape:** Required, inherited from Capture (cross-phase consistency).
- **interactionMode:** Required, identical to the Capture artifact.
- **status:** Required. `complete`.
- **type:** Required. One of the four (re-confirmed by Refine Step 1).
- **slug:** Required. The **resolved** slug; kebab-case; globally unique (Refine confirmed no exact collision unless `resolution: new-slug`/`update-existing`).
- **frontmatter:** Required. Every required field validated per [entry-schema.md](../../entry-schema.md); `tags` length 2–6; numeric scores 0–10; `confidence`/`priority` in enums; `created_at` preserved, `updated_at` stamped.
- **body:** Required. The per-type section template present in full (Refine flagged any missing section as a pause trigger; auto-fill is forbidden).
- **dup-status:** Required. `exact`, `analog`, or `none`.
- **matched-slug:** Required (= the existing slug) when `dup-status` is `exact` or `analog`; `null` when `none`.
- **match-evidence:** Required when `dup-status` is `exact` or `analog`; the shared signals (slug match, or domain+tags+type+conclusion overlap) so the user can confirm the match is real.
- **resolution:** Required. Must be one of `update-existing`, `new-slug`, `merge-into-canonical`, `keep-separate`, `none`; `none` only when `dup-status: none`.
- **lineage:** Required when `resolution: merge-into-canonical` (`merged-into`, `also-seen-in-added`, `rationale`); absent otherwise. No file is created, deleted or de-indexed by a Refine-time merge.
- **preserved:** Required when `resolution: update-existing` (or a revive of an obsolete entry); absent otherwise.
- **source-candidate:** Carried through from Capture (setter of the entry's `source.reference` traceability).

## Example (explicit decision, no duplicate)

```yaml
refine-id: 2026-08-08-001-refine
capture-id: 2026-08-08-001-capture
learn-id: 2026-08-08-001
input-shape: explicit
interactionMode: smart
status: complete
timestamp: 2026-08-08T14:32:00Z
type: decision
slug: use-pnpm-when-both-lockfiles-exist
frontmatter:
  type: decision
  slug: use-pnpm-when-both-lockfiles-exist
  domain: tooling
  priority: normal
  applicability: { current_project: 8, general: 6 }
  tags: [package-management, npm, pnpm, lockfiles]
  created_at: 2026-08-08T14:30:00Z
  updated_at: 2026-08-08T14:32:00Z
  source: { type: commit, reference: "1ee04e2", extracted_at: 2026-08-08T14:30:00Z }
  confidence: high
body: |
  # Use pnpm When Both Lockfiles Exist
  ## Problem
  ...
  ## Solution
  ...
dup-status: none
matched-slug: null
match-evidence: null
resolution: none
source-candidate: null
```

## Example (analog → merge-into-canonical, the existing entry is the canonical)

```yaml
refine-id: 2026-08-08-002-refine
capture-id: 2026-08-08-002-capture
learn-id: 2026-08-08-002
input-shape: candidate
interactionMode: smart
status: complete
timestamp: 2026-08-08T14:40:00Z
type: gotcha
slug: redis-ttl-set-vs-expire             # the EXISTING entry's slug; the draft never becomes a file
frontmatter:
  type: gotcha
  slug: redis-ttl-set-vs-expire
  domain: data-storage
  priority: important
  applicability: { current_project: 8, general: 7 }
  tags: [redis, ttl, session-store, caching]
  summary: Pass the TTL on SET ... EX; a separate EXPIRE is lost when the key is overwritten.
  created_at: 2026-07-10T00:00:00Z         # the existing entry's, preserved
  updated_at: 2026-08-08T14:40:00Z
  source: { type: commit, reference: "9f3c2ab", extracted_at: 2026-07-10T00:00:00Z }
  also-seen-in: ["2026-07-10-001-review#2026-07-10-001-T02a:green"]
  confidence: medium
body: |
  # Redis TTL Must Propagate to the SET Command
  ## Problem
  ...
  ## Trap / Solution / Prevention / Source ...  (the draft's evidence consolidated into the existing sections)
dup-status: analog
matched-slug: redis-ttl-set-vs-expire
match-evidence: |
  same domain (data-storage) + 3 shared tags (redis, ttl, session-store) + same type (gotcha)
  + same conclusion (SET ... EX must carry the TTL); different proposed slug.
resolution: merge-into-canonical
lineage:
  merged-into: redis-ttl-set-vs-expire
  also-seen-in-added: "2026-07-10-001-review#2026-07-10-001-T02a:green"
  rationale: "Same gotcha, same prevention; the new evidence is folded into the existing entry."
source-candidate:
  key: "2026-07-10-001-review#2026-07-10-001-T02a:green"
  title: "Redis TTL must be propagated to the SET command"
  domain: data-storage
  summary: "TTL test failed because SET ... EX must carry the TTL."
  type: gotcha
```

## Notes

- Refine is the **validator + conflict resolver**; it does not write the entry file (Index does) and does not coerce frontmatter silently (a wrong field surfaces as a pause trigger, never a silent fix).
- The `slug` here is the **resolved** slug — it may differ from Capture's proposal only when a conflict chose `new-slug` (Capture proposed → existing collision → user renamed) or `update-existing` (Capture proposed → existing match → keep existing slug).
- The `lineage` block is the **single** place the merge's bookkeeping lives at Refine-time; Index reads it to rewrite the canonical entry with the folded body, tags and `also-seen-in`. Refine may not authorize deletion or de-indexing; those belong to Maintain (per [dedup-rules.md](../../dedup-rules.md)).
- `created_at` on a merge or an `update-existing` is the **existing** entry's timestamp (see `preserved`); `updated_at` stamps the change. This preserves chronology across the absorption.