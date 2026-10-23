#!/usr/bin/env python3
"""Coverage gate for plans produced by the /plan skill.

Checks that a rendered plan stays inside its source of truth: every source item is
covered or explicitly excluded, every unit traces to a source item, unit count stays
proportional, unit order and dependencies are valid, file lists are concrete and agree
with the repository (Modify paths exist, Create paths do not, no file is created twice,
stated file counts match the lists), and (optionally) every test ID named in the source
appears in the plan.

Usage:
    python check-plan.py <plan.md> [--source <doc>] [--section <heading-regex>]
                         [--item-regex <regex>] [--max-ratio 1.5] [--hard-ratio 2.0]
                         [--repo <dir>] [--no-fs]

Exit codes: 0 = pass (warnings allowed), 1 = at least one error, 2 = usage/IO error.
Uses only the Python standard library.
"""

import argparse
import math
import os
import re
import sys

# Phrases that make a Files list non-concrete (matched case-insensitively on file lines).
VAGUE_PHRASES = [
    "as needed", "if needed", "where needed", "if required", "only if required",
    "as required", "where required", "etc.", "and similar", "and so on",
]

UNIT_START = re.compile(r"^\s*-\s+\*{0,2}(U\d+[a-z]?)\b")
UNIT_ID = re.compile(r"U(\d+)([a-z]?)")
TEST_ID = re.compile(r"\b([A-Z]{1,5}(?:-[A-Z]{1,5})*)-(\d{2})(?:\.\.(\d{2}))?\b")
HEADING = re.compile(r"^(#{1,6})\s+(.*)$")
FILE_LINE = re.compile(r"^\s*(?:[-*]\s+)?\**(Create|Modify|Test)\**:?\**\s*(.*)$", re.I)
FILE_COUNT_CLAIM = re.compile(r"\b(\d+)\s+planned\s+files\b|\b(\d+)\s+files\s+in\s+total\b|\btotal\s+of\s+(\d+)\s+files\b", re.I)


def read_text(path):
    """Read a UTF-8 text file; exit with code 2 when it cannot be read."""
    try:
        with open(path, encoding="utf-8") as handle:
            return handle.read()
    except OSError as error:
        print(f"ERROR cannot read {path}: {error}")
        sys.exit(2)


def unit_sort_key(unit_id):
    """Return a (number, letter) tuple so unit IDs compare in document order."""
    match = UNIT_ID.fullmatch(unit_id)
    return (int(match.group(1)), match.group(2))


def expand_units(text):
    """Expand unit references in text, including ranges such as U1-U8 or U1–U8."""
    found = []
    for match in re.finditer(r"U(\d+)\s*[–-]\s*U?(\d+)", text):
        found.extend(f"U{n}" for n in range(int(match.group(1)), int(match.group(2)) + 1))
    cleaned = re.sub(r"U(\d+)\s*[–-]\s*U?(\d+)", " ", text)
    found.extend(m.group(0) for m in re.finditer(r"U\d+[a-z]?\b", cleaned))
    return found


def expand_test_ids(text):
    """Return the set of test IDs in text, expanding ranges like U-JRN-01..04."""
    ids = set()
    for match in TEST_ID.finditer(text):
        prefix, start, end = match.group(1), int(match.group(2)), match.group(3)
        last = int(end) if end else start
        ids.update(f"{prefix}-{n:02d}" for n in range(start, last + 1))
    return ids


def section_text(text, heading_regex):
    """Return the body of the first heading matching heading_regex, up to the next heading of equal or higher level."""
    lines = text.splitlines()
    for index, line in enumerate(lines):
        match = HEADING.match(line)
        if match and re.search(heading_regex, line):
            level = len(match.group(1))
            body = []
            for follow in lines[index + 1:]:
                follow_match = HEADING.match(follow)
                if follow_match and len(follow_match.group(1)) <= level:
                    break
                body.append(follow)
            return "\n".join(body)
    return None


def parse_units(text):
    """Parse unit blocks into dicts with id, line, source ids, dependency ids and file lines."""
    units = []
    current = None
    for number, line in enumerate(text.splitlines(), start=1):
        if HEADING.match(line):
            current = None
            continue
        start = UNIT_START.match(line)
        if start:
            current = {"id": start.group(1), "line": number, "source": [], "deps": [], "files": []}
            units.append(current)
            continue
        if current is None:
            continue
        field = re.match(r"^\s*(?:[-*]\s+)?\**(Source|Dependencies|Files|Create|Modify|Test)\b\**:?\**:?\s*(.*)$", line, re.I)
        if not field:
            if current["files"] and re.match(r"^\s+[-*]\s+", line):
                current["files"].append(line)
            continue
        name, value = field.group(1).lower(), field.group(2)
        if name == "source":
            current["source"] = [s for s in re.split(r"[,;\s]+", value.replace("*", "")) if s]
        elif name == "dependencies":
            current["deps"] = expand_units(value)
        else:
            current["files"].append(line)
    return units


