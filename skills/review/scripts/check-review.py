#!/usr/bin/env python3
"""Coherence gate for reports produced by the /review skill.

Checks that a Review Report is internally consistent: every finding is well formed and
evidenced, the rollup matches the findings, the approval status follows from the tallies,
per-task verdicts follow from the findings attributed to each task, and (optionally) the
task files, work index, and registry agree with the report.

Usage:
    python check-review.py <report.md> [--registry <docs/review/index.md>] [--tasks <docs/tasks/work-id>]

Exit codes: 0 = pass (warnings allowed), 1 = at least one error, 2 = usage/IO error.
Uses only the Python standard library.
"""

import argparse
import glob
import os
import re
import sys

SEVERITIES = ["blocker", "major", "minor", "nit"]
CATEGORIES = ["quality", "security", "tests", "documentation", "integration", "scope-creep"]
VERDICTS = {"approved", "changes-requested", "rejected"}
SHAPES = {"change-set", "work-linked", "task-in-review", "ad-hoc"}
MAX_LISTED_NITS = 5
NULLISH = {"", "null", "none", "~"}


def read_text(path):
    """Read a UTF-8 text file; exit with code 2 when it cannot be read."""
    try:
        with open(path, encoding="utf-8") as handle:
            return handle.read()
    except (OSError, UnicodeDecodeError) as error:
        print(f"ERROR cannot read {path}: {error}")
        sys.exit(2)


def top_level(lines):
    """Return {key: raw value} for column-0 `key: value` lines (fences and frontmatter dashes skipped)."""
    found = {}
    for line in lines:
        match = re.match(r"^([a-z][a-z-]*):\s*(.*?)\s*$", line)
        if match:
            found.setdefault(match.group(1), match.group(2).strip("\"'"))
    return found


def block(lines, key):
    """Return the indented lines that follow a column-0 `key:` line, up to the next column-0 key."""
    out, inside = [], False
    for line in lines:
        if re.match(rf"^{key}:", line):
            inside = True
            if line.strip() != f"{key}:":
                return []  # inline value such as `findings: []`
            continue
        if inside:
            if re.match(r"^[a-z][a-z-]*:", line):
                break
            out.append(line)
    return out


def parse_findings(lines):
    """Parse the findings block into a list of {field: raw value} dicts."""
    findings, current = [], None
    for line in block(lines, "findings"):
        start = re.match(r"^\s+-\s+id:\s*(\S+)", line)
        if start:
            current = {"id": start.group(1).strip("\"'")}
            findings.append(current)
            continue
        field = re.match(r"^\s+([a-z][a-z-]*):\s*(.*?)\s*$", line)
        if field and current is not None:
            current[field.group(1)] = field.group(2).strip("\"'")
    return findings


def parse_counts(lines, name):
    """Parse a `by-severity` / `by-category` dict line from the findings-rollup block."""
    for line in block(lines, "findings-rollup"):
        if re.match(rf"^\s+{name}:", line):
            return {k: int(v) for k, v in re.findall(r"([a-z-]+):\s*(\d+)", line)}
    return None


def parse_total(lines):
    """Return the rollup `total` as an int, or None."""
    for line in block(lines, "findings-rollup"):
        match = re.match(r"^\s+total:\s*(\d+)", line)
        if match:
            return int(match.group(1))
    return None


def parse_verdicts(lines):
    """Parse task-verdicts rows into {task-id: (verdict, set of finding ids)}."""
    verdicts = {}
    for line in block(lines, "task-verdicts"):
        row = re.search(r"task-id:\s*([^,\s}]+),\s*verdict:\s*([a-z-]+),\s*findings:\s*\[(.*?)\]", line)
        if row:
            ids = {i.strip() for i in row.group(3).split(",") if i.strip()}
            verdicts[row.group(1)] = (row.group(2), ids)
    return verdicts


def derive(findings):
    """Apply the approval rule to a list of findings; return (status, blocker count, major count, creep count)."""
    blockers = sum(1 for f in findings if f.get("severity") == "blocker")
    majors = sum(1 for f in findings if f.get("severity") == "major")
    creep = sum(1 for f in findings if f.get("scope-creep") == "true" and f.get("accepted", "null") in NULLISH)
    if blockers:
        return "rejected", blockers, majors, creep
    if majors or creep:
        return "changes-requested", blockers, majors, creep
    return "approved", blockers, majors, creep


