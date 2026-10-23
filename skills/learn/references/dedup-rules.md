---
title: Dedup Rules
description: Authoritative reference for Refine (per-entry dup/analog check) and Maintain (base-wide dedup). Defines what counts as an exact duplicate vs an analog (clearly distinct from exact), the matching signals, the resolution options (update-existing / new-slug / merge-into-canonical / keep-separate), and the lineage-preserving merge procedure — de-index the analog, keep its file with superseded-by, never delete.
type: reference
version: 1.0
timestamp: "2026-08-08"
---

# Dedup Rules

Authoritative reference for the **Refine** phase (per-entry duplicate+analog check) and the **Maintain** phase (base-wide dedup). Defines what counts as an **exact duplicate** vs an **analog** (a distinct category), the matching signals, the resolution options, and the **lineage-preserving merge procedure** — de-index the analog, keep its file with a `superseded-by` note, never delete. Refine and Maintain apply this reference; they do not re-encode it.

## Core Principle

> **Decisions don't duplicate, but analogs exist.** An exact duplicate (same `slug`) means a re-author; the user updates the existing entry or picks a new `slug`. An analog (same conclusion about the same domain, different `slug`) is a dedup candidate: merging the analog into the canonical entry **preserves lineage** — the analog is de-indexed (its index record removed, its file kept with a `superseded-by` note), never deleted. This is why dedup **merges**, never **deletes**: knowledge is rarely destroyed, it is superseded and absorbed. A merged or migrated entry carries both the old and new knowledge, not just the new.

## Matching Categories

| Match      | Definition                                                                                       | Detection signals (authoritative)                                            |
| ---------- | ------------------------------------------------------------------------------------------------ | ---------------------------------------------------------------------------- |
| `exact`    | An existing entry with the same `slug` (case-insensitive, hyphen-normalized), or the same canonicalized title. | Identical `slug`; or kebab-case(title) matches slug. |
| `analog`   | An existing entry addressing the **same conclusion** on the **same domain** with overlapping `tags`, under a different `slug`. | Same `domain` + ≥2 overlapping `tags` + same `type` + semantically same Problem/Solution. |
| `insignificant` | Loose/distant matches: same `domain` only, or one overlapping tag, or a different `type` on a related topic. | Same `domain` with ≤1 overlapping `tags`; or different `type` (a decision about caching is not an analog of a gotcha about caching). |

**The matching algorithm** (run by Refine on the new draft; by Maintain on all pairs):

```
1. Canonicalize the candidate's slug and title (kebab-case, lowercase, hyphen-collapsed).
2. For each existing entry in docs/learn/<type>/ (and cross-type — slug namespace is global;
   entries marked obsolete or superseded still hold their slug):
   - if slug matches (hyphen-normalized, case-insensitive) -> EXACT
3. Else, for each ACTIVE existing entry of the same type and domain (a bucket, never all pairs):
   - compute overlap: domain-strict-match + (shared-tags count) + same-type
   - if same domain AND >=2 shared tags AND same type:
       read both bodies' Problem/Solution; if semantically the same conclusion -> ANALOG
   - else -> INSIGNIFICANT (ignore; not a dedup candidate)
4. Record the matches with evidence (the shared signals + the matched slug).
```

Only `exact` and `analogs` surface for resolution; `insignificant` matches are ignored (no dedup, no pause).

## Resolution Options (the user picks)

### exact

A re-author of the same `slug`. Two options (a third applies when the existing entry is obsolete, see Edge Cases):

