#!/usr/bin/env python3
"""Coherence gate for runs produced by the /work skill.

Checks the task folder of a work-id: every task file has a valid status and exactly one
test file, the index checklist and each task's Acceptance Criteria checkbox match the task
status, no task is left in-progress, the Work Report block is not duplicated, and
(optionally) the plan's source coverage is reported against task outcomes.

Usage:
    python check-work.py <docs/tasks/work-id> [--plan <plan.md>] [--require-complete]

Exit codes: 0 = pass (warnings allowed), 1 = at least one error, 2 = usage/IO error.
Uses only the Python standard library.
"""

import argparse
import glob
import os
import re
import sys

STATUSES = {"not-started", "in-progress", "for-review", "completed", "blocked", "skipped"}
TASK_FILE = re.compile(r"^(T\d+[a-z]?)-.+\.md$")
INDEX_ROW = re.compile(r"^\s*-\s+\[( |x)\]\s+(T\d+[a-z]?)\b")
REPORT_BLOCK = re.compile(r"^##\s+Work Report\s+[—-]\s+(\S+)\s*$", re.MULTILINE)
UNIT_REF = re.compile(r"U\d+[a-z]?\b")


def read_text(path):
    """Read a UTF-8 text file; exit with code 2 when it cannot be read."""
    try:
        with open(path, encoding="utf-8") as handle:
            return handle.read()
    except (OSError, UnicodeDecodeError) as error:
        print(f"ERROR cannot read {path}: {error}")
        sys.exit(2)


def split_frontmatter(text):
    """Return (frontmatter, body) for a markdown file, or ("", text) when there is none."""
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", text, re.DOTALL)
    return (match.group(1), match.group(2)) if match else ("", text)


def scalar(frontmatter, key):
    """Return the unquoted value of a top-level `key: value` frontmatter line, or None."""
    match = re.search(rf"^{key}:\s*(.+?)\s*$", frontmatter, re.MULTILINE)
    return match.group(1).strip("\"'") if match else None


def test_files(frontmatter):
    """Return the paths listed under files.test (inline list or block list)."""
    inline = re.search(r"^\s*test:\s*\[(.*?)\]", frontmatter, re.MULTILINE)
    if inline:
        return [p.strip().strip("\"'`") for p in inline.group(1).split(",") if p.strip()]
    block = re.search(r"^\s*test:\s*\n((?:\s+-\s+.+\n?)+)", frontmatter, re.MULTILINE)
    if block:
        return [re.sub(r"^\s*-\s+", "", line).strip().strip("\"'`") for line in block.group(1).splitlines()]
    return []


def load_tasks(folder):
    """Parse every T<NN>-*.md task file in folder into {short-id: info}."""
    tasks = {}
    for path in sorted(glob.glob(os.path.join(folder, "T*.md"))):
        match = TASK_FILE.match(os.path.basename(path))
        if not match:
            continue
        frontmatter, body = split_frontmatter(read_text(path))
        box = re.search(r"^## Acceptance Criteria\s*\n+\s*-\s+\[( |x)\]", body, re.MULTILINE)
        tasks[match.group(1)] = {
            "path": path,
            "status": scalar(frontmatter, "status"),
            "unit": scalar(frontmatter, "unit"),
            "tests": test_files(frontmatter),
            "box": box.group(1) if box else None,
        }
    return tasks


def check_tasks(tasks, index_text, errors):
    """Validate per-task invariants and index/checkbox coherence; append problems to errors."""
    rows = {m.group(2): m.group(1) for line in index_text.splitlines() if (m := INDEX_ROW.match(line))}
    for task_id, info in tasks.items():
        status = info["status"]
        if status not in STATUSES:
            errors.append(f"{task_id}: invalid status {status!r}")
            continue
        if status == "in-progress":
            errors.append(f"{task_id}: left in-progress")
        if len(info["tests"]) != 1:
            errors.append(f"{task_id}: expected exactly one files.test, found {len(info['tests'])}")
        done = status == "completed"
        if task_id not in rows:
            errors.append(f"{task_id}: missing from index checklist")
        elif (rows[task_id] == "x") != done:
            errors.append(f"{task_id}: index checkbox [{rows[task_id]}] does not match status {status}")
        if info["box"] is None:
            errors.append(f"{task_id}: no Acceptance Criteria checkbox")
        elif (info["box"] == "x") != done:
            errors.append(f"{task_id}: Acceptance Criteria checkbox [{info['box']}] does not match status {status}")
    for task_id in rows:
        if task_id not in tasks:
            errors.append(f"{task_id}: index row has no task file")


