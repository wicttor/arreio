---
title: "Learnings gate logic with keyword matching and relevance scoring"
timestamp: "2026-07-02"
category: pattern
domain: information-retrieval
tags:
  [
    keyword-matching,
    relevance-scoring,
    fuzzy-search,
    gap-identification,
    scope-phase,
  ]
severity: recommended
source: commit 3943146
---

# Learnings Gate Logic with Keyword Matching and Relevance Scoring

## Problem

When scoping a plan, the system must find relevant past learnings and identify knowledge gaps. Manual lookup doesn't scale; automated matching needs a scoring system that balances precision (don't include irrelevant learnings) with recall (don't miss useful ones).

## Solution

A 5-step gate algorithm:

### Algorithm

```
1. Extract keywords — Tokenize task description/intended behavior
   (remove stop words, normalize to lowercase, keep domain terms)

2. Match learnings — Against docs/learnings/index.md
   - Exact match: keyword in learning title/summary
   - Fuzzy match: Levenshtein distance ≤ 2 (e.g., "auth" ↔ "authentication")

3. Score relevance — HIGH / MEDIUM / LOW based on domain match + applicability
   - HIGH: Exact domain match + DIRECT/CRITICAL applicability
   - MEDIUM: Related domain + RECOMMENDED/CONTEXTUAL applicability
   - LOW: Distant domain or HISTORICAL/INFORMATIONAL → EXCLUDE

4. Filter — Include only HIGH/MEDIUM in Scoped Context
   - Trim to top 5-7 if >10 matches found

5. Identify gaps — For each task domain not covered by HIGH/MEDIUM learnings
   - Document: gap name, domain, relevance, suggested action
```

### Relevance Scoring Table

| Level      | Criteria                                     | Example                                                  |
| ---------- | -------------------------------------------- | -------------------------------------------------------- |
| **HIGH**   | Exact domain + DIRECT/CRITICAL applicability | Task "Migrate REST→gRPC" + `grpc-tuning.md` → HIGH       |
| **MEDIUM** | Related domain + RECOMMENDED/CONTEXTUAL      | Task "Reduce latency" + `caching-strategies.md` → MEDIUM |
| **LOW**    | Distant domain or HISTORICAL → EXCLUDE       | Task "Dark mode UI" + `backend-balancing.md` → EXCLUDE   |

### Gap Format

```yaml
- gap_name: "[Domain] — [what's missing]"
  domain: primary domain
  relevance: why this matters for the task
  suggested_action: "Research external resource" or "Document post-implementation"
```

## Application

- Integrate in Scope Phase Step 4 of plan pipelines
- Requires `docs/learnings/index.md` to exist (skip gracefully if missing)
- Malformed learning entries are logged as warnings and skipped

## Source

- `skills/plan/references/learnings-gate-logic.md` — Full algorithm reference
- Commit `3943146`