| Option            | Action                                                                                       |
| ----------------- | --------------------------------------------------------------------------------------------- |
| **update-existing** | Overwrite the existing entry file at `docs/learn/<type>/<slug>.md` with the refined content; upsert its index record (idempotent on `slug`); bump `updated_at`. **Carry over from the existing file:** `created_at`, `related`, `migrated-from`, `also-seen-in`, and its `source` (when the new draft's `source.reference` differs, append it to `also-seen-in`). The canonical way to revise a decision. |
| **new-slug**        | Pick a different `slug` for the draft (e.g., append `-v2` or a domain qualifier); both entries coexist. Use when the new draft is a genuinely different decision that happened to share a slug by coincidence. |

### analog

A same-conclusion, same-domain entry under a different `slug`. Two options:

| Option                    | Action                                                                                                                                                                                                                    |
| ------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **merge-into-canonical**  | **At Refine time the existing entry is the canonical one and the draft is folded into it:** append/consolidate the draft's evidence into the body, union the tags (cap 6), append the draft's `source.reference` to `also-seen-in`, bump `updated_at`. The draft never becomes a file, so nothing is de-indexed and no `superseded-by` is written. **In Maintain** (two existing entries) the analog keeps its **file** with `superseded-by: <canonical-slug>` and `status: obsolete` and its index record is **removed** (de-indexed, not deleted); the canonical's `related` records the analog's `slug`. Both forms keep the lineage. |
| **keep-separate**          | Keep the draft as its own entry under the proposed `slug`. Use when the analog is genuinely a different angle (e.g., a cache-invalidation decision and a separate cache-key-naming decision that share `domain + 2 tags` but resolve different problems). |

### none

Proceed — a genuine new entry. No resolution.

## Lineage-Preserving Merge Procedure (authoritative)

On a base-wide `merge-into-canonical` (Maintain, two existing entries) the procedure below applies. A Refine-time merge uses only steps 2 (fold the draft's body and tags into the existing entry) and 4–5, with `also-seen-in` in place of `related`, because the draft has no file to mark.

```
1. Pick the canonical slug:
   - Prefer the older entry (earlier created_at)
   - On tie, prefer the higher-priority
   - On tie, prefer the existing entry (keep the in-place one canonical)
2. Fold the analog's body into the canonical:
   - Append the analog's Problem paragraph (or merge into the canonical's Problem if clearer)
   - Append the analog's Solution/example
   - Append the analog's tags (union into the canonical's tags; cap at 6; if union exceeds 6, keep the top-6 by domain-relevance, log the trim)
   - Bump the canonical's updated_at
3. Mark the analog (de-index, keep file):
   - In the analog's frontmatter, add `superseded-by: <canonical-slug>` and `status: obsolete`
   - Do NOT delete the analog's file
   - Remove the analog's record from docs/learn/index.md (YAML block + By Category / By Domain tables)
4. Link the canonical:
   - Add the analog's slug to the canonical's `related` list (the lineage link)
   - The canonical's index record now reflects the merged content (richer body; same or expanded tags)
5. Record the merge in the artifact (Refine's lineage field / Maintain's merges list):
   merge: <analog-slug> -> <canonical-slug>
```

**Why de-index and not delete:** the analog's file may be referenced by a `related` link in another entry, or by external docs/commits. Deleting its file would orphan those links. De-indexing keeps the file reachable (the `superseded-by` note redirects readers to the canonical) and the canonical's `related` link proves the absorption. The analog's content is **not** lost — it lives in its file, superseded, plus absorbed into the canonical.

## Refine vs Maintain Scope

| Phase    | Scope of dedup                                                   | When                                                                 |
| -------- | ---------------------------------------------------------------- | -------------------------------------------------------------------- |
| Refine   | The **one** draft against the existing entries of its type and domain (per-entry), plus an exact-slug check across all types | Every authoring run (`/learn <type> <text>` or candidate curation)   |
| Maintain | Every pair **within a type + domain bucket** of the canonical store (base-wide)                 | On-demand (`/learn maintain`), after the migration step              |

Refine catches duplicates at author-time (prevents creating a duplicate). Maintain catches **inter-existing** analogs across an already-built store (the store may have accumulated analogs from many separate runs). Both use the same matching algorithm and the same resolution options above.

## Smart Pause Triggers

Dedup operations are destructive (a merge de-indexes an analog; a slug collision forces a choice). They pause in Smart mode and **always surface in Autopilot** (per [interaction-mode-propagation.md](interaction-mode-propagation.md) — destructive ops never silent):

- Refine: `dup-status: exact` (update vs new-slug) or `dup-status: analog` (merge vs keep).
- Maintain: any analog pair found in the base-wide scan (merge vs keep, per pair).

## Edge Cases

| Scenario                                                                 | Resolution                                                              |
| ----------------------------------------------------------------------- | ----------------------------------------------------------------------- |
| Analog pair but different `type` (e.g., a `decision` and a `gotcha` on caching) | **Not an analog** — different `type` blocks the analog match (a decision is not a gotcha). Keep separate. |
| Two entries with the same `slug` already on disk (corrupt store)         | Maintain flags both; the user picks the canonical; the other renames. Index reconciliation detects the duplicate row. |
| An analog referenced in another entry's `related` list                    | Still merge — but the canonical's `related` now points to the analog's old slug; readers follow the analog's `superseded-by` to the canonical. No orphan. |
| Merge would push the canonical's `tags` over 6                          | Trim to top-6 by domain-relevance; log the trim; the analog's tags are noted in the body. |
| A draft's slug matches an entry that is already `obsolete` or superseded   | Offer **revive** (re-author in place: `status` returns to active, `superseded-by` is removed, the former canonical's `related` entry for it is kept) or **new-slug**. Never write over an obsolete file silently. |
| The canonical entry is itself `obsolete`                                  | Do not merge into an obsolete entry; surface to user — likely the analog is the live one; reverse the canonical choice. |

## Validation (Refine Step 3 / Maintain Step 2 re-checks)

- A match was recorded for every same-slug / same-domain-overlapping pair (no silent matches).
- A Maintain `merge-into-canonical` always sets `superseded-by` on the analog and adds the analog's slug to the canonical's `related` (lineage preserved both ways); a Refine-time merge records the draft's reference in the canonical's `also-seen-in`.
- No analog file was deleted on a merge (only de-indexed).
- The matched evidence is recorded (`slug` + the shared signals) so the user can confirm the match is real, not a false positive.

## Notes

- This reference is the single source of truth for the matching algorithm, the resolution options, and the lineage-preserving merge procedure. Refine and Maintain apply it; the modules never re-encode the matching signals inline.
- **Decisions-not-logs** is honored: dedup operates on durable knowledge entries, never on session records. Two analogs reached the store because they were authored at different times as separate conclusions; merging absorbs them as one durable conclusion with lineage.
- The `keep-separate` option is a first-class choice: analogs that resolve *different* problems should stay separate even when they share a domain and tags. Refine/Maintain's job is to surface the candidate, not to auto-merge.