def check_report_blocks(index_text, errors):
    """Fail when the same Work Report block appears more than once in the index."""
    seen = set()
    for review_id in REPORT_BLOCK.findall(index_text):
        if review_id in seen:
            errors.append(f"duplicate Work Report block for {review_id}")
        seen.add(review_id)


def parse_coverage(plan_text):
    """Return [(source item, title, outcome cell)] from the plan's Source Coverage table."""
    section = re.search(r"^## Source Coverage\s*\n(.*?)(?=^## |\Z)", plan_text, re.MULTILINE | re.DOTALL)
    if not section:
        return None
    rows = []
    for line in section.group(1).splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) >= 3 and line.strip().startswith("|") and not set(cells[0]) <= set("-: ") and cells[0].lower() != "source item":
            rows.append((cells[0], cells[1], cells[2]))
    return rows


def check_coverage(tasks, plan_text, errors, warnings):
    """Report each source item's task outcomes; unfinished items warn, orphan units error."""
    rows = parse_coverage(plan_text)
    if rows is None:
        errors.append("plan has no Source Coverage table")
        return
    by_unit = {}
    for task_id, info in tasks.items():
        if info["unit"]:
            by_unit.setdefault(re.match(r"U\d+", info["unit"]).group(0), []).append((task_id, info["status"]))
    covered_units = {re.match(r"U\d+", u).group(0) for _, _, outcome in rows
                     if not outcome.lower().startswith("excluded") for u in UNIT_REF.findall(outcome)}
    for task_id, info in tasks.items():
        if info["unit"] and re.match(r"U\d+", info["unit"]).group(0) not in covered_units:
            errors.append(f"{task_id}: unit {info['unit']} is not covered by any source item in the plan")
    print("Source coverage:")
    for item, title, outcome in rows:
        if outcome.lower().startswith("excluded"):
            print(f"  {item}  {title}: excluded")
            continue
        units = UNIT_REF.findall(outcome)
        results = [r for u in units for r in by_unit.get(re.match(r"U\d+", u).group(0), [])]
        if not results:
            errors.append(f"source item {item}: no task covers {', '.join(units) or outcome!r}")
            continue
        open_tasks = [f"{t}={s}" for t, s in results if s != "completed"]
        print(f"  {item}  {title}: {'done' if not open_tasks else 'OPEN ' + ', '.join(open_tasks)}")
        if open_tasks:
            warnings.append(f"source item {item} not fully completed ({', '.join(open_tasks)})")


def main():
    """Parse arguments, run the checks, print PASS/FAIL, and exit with the matching code."""
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("folder", help="task folder of the work-id, e.g. docs/tasks/2026-10-23-001")
    parser.add_argument("--plan", help="plan file whose Source Coverage is reported against task outcomes")
    parser.add_argument("--require-complete", action="store_true", help="treat any task that is not completed as an error")
    args = parser.parse_args()

    index_path = os.path.join(args.folder, "index.md")
    if not os.path.isdir(args.folder) or not os.path.isfile(index_path):
        print(f"ERROR {args.folder} is not a task folder with an index.md")
        sys.exit(2)

    tasks = load_tasks(args.folder)
    if not tasks:
        print(f"ERROR no task files found in {args.folder}")
        sys.exit(2)

    errors, warnings = [], []
    index_text = read_text(index_path)
    check_tasks(tasks, index_text, errors)
    check_report_blocks(index_text, errors)
    if args.plan:
        check_coverage(tasks, read_text(args.plan), errors, warnings)
    open_tasks = [f"{t}={i['status']}" for t, i in tasks.items() if i["status"] != "completed"]
    if open_tasks:
        (errors if args.require_complete else warnings).append("not completed: " + ", ".join(open_tasks))

    for message in warnings:
        print(f"WARN  {message}")
    for message in errors:
        print(f"ERROR {message}")
    print(f"{'FAIL' if errors else 'PASS'} ({len(tasks)} tasks, {len(errors)} errors, {len(warnings)} warnings)")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
