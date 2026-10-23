---
title: Entry Schema
description: Authoritative write-contract reference for Capture (drafts) and Refine (validates). Defines the canonical per-entry frontmatter (the unified schema the legacy decision+pattern entries converged to), the per-type body section templates, and the index-record shape that the read side (Plan/Work/Review's learnings-gate-logic) parses. Single source of truth for the entry's shape.
type: reference
version: 1.0
timestamp: "2026-08-08"
---

# Entry Schema

Authoritative **write contract** for a knowledge entry. Capture drafts the frontmatter and body from this schema; Refine validates against it; Index derives the index-record enum from it; Maintain refreshes stale entries to it. The schema unifies the two historical layouts observed in the legacy store (the newer `decision`/`gotcha` layout with `slug`+`priority`+`applicability`+`confidence`, and the older `pattern`/`workflow` layout with `title`+`category`+`severity`) into one canonical form. Capture/Refine **look this schema up**; they do not re-encode the field list.

> **Write side / read side (single source of truth).** This reference owns the **write side** — the per-entry frontmatter and the `index-record` shape. The Plan skill owns the **read side** — the search algorithm in [learnings-gate-logic.md](../../plan/references/learnings-gate-logic.md). The two contracts share the **index-record shape** (`filename`, `domain`, `tags`, `applicability`, `summary`). Capturing this schema here, once, prevents the secondary-spec-contradicts-authoritative-matrix gotcha: no other reference re-encodes the entry's fields.

## The Four Entry Types

| Type       | Carries                                                                          | Section template (body)                                                                             |
| ---------- | -------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------- |
| `decision` | An authoritative choice with rationale                                          | Problem / Solution / Decision Rationale / Application / Related Learnings                            |
| `pattern`  | A confirmed, reusable approach                                                  | Problem / Pattern / When to Apply / Example / Related Learnings                                      |
| `gotcha`   | A recurring trap with prevention                                                | Problem / Trap / Solution / Prevention / Related Learnings / Source                                 |
| `workflow` | A project convention                                                            | Convention / Why / How / Related Learnings                                                          |

Each entry is **exactly one** conclusion; one entry per conclusion; never a bundle.

## Per-Entry Frontmatter (canonical, unified)

```yaml
---
slug: <kebab-case-slug>                       # REQUIRED. Globally unique. The upsert key for the entry file + index record.
type: decision | pattern | gotcha | workflow  # REQUIRED. One of the four.
domain: <primary-domain>                      # REQUIRED. A single primary domain.
priority: important | normal                  # OPTIONAL (default normal).
applicability:                                # REQUIRED. Numeric scores per side.
  current_project: <0-10>                    # How directly the project uses this.
  general: <0-10>                            # How broadly it generalizes.
tags: [<related-domain-1>, ...]              # REQUIRED. 2-6 related domains.
summary: <1-2 sentences>                      # REQUIRED. What a reader needs to decide whether to open the entry. Copied verbatim into the index record.
created_at: <ISO-8601>                        # REQUIRED. Set by Capture; Refine preserves.
updated_at: <ISO-8601>                        # REQUIRED. Stamped on any edit (Refine/Index/Maintain).
source:                                       # REQUIRED. Where the entry came from.
  type: commit | candidate | user             # commit: derived from a commit; candidate: from Work/Review; user: freeform author.
  reference: <commit-sha | report-id#finding-id | text>  # The locator.
  extracted_at: <ISO-8601>                   # When the entry was captured.
confidence: high | medium | low               # OPTIONAL (default medium). The author's confidence.
# Lineage (set by Maintain / migration, optional):
migrated-from: <docs/learnings/<type>/<file>.md>   # Only for a migrated legacy entry.
superseded-by: <canonical-slug>              # Only for an analog merged into a canonical entry.
status: active | obsolete                    # OPTIONAL (default active). `obsolete` de-indexes the entry.
related: [<slug>, ...]                       # OPTIONAL. Linked entries (a canonical entry lists the analogs it absorbed).
also-seen-in: [<source.reference>, ...]      # OPTIONAL. Other evidence folded into this entry by a merge or a re-author; never edited by hand.
---
```

**Field rules (authoritative):**

- `slug` — kebab-case; globally unique across all four types (one slug namespace); descriptive (date suffix allowed for time-bound decisions). Capture proposes; Refine uniqueness-checks; Index upserts on it.
- `type` — one of the four; the body section template is determined by it (see above). Type does not change after authoring (a `decision` may not be reclassified as a `pattern` post-hoc — that's a new entry with a new `slug`, and the old one de-indexes).
- `domain` — a single primary domain (never a list); the `tags` carry the related domains.
- `priority` — `important` for entries that block or strongly steer a skill; `normal` otherwise. Defaults to `normal` when absent.
- `applicability.current_project` / `general` — integers 0–10. The **write side** stores the rich numerics; the **read side** projects to the enum (see [index-format.md](index-format.md)).
- `tags` — a list of **2–6** related domains or topics (no more, no fewer; Refine validates the count). The `domain` need not repeat in `tags`.
- `confidence` — `high` / `medium` / `low`; defaults to `medium` when absent.
- `summary` — required; one or two sentences, no more than 240 characters, written as the conclusion (not "this entry describes..."). Maintain may derive a missing one from the body as a non-destructive fix.
- `source.type` — `commit` (derived from a commit sha), `candidate` (from a Work/Review `learnings-to-capture` list), or `user` (freeform `/learn <type> <text>`). The `reference` formats are fixed in [entry-discipline.md](entry-discipline.md#evidence); `reference` is never empty.
- `also-seen-in` — written by Refine/Index when a later draft was merged into this entry (see [dedup-rules.md](dedup-rules.md)) or when `update-existing` re-authors it with a different `source.reference`. It is how a candidate already folded in is recognized as captured.
- `migrated-from` / `superseded-by` / `related` / `also-seen-in` — lineage fields set by Maintain (or Index on a merge), not by Capture. See [dedup-rules.md](dedup-rules.md) and [migration-bootstrap.md](migration-bootstrap.md).

## Per-Type Body Section Templates (authoritative)

A `decision` body has exactly these sections (in order); body sections are validated by Refine:

### decision
```
# <Title in Title Case>

## Problem     [what problem this decision resolves]
## Solution    [the decision — what was chosen]
## Decision Rationale  [why this choice over alternatives]
## Application [where in the project this decision lives — files, skills, phases]
## Related Learnings  [linked slug(s) + one-line role]
```

### pattern
```
# <Title in Title Case>

## Problem    [the recurring problem the pattern solves]
## Pattern    [the confirmed approach]
## When to Apply [signals that this pattern fits]
## Example    [a concrete use of the pattern, ideally in-repo]
## Related Learnings  [linked slug(s) + one-line role]
```

### gotcha
```
# <Title in Title Case>

## Problem    [the surface symptom]
## Trap       [the silent failure mode]
## Solution   [how to fix it once hit]
## Prevention [how to avoid it next time — the durable part]
## Related Learnings  [linked slug(s) + one-line role]
## Source     [file/commit/ref where this was confirmed — optional duplicate of frontmatter.source for human readability]
```

### workflow
```
# <Title in Title Case>

## Convention [the agreed-upon practice]
## Why        [the reason for the convention]
## How         [the steps to apply it — concrete, repo-relative]
## Related Learnings  [linked slug(s) + one-line role]
```

## Index-Record Shape (the read-contract projection)

`docs/learn/index.md` carries one record per entry in its YAML `entries:` block (format in [index-format.md](index-format.md)). That record projects the full frontmatter to the **five fields** the read side parses:

```yaml
- filename: docs/learn/<type>/<slug>.md
  domain: <primary-domain>
  tags: [tag-1, tag-2]
  applicability: DIRECT | RECOMMENDED | CONTEXTUAL | HISTORICAL | INFORMATIONAL
  summary: <the entry's frontmatter summary, verbatim>
```

The `applicability` enum is **derived** from the frontmatter's numeric scores per [index-format.md](index-format.md)'s derivation — never stored twice. The `summary` is the frontmatter's `summary`, verbatim. **Field set is fixed**: `filename`, `domain`, `tags`, `applicability`, `summary` — exactly these five (the gate-logic's read contract).

## Validation Rules (Refine applies)

1. **Frontmatter:** all REQUIRED fields present and well-typed; `type` ∈ the four; `domain` non-empty; `tags` length 2–6; `applicability` scores integers 0–10; `confidence` ∈ enum; `slug` kebab-case.
2. **Body:** the per-type section template present (all the sections for the type); no extra top-level sections that contradict the template.
3. **Coherence:** the slug describes the body title (a date or `-v2`-style suffix is allowed); the file sits at `docs/learn/<type>/<slug>.md` for its own `type` and `slug`; the index-record projection (filename/domain/tags/applicability/summary) is computable from the entry.
4. **Durability and evidence:** the draft passes [entry-discipline.md](entry-discipline.md) (the durability test, a `source.reference` in the fixed format, no invented sections, no absolute paths or secrets).
5. **On a missing `summary`:** ask for it (Refine) or derive it from the body (Maintain refresh); never index a record without one. On a wrong type/wrong shape: block and ask (Category 2 recovery).

## Migration (legacy → canonical)

Legacy entries use one of two prior layouts; the migration ([migration-bootstrap.md](migration-bootstrap.md)) normalizes both to the canonical schema:

| Legacy layout | Fields present | Canonical conversion |
| ------------- | -------------- | -------------------- |
| Newer (decision/gotcha) | `slug`, `type`, `domain`, `priority`, `applicability.{current_project,general}`, `tags`, `confidence` | Already canonical apart from a possibly missing `summary` (derive it from the body, noted as derived); preserve; add `migrated-from` lineage. |
| Older (pattern/workflow) | `title`, `category`, `severity`, `domain`, `tags`, `source: commit <sha>` | Convert: `type = category` (the legacy `category` field); `slug = <kebab-case-of-title>[-<date>]`; `summary` = the legacy summary if present, else the first sentence of the body's Problem or Convention section (noted as derived); `priority = important if severity==important else normal`; `applicability.{current_project,general}` inferred from `severity` (`important`→{9,7}, `recommended`→{6,5}, `informational`→{3,4}); `confidence = medium`; restructure `source` to `{type: commit, reference: <sha>, extracted_at: <date>}`. Add `migrated-from`. |

The conversion **preserves content** — the body sections are kept, frontmatter is normalized, lineage is recorded. No legacy entry is silently dropped; no canonical field is invented where the legacy had no basis (an inferred score from `severity` is noted as inferred, never silently exact).

## Notes

- This reference is the single source of truth for the entry's shape. Capture drafts from it; Refine validates against it; Index projects to the index-record from it; Maintain refreshes to it. None re-encode the field list or body templates inline.
- The schema deliberately separates the **write side** (rich numeric `applicability` + `confidence` + lineage) from the **read side** (the enum projection in the index-record). This honors the secondary-spec gotcha: the search algorithm lives once in Plan's gate-logic; the entry schema lives once here.
- `summary` is a required frontmatter field; the index record carries it verbatim, so the entry and the index cannot disagree.
- Changing an entry's `type` post-hoc is a **new entry** (new `slug`), and the old entry de-indexes — never an in-place reclassification (a decision is a decision; a pattern is a pattern).