def check_findings(findings, scope_creep_summary, errors, warnings):
    """Validate each finding's fields, trace/creep exclusivity, evidence, and acceptance."""
    seen = set()
    for f in findings:
        fid = f["id"]
        if fid in seen:
            errors.append(f"{fid}: duplicate finding id")
        seen.add(fid)
        if f.get("severity") not in SEVERITIES:
            errors.append(f"{fid}: invalid severity {f.get('severity')!r}")
        if f.get("category") not in CATEGORIES:
            errors.append(f"{fid}: invalid category {f.get('category')!r}")
        location = f.get("location", "")
        if not location or location.startswith("/") or re.match(r"^[A-Za-z]:[\\/]", location) or ".." in location.split(":")[0].split("/"):
            errors.append(f"{fid}: location {location!r} is not a repository-relative path")
        evidence = f.get("evidence", "")
        if evidence.lower() in NULLISH:
            (errors if f.get("severity") in ("blocker", "major") else warnings).append(f"{fid}: missing evidence")
        has_trace = f.get("trace", "null").lower() not in NULLISH
        has_creep = f.get("scope-creep") == "true"
        if has_trace == has_creep:
            errors.append(f"{fid}: needs exactly one of trace / scope-creep: true")
        if (f.get("category") == "scope-creep") != has_creep:
            errors.append(f"{fid}: category scope-creep and the scope-creep flag must agree")
        if has_creep and scope_creep_summary.startswith("skipped"):
            errors.append(f"{fid}: scope-creep finding although scope-creep was skipped (no requirements)")
        if f.get("accepted", "null").lower() not in NULLISH and not has_creep:
            errors.append(f"{fid}: only scope-creep findings can be accepted")
    nits = [f for f in findings if f.get("severity") == "nit" and not re.match(r"^\d+ further", f.get("message", ""))]
    if len(nits) > MAX_LISTED_NITS:
        errors.append(f"{len(nits)} nits listed individually; fold all but {MAX_LISTED_NITS} into one 'N further style nits' finding")


def check_rollup(lines, findings, errors):
    """Compare the report's rollup counts with a recount of the findings."""
    by_severity, by_category, total = parse_counts(lines, "by-severity"), parse_counts(lines, "by-category"), parse_total(lines)
    if by_severity is None or by_category is None or total is None:
        errors.append("findings-rollup is missing by-severity, by-category, or total")
        return
    for name, counts, field, keys in (("severity", by_severity, "severity", SEVERITIES), ("category", by_category, "category", CATEGORIES)):
        for key in keys:
            actual = sum(1 for f in findings if f.get(field) == key)
            if counts.get(key, 0) != actual:
                errors.append(f"rollup by-{name} {key}: report says {counts.get(key, 0)}, findings have {actual}")
    if total != len(findings):
        errors.append(f"rollup total: report says {total}, findings have {len(findings)}")


def check_verdicts(findings, verdicts, errors):
    """Check each task's verdict equals the rule applied to its attributed plus run-level findings."""
    for task_id, (verdict, listed) in verdicts.items():
        if verdict not in VERDICTS:
            errors.append(f"{task_id}: invalid verdict {verdict!r}")
            continue
        attributed = [f for f in findings if not f.get("tasks", "").strip("[] ") or task_id in re.findall(r"[^\s,\[\]]+", f.get("tasks", ""))]
        expected = derive(attributed)[0]
        if verdict != expected:
            errors.append(f"{task_id}: verdict {verdict}, but its findings give {expected}")
        if listed != {f["id"] for f in attributed}:
            errors.append(f"{task_id}: verdict lists findings {sorted(listed)}, attributed are {sorted(f['id'] for f in attributed)}")
    for f in findings:
        for task_id in re.findall(r"[^\s,\[\]]+", f.get("tasks", "")):
            if task_id not in verdicts:
                errors.append(f"{f['id']}: attributed to {task_id}, which has no verdict")


def short_id(task_id):
    """Return the T<NN> part of a task id such as 2026-10-23-001-T02a."""
    return re.search(r"(T\d+[a-z]?)$", task_id).group(1) if re.search(r"(T\d+[a-z]?)$", task_id) else task_id


