---
title: Entry Discipline
description: Authoritative reference for Capture (drafting) and Refine (accepting). Defines what makes a conclusion durable enough to be an entry, the evidence every entry must cite, the rubrics for applicability, confidence and priority, the rule against inventing content the input does not support, and the reasons a candidate is declined.
type: reference
version: 1.0
timestamp: "2026-10-23"
---

# Entry Discipline

Authoritative rules for **what is allowed to become an entry**. [entry-schema.md](entry-schema.md) says what an entry looks like; this reference says whether the thing in hand deserves to be one, and how to fill the judgement fields (`applicability`, `confidence`, `priority`) so two agents reach the same numbers. Capture applies it while drafting; Refine re-applies it before accepting. Neither re-encodes it.

> Plan, Work and Review treat the index as the source of truth. A weak entry is not neutral: it is read later as fact. When in doubt, decline the entry and say why; an empty run is a valid outcome.

## The Durability Test

A draft passes only if **all** hold. Record the answer for each as one line in the Captured Entry (`durability`).

| # | Test | Fails when |
| - | ---- | ---------- |
| 1 | **A future skill would act differently** because of it (a Plan avoids a path, a Work run picks a pattern, a Review flags a trap). | It only describes what happened, or restates what the code or the commit message already shows. |
| 2 | **It is a conclusion, not an event.** It reads true next month without "today", "this session", "we just", "the run". | The body is a timeline, a status, a task list, or a retelling of the session. |
| 3 | **One conclusion.** A single decision, pattern, trap or convention. | It bundles several; split into separate drafts (one per Capture run). |
| 4 | **It has evidence** (see below). | No file, commit, finding, or user statement backs it. |
| 5 | **It is not derivable in seconds** from the repository (a function signature, a config value, a file layout). | A reader gets the same answer from one `grep`. |
| 6 | **It recurs or is costly.** A `gotcha` or `pattern` needs a reason to expect a second occurrence, or a cost when missed. | A one-off bug with a local fix and no way to recur (fix it; do not file it). |

A `decision` or `workflow` stated directly by the user (`/learn decision <text>`) passes tests 1 and 4 by that statement; the others still apply.

## Evidence

Every entry cites where its conclusion was confirmed, in `source.reference` and, for `gotcha`, in `## Source`.

| `source.type` | `reference` must be | Not acceptable |
| ------------- | ------------------- | -------------- |
| `commit` | A commit sha that exists in the repository. | A branch name, "latest". |
| `candidate` | `<report-id>#<candidate-key>`, where the key is the candidate's finding id, `<task-id>:<gate>`, or `c<n>` (its 1-based position in the list). | The bare report id. |
| `user` | The user's own words (a short quote or the file path they pointed at). | A paraphrase the user never saw. |

When the input is a file or commit ref, **read it** and ground the draft in what it contains. A ref that cannot be read is not evidence (ask for the conclusion in prose).

## Do Not Invent

A section may be filled only from the input, the files it points at, or the user's answer.

- Short explicit text (a sentence or two) usually supports only the headline section (`Solution`, `Pattern`, `Trap`, `Convention`). The other sections (`Decision Rationale`, `Prevention`, `Why`, `Example`) are **asked for, one question per missing section**, or the user is offered "leave out the entry". They are never filled with a plausible guess.
- A candidate supports what its `summary` and the cited task or finding show. Read the cited task file or finding and quote what it shows; do not extrapolate past it.
- `Related Learnings` lists only slugs that exist in the index (the dedup scan found them). Write `(none yet)` otherwise.
- An `Example` points at a real path in the repository or is a short snippet taken from it. No made-up code.
- Never write secrets, tokens, credentials, personal data, or absolute machine paths into an entry. Paths are repository-relative.

## Rubrics

### `applicability` (0–10 each)

Score from observable facts, then check the derived enum in [index-format.md](index-format.md) is the one you expect.

| Score | `current_project` — how directly this project uses it | `general` — how far it travels |
| ----- | ------------------------------------------------------ | ------------------------------ |
| 9–10 | Names files, skills or commands that exist here and will be touched again. | True for any project using the same stack or practice. |
| 7–8 | Applies to code or process here that is in regular use. | True for most projects using the same tool or language. |
| 5–6 | Applies to a part of the project that changes rarely. | True under stated conditions that are common. |
| 3–4 | Applied once, or in a part being retired. | True only for a narrow variant. |
| 0–2 | Not used here today (kept as a reference). | Specific to this project. |

`current_project` scores what exists in this repository now; do not inflate it because the topic feels important.

### `confidence`

| Value | When |
| ----- | ---- |
| `high` | Confirmed by running something or reading the code, and the evidence is cited. |
| `medium` | Stated by the user or drawn from a report, not independently confirmed. (Default.) |
| `low` | A hypothesis, or evidence that is indirect. A `low` entry also says so in its body. |

### `priority`

`important` only when ignoring the entry would make a skill produce wrong output or break something (a gotcha with silent failure, a decision other entries depend on). Everything else is `normal`. No more than a fifth of the entries in a store should be `important`; if Refine finds the store above that, it warns and asks.

## Reasons to Decline (record, do not write)

| Code | Meaning |
| ---- | ------- |
| `not-durable` | Fails test 1, 2 or 5. |
| `no-evidence` | Fails test 4 and the user cannot supply one. |
| `one-off` | Fails test 6. |
| `bundle` | Fails test 3 and the user chose not to split. |
| `already-captured` | An entry's `source.reference` or `also-seen-in` already holds this candidate key. |
| `declined-by-user` | The user chose not to author it. |

A declined candidate appears in the run's closing line with its code. It is not written anywhere and does not block the others.

## Notes

- Applying this reference is Capture's job (it drafts only what passes) and Refine's job (it re-checks, never trusting the draft). The coherence gate script checks what is mechanical (evidence present, absolute paths, session wording); judgement (tests 1, 5 and 6) stays with the agent and the user.
- The rubrics exist so that `applicability` is reproducible. Example values in templates are illustrations; compute from the real entry.