def parse_coverage(text):
    """Parse the Source Coverage section into (rows, justification). Rows: id -> {units, excluded, reason}."""
    body = section_text(text, r"^##\s+Source Coverage")
    if body is None:
        return None, ""
    rows, justification = {}, ""
    for line in body.splitlines():
        if line.lower().lstrip("*- ").startswith("justification:"):
            justification = line.split(":", 1)[1].strip(" *")
            continue
        if not line.strip().startswith("|") or re.match(r"^\s*\|[\s:|-]+\|?\s*$", line):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 3 or cells[0].lower() in ("source item", "item", "id"):
            continue
        outcome = cells[2]
        excluded = outcome.lower().startswith("excluded")
        reason = outcome.split("—", 1)[-1].split("-", 1)[-1].strip() if excluded else ""
        rows[cells[0].strip("` ")] = {"units": set(expand_units(outcome)), "excluded": excluded, "reason": reason}
    return rows, justification


def find_repo_root(plan_path, explicit):
    """Return the repository root: --repo, else the nearest ancestor of the plan holding .git, else the current directory."""
    if explicit:
        return os.path.abspath(explicit)
    folder = os.path.dirname(os.path.abspath(plan_path))
    while True:
        if os.path.exists(os.path.join(folder, ".git")):
            return folder
        parent = os.path.dirname(folder)
        if parent == folder:
            return os.getcwd()
        folder = parent


def file_entries(unit):
    """Return (kind, path) pairs from a unit's file lines; globs and non-path tokens (test IDs) are skipped."""
    entries = []
    for line in unit["files"]:
        match = FILE_LINE.match(line)
        if not match:
            continue
        kind = match.group(1).lower()
        for token in re.findall(r"`([^`]+)`", match.group(2)):
            if "/" in token and "*" not in token and " " not in token:
                entries.append((kind, token.replace("\\", "/")))
    return entries


def check_files(units, plan_text, repo, errors, warnings):
    """Check file lists against the repository and against each other; return (entry count, distinct count)."""
    created_by = {}
    entry_total, distinct = 0, set()
    for unit in units:
        for kind, path in file_entries(unit):
            entry_total += 1
            distinct.add(path)
            exists = repo is not None and os.path.exists(os.path.join(repo, path))
            if kind == "create":
                if path in created_by:
                    errors.append(f"{unit['id']}: `{path}` is already created by {created_by[path]}; use Modify or drop the duplicate")
                    continue
                created_by[path] = unit["id"]
                if exists:
                    errors.append(f"{unit['id']}: Create `{path}` already exists in the repository (use Modify, or fix the path)")
            elif kind == "modify" and repo is not None and not exists and path not in created_by:
                errors.append(f"{unit['id']}: Modify `{path}` does not exist and no earlier unit creates it")
    # Stated file counts must match the lists (lines outside the unit file lists only).
    unit_file_lines = {line for unit in units for line in unit["files"]}
    for line in plan_text.splitlines():
        if line in unit_file_lines:
            continue
        for claim in FILE_COUNT_CLAIM.finditer(line):
            stated = int(next(g for g in claim.groups() if g))
            if stated not in (entry_total, len(distinct)):
                errors.append(f"plan states {stated} files but the units list {entry_total} entries ({len(distinct)} distinct paths); recount or drop the number")
    return entry_total, len(distinct)


