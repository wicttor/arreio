#!/usr/bin/env python3
"""Coverage gate for plans produced by the /plan skill.

Checks that a rendered plan stays inside its source of truth: every source item is
covered or explicitly excluded, every unit traces to a source item, unit count stays
proportional, unit order and dependencies are valid, file lists are concrete, and
(optionally) every test ID named in the source appears in the plan.

Usage:
    python check-plan.py <plan.md> [--source <doc>] [--section <heading-regex>]
                         [--item-regex <regex>] [--max-ratio 1.5]

Exit codes: 0 = pass (warnings allowed), 1 = at least one error, 2 = usage/IO error.
Uses only the Python standard library.
"""

import argparse
import math
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


def check(plan_text, args):
    """Run all checks; return (errors, warnings, summary)."""
    errors, warnings = [], []
    units = parse_units(plan_text)
    rows, justification = parse_coverage(plan_text)

    if not re.search(r"^source:\s*\S+", plan_text.split("\n---", 2)[0], re.M):
        errors.append("frontmatter has no `source:` field (use `source: prompt` when no document applies)")
    if not re.search(r"^##\s+Open Decisions\b", plan_text, re.M | re.I):
        errors.append("missing `## Open Decisions` section (write `None.` when empty)")
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

    summary = f"Coverage: {len(covered)} source items -> {len(units)} units (x{ratio:.2f}), {excluded} excluded"
    return errors, warnings, summary


def main():
    """Parse arguments, run the checks, print findings and set the exit code."""
    parser = argparse.ArgumentParser(description="Coverage gate for /plan output.")
    parser.add_argument("plan", help="path to the rendered plan markdown file")
    parser.add_argument("--source", help="source-of-truth document to compare against")
    parser.add_argument("--section", help="heading regex selecting the source section (e.g. '^## 8\\. M2')")
    parser.add_argument("--item-regex", default=r"^#{2,4}\s+(\d+(?:\.\d+)+)\b", help="regex whose group 1 captures source item IDs from headings")
    parser.add_argument("--max-ratio", type=float, default=1.5, help="max units per covered source item")
    args = parser.parse_args()

    errors, warnings, summary = check(read_text(args.plan), args)
    print(summary)
    for message in warnings:
        print(f"WARN  {message}")
    for message in errors:
        print(f"ERROR {message}")
    print("FAIL" if errors else "PASS")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