def check_tasks(folder, report_id, shape, verdicts, errors):
    """Check task files, checkboxes, and the work-index block against the report."""
    index_path = os.path.join(folder, "index.md")
    index_text = read_text(index_path) if os.path.isfile(index_path) else ""
    if not index_text:
        errors.append(f"{index_path} missing or empty")
    rows = {m.group(2): m.group(1) for line in index_text.splitlines() if (m := re.match(r"^\s*-\s+\[( |x)\]\s+(T\d+[a-z]?)\b", line))}
    blocks = len(re.findall(rf"^## Review Report\s+[—-]\s+{re.escape(report_id)}\s*$", index_text, re.MULTILINE))
    if shape in ("work-linked", "task-in-review") and blocks != 1:
        errors.append(f"work index has {blocks} Review Report blocks for {report_id}; expected exactly 1")
    for task_id, (verdict, _) in verdicts.items():
        short = short_id(task_id)
        matches = glob.glob(os.path.join(folder, f"{short}-*.md"))
        if len(matches) != 1:
            errors.append(f"{task_id}: expected one task file {short}-*.md, found {len(matches)}")
            continue
        text = read_text(matches[0]).replace("\r\n", "\n")
        front = re.match(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
        front = front.group(1) if front else ""
        status = (re.search(r"^status:\s*(\S+)", front, re.MULTILINE) or [None, None])[1]
        box = (re.search(r"^## Acceptance Criteria\s*\n+\s*-\s+\[( |x)\]", text, re.MULTILINE) or [None, None])[1]
        approved = verdict == "approved"
        want = "completed" if approved else "blocked"
        if status != want:
            errors.append(f"{task_id}: verdict {verdict} requires status {want}, task file has {status}")
        if (box == "x") != approved or (rows.get(short) == "x") != approved:
            errors.append(f"{task_id}: checkboxes (task [{box}], index [{rows.get(short)}]) do not match verdict {verdict}")
        if not approved:
            if not re.search(r"^block-reason:\s*\S", front, re.MULTILINE):
                errors.append(f"{task_id}: blocked without block-reason")
            if not re.search(rf"^blocked-by:\s*review:{re.escape(report_id)}\s*$", front, re.MULTILINE):
                errors.append(f"{task_id}: blocked without blocked-by: review:{report_id}")
        elif re.search(r"^(block-reason|blocked-by):", front, re.MULTILINE):
            errors.append(f"{task_id}: approved but still carries block-reason / blocked-by")


def main():
    """Parse arguments, run the checks, print PASS/FAIL, and exit with the matching code."""
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("report", help="path to the Review Report markdown file")
    parser.add_argument("--registry", help="docs/review/index.md; the report-id must appear in exactly one row")
    parser.add_argument("--tasks", help="docs/tasks/<work-id> folder to check statuses, checkboxes, and the index block")
    args = parser.parse_args()

    lines = [l.rstrip("\r") for l in read_text(args.report).split("\n") if not l.startswith("```") and l.strip() != "---"]
    head = top_level(lines)
    errors, warnings = [], []

    for key in ("report-id", "input-shape", "approval-status", "work-id"):
        if key not in head:
            errors.append(f"missing {key}")
    if errors:
        for message in errors:
            print(f"ERROR {message}")
        print("FAIL (cannot continue)")
        sys.exit(1)

    shape, report_id = head["input-shape"], head["report-id"]
    if shape not in SHAPES:
        errors.append(f"invalid input-shape {shape!r}")
    findings = parse_findings(lines)
    check_findings(findings, head.get("scope-creep-summary", ""), errors, warnings)
    check_rollup(lines, findings, errors)

    expected, blockers, majors, creep = derive(findings)
    status = head["approval-status"]
    if status not in VERDICTS:
        errors.append(f"invalid approval-status {status!r}")
    elif status != expected:
        errors.append(f"approval-status {status}, but {blockers} blocker / {majors} major / {creep} unaccepted creep give {expected}")
    if not head.get("rationale"):
        errors.append("missing rationale")

    verdicts = parse_verdicts(lines)
    if shape == "task-in-review":
        if not verdicts:
            errors.append("task-in-review report has no task-verdicts")
        check_verdicts(findings, verdicts, errors)
        if not any(re.match(r"^\s+tasks-updated:\s*true\s*$", line) for line in lines):
            errors.append("registration.tasks-updated must be true for task-in-review")
        if args.tasks:
            check_tasks(args.tasks, report_id, shape, verdicts, errors)
        else:
            warnings.append("--tasks not given; task statuses were not checked")
    elif verdicts:
        errors.append("task-verdicts are only valid for task-in-review input")
    elif args.tasks and shape == "work-linked":
        check_tasks(args.tasks, report_id, shape, {}, errors)

    if args.registry:
        rows = sum(1 for l in read_text(args.registry).splitlines() if report_id in l)
        if rows != 1:
            errors.append(f"registry has {rows} rows for {report_id}; expected exactly 1")

    for message in warnings:
        print(f"WARN  {message}")
    for message in errors:
        print(f"ERROR {message}")
    print(f"{'FAIL' if errors else 'PASS'} ({len(findings)} findings, {len(errors)} errors, {len(warnings)} warnings)")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