def check(plan_text, args, repo=None):
    """Run all checks; return (errors, warnings, summary)."""
    errors, warnings = [], []
    units = parse_units(plan_text)
    rows, justification = parse_coverage(plan_text)

    if not re.search(r"^source:\s*\S+", plan_text.split("\n---", 2)[0], re.M):
        errors.append("frontmatter has no `source:` field (use `source: prompt` when no document applies)")
    if not re.search(r"^##\s+Open Decisions\b", plan_text, re.M | re.I):
        errors.append("missing `## Open Decisions` section (write `None.` when empty)")
    status = re.search(r"^status:\s*(\S+)", plan_text.split("\n---", 2)[0], re.M)
    if status and status.group(1).strip("\"'") == "complete":
        warnings.append("frontmatter `status: complete` on a freshly generated plan; use `ready` (Work and Review move it on)")
    if not units:
        errors.append("no implementation units found (expected lines like `- U1. **Name**`)")
    if rows is None:
        errors.append("missing `## Source Coverage` section")
        return errors, warnings, "no coverage table"

    # Unit order: IDs must increase in document order.
    ordered = [u["id"] for u in units]
    if len(set(ordered)) != len(ordered):
        errors.append("duplicate unit IDs: " + ", ".join(sorted({i for i in ordered if ordered.count(i) > 1})))
    for previous, unit in zip(units, units[1:]):
        if unit_sort_key(unit["id"]) <= unit_sort_key(previous["id"]):
            errors.append(f"line {unit['line']}: {unit['id']} appears after {previous['id']} (unit IDs must increase in document order)")

    # Dependencies: must exist and appear earlier.
    position = {u["id"]: i for i, u in enumerate(units)}
    for index, unit in enumerate(units):
        for dep in unit["deps"]:
            if dep not in position:
                errors.append(f"{unit['id']}: dependency {dep} does not exist")
            elif position[dep] >= index:
                errors.append(f"{unit['id']}: dependency {dep} is not an earlier unit")

    # Concrete files.
    for unit in units:
        for line in unit["files"]:
            hit = next((p for p in VAGUE_PHRASES if p in line.lower()), None)
            if hit:
                errors.append(f"{unit['id']}: vague file list (\"{hit}\"): {line.strip()[:80]}")

    entries, distinct_count = check_files(units, plan_text, repo, errors, warnings)

    # Traceability: units <-> coverage rows.
    computed = {}
    for unit in units:
        if not unit["source"]:
            errors.append(f"{unit['id']}: no `Source:` field (every unit must trace to a source item)")
        for item in unit["source"]:
            if item not in rows:
                errors.append(f"{unit['id']}: Source `{item}` is not in the Source Coverage table")
            computed.setdefault(item, set()).add(unit["id"])
    for item, row in rows.items():
        if row["excluded"]:
            if not row["reason"]:
                errors.append(f"source item {item}: excluded without a reason")
            continue
        if not row["units"]:
            errors.append(f"source item {item}: neither covered by a unit nor excluded")
        elif row["units"] != computed.get(item, set()):
            errors.append(f"source item {item}: table lists {sorted(row['units'])} but units declare {sorted(computed.get(item, set()))}")

    covered = [i for i, r in rows.items() if not r["excluded"]]
    excluded = len(rows) - len(covered)
    cap = math.ceil(args.max_ratio * max(len(covered), 1))
    ratio = len(units) / max(len(covered), 1)
    if len(units) > cap and not justification:
        errors.append(f"{len(units)} units for {len(covered)} source items exceeds the cap of {cap} (x{args.max_ratio}); merge units or add `Justification:` in Source Coverage")
    elif len(units) > cap:
        warnings.append(f"{len(units)} units exceed the cap of {cap}; justified: {justification[:80]}")
    hard = math.ceil(args.hard_ratio * max(len(covered), 1))
    if len(units) > hard:
        errors.append(f"{len(units)} units for {len(covered)} source items exceeds the hard ceiling of {hard} (x{args.hard_ratio}) even with a justification; merge units or move work to Open Decisions")

    # Optional comparison against the source document itself.
    if args.source:
        source_body = section_text(read_text(args.source), args.section) if args.section else read_text(args.source)
        if source_body is None:
            errors.append(f"section matching `{args.section}` not found in {args.source}")
        else:
            source_items = re.findall(args.item_regex, source_body, re.M)
            for item in source_items:
                if item not in rows:
                    errors.append(f"source item {item} (in {args.source}) is missing from the Source Coverage table")
            for item in rows:
                if source_items and item not in source_items:
                    warnings.append(f"coverage row {item} does not match any item in the source section")
            test_lines = "\n".join(l for l in source_body.splitlines() if re.search(r"test", l, re.I))
            missing = sorted(expand_test_ids(test_lines) - expand_test_ids(plan_text))
            if missing:
                errors.append("test IDs in the source but not in the plan: " + ", ".join(missing))

    # A test ID owned by several units is suspicious (gate units that list all tests are expected).
    seen = {}
    for unit in units:
        for test_id in expand_test_ids("\n".join(unit["files"])):
            seen.setdefault(test_id, set()).add(unit["id"])
    for test_id, owners in sorted(seen.items()):
        if len(owners) > 1:
            warnings.append(f"test ID {test_id} appears in several units: {', '.join(sorted(owners))}")

    summary = f"Coverage: {len(covered)} source items -> {len(units)} units (x{ratio:.2f}), {excluded} excluded; {entries} file entries, {distinct_count} distinct paths"
    return errors, warnings, summary


def main():
    """Parse arguments, run the checks, print findings and set the exit code."""
    parser = argparse.ArgumentParser(description="Coverage gate for /plan output.")
    parser.add_argument("plan", help="path to the rendered plan markdown file")
    parser.add_argument("--source", help="source-of-truth document to compare against")
    parser.add_argument("--section", help="heading regex selecting the source section (e.g. '^## 8\\. M2')")
    parser.add_argument("--item-regex", default=r"^#{2,4}\s+(\d+(?:\.\d+)+)\b", help="regex whose group 1 captures source item IDs from headings")
    parser.add_argument("--max-ratio", type=float, default=1.5, help="max units per covered source item")
    parser.add_argument("--hard-ratio", type=float, default=2.0, help="ceiling on units per covered source item; an error even when justified")
    parser.add_argument("--repo", help="repository root for path checks (default: nearest ancestor of the plan holding .git)")
    parser.add_argument("--no-fs", action="store_true", help="skip the checks that read the repository (Modify exists, Create does not)")
    args = parser.parse_args()

    repo = None if args.no_fs else find_repo_root(args.plan, args.repo)
    errors, warnings, summary = check(read_text(args.plan), args, repo)
    print(summary)
    for message in warnings:
        print(f"WARN  {message}")
    for message in errors:
        print(f"ERROR {message}")
    print("FAIL" if errors else "PASS")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
