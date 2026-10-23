#!/usr/bin/env python3
"""Coherence gate for the knowledge base written by the /learn skill.

Checks that every entry under docs/learn/<type>/ is well formed (frontmatter, body sections,
evidence, lineage links) and that docs/learn/index.md agrees with the entries on disk: one
five-field record per active entry, the applicability enum derived from the numeric scores,
By Category counts and rows, and By Domain coverage.

Usage:
    python check-learn.py <docs/learn directory>

Exit codes: 0 = pass (warnings allowed), 1 = at least one error, 2 = usage/IO error.
Uses only the Python standard library.
"""

import os
import re
import sys

TYPES = ["decision", "pattern", "gotcha", "workflow"]
SECTIONS = {
    "decision": ["Problem", "Solution", "Decision Rationale", "Application", "Related Learnings"],
    "pattern": ["Problem", "Pattern", "When to Apply", "Example", "Related Learnings"],
    "gotcha": ["Problem", "Trap", "Solution", "Prevention", "Related Learnings"],  # Source is optional
    "workflow": ["Convention", "Why", "How", "Related Learnings"],
}
OPTIONAL_SECTIONS = {"gotcha": ["Source"]}
APPLICABILITY = ["DIRECT", "RECOMMENDED", "CONTEXTUAL", "HISTORICAL", "INFORMATIONAL"]
SLUG = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
ABSOLUTE_PATH = re.compile(r"([A-Za-z]:[\\/]|/Users/|/home/)")
SESSION_WORDS = re.compile(r"\b(this session|today we|we just|in this run|the run just)\b", re.I)
MAX_SUMMARY = 240

errors, warnings = [], []


def err(where, message):
    """Record an error found in `where`."""
    errors.append(f"{where}: {message}")


def warn(where, message):
    """Record a warning found in `where`."""
    warnings.append(f"{where}: {message}")


def read_text(path):
    """Read a UTF-8 text file; exit with code 2 when it cannot be read."""
    try:
        with open(path, encoding="utf-8") as handle:
            return handle.read()
    except (OSError, UnicodeDecodeError) as error:
        print(f"ERROR cannot read {path}: {error}")
        sys.exit(2)


def strip_comment(value):
    """Drop a trailing ` # comment` that sits outside quotes."""
    quote = None
    for index, char in enumerate(value):
        if quote:
            if char == quote:
                quote = None
        elif char in "\"'":
            quote = char
        elif char == "#" and (index == 0 or value[index - 1] in " \t"):
            return value[:index]
    return value


def split_top(text):
    """Split on commas that are outside quotes and brackets."""
    parts, depth, quote, current = [], 0, None, ""
    for char in text:
        if quote:
            current += char
            if char == quote:
                quote = None
        elif char in "\"'":
            quote = char
            current += char
        elif char in "[{":
            depth += 1
            current += char
        elif char in "]}":
            depth -= 1
            current += char
        elif char == "," and depth == 0:
            parts.append(current)
            current = ""
        else:
            current += char
    if current.strip():
        parts.append(current)
    return parts


def parse_value(raw):
    """Parse a scalar, an inline list `[a, b]`, or an inline map `{a: 1}` into Python values."""
    raw = strip_comment(raw).strip()
    if raw.startswith("[") and raw.endswith("]"):
        return [parse_value(part) for part in split_top(raw[1:-1])]
    if raw.startswith("{") and raw.endswith("}"):
        mapping = {}
        for part in split_top(raw[1:-1]):
            key, _, value = part.partition(":")
            mapping[key.strip()] = parse_value(value)
        return mapping
    if len(raw) >= 2 and raw[0] == raw[-1] and raw[0] in "\"'":
        return raw[1:-1]
    if re.fullmatch(r"-?\d+", raw):
        return int(raw)
    return raw


def parse_frontmatter(lines):
    """Parse the lines between the `---` fences into a dict (scalars, inline and block maps/lists)."""
    data, index = {}, 0
    while index < len(lines):
        line = lines[index]
        index += 1
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        match = re.match(r"^([A-Za-z_][\w-]*):\s*(.*)$", line)
        if not match:
            continue
        key, value = match.group(1), strip_comment(match.group(2)).strip()
        if value:
            data[key] = parse_value(value)
            continue
        children = []
        while index < len(lines) and (not lines[index].strip() or lines[index].startswith((" ", "\t"))):
            if lines[index].strip():
                children.append(lines[index].strip())
            index += 1
        if children and children[0].startswith("- "):
            data[key] = [parse_value(child[2:]) for child in children if child.startswith("- ")]
        else:
            mapping = {}
            for child in children:
                name, _, rest = child.partition(":")
                mapping[name.strip()] = parse_value(rest)
            data[key] = mapping
    return data


def split_entry(text):
    """Return (frontmatter lines, body lines) or (None, lines) when the fences are missing."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None, lines
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            return lines[1:index], lines[index + 1:]
    return None, lines


def is_active(meta):
    """An entry is active unless it is obsolete or superseded."""
    return meta.get("status", "active") != "obsolete" and not meta.get("superseded-by")


def derive_applicability(project, general):
    """Map the numeric scores to the index enum (index-format.md)."""
    if project >= 8 and general >= 7:
        return "DIRECT"
    if project >= 5 and general >= 5:
        return "RECOMMENDED"
    if general >= 5:
        return "CONTEXTUAL"
    if general >= 3:
        return "HISTORICAL"
    return "INFORMATIONAL"


def check_source(where, source):
    """Validate the `source` block, including the evidence reference format."""
    if not isinstance(source, dict):
        err(where, "source must be a map with type, reference, extracted_at")
        return
    kind, reference = source.get("type"), str(source.get("reference", "")).strip()
    for field in ("type", "reference", "extracted_at"):
        if not str(source.get(field, "")).strip():
            err(where, f"source.{field} is missing")
    if kind not in ("commit", "candidate", "user"):
        err(where, f"source.type '{kind}' is not commit | candidate | user")
    elif kind == "commit" and not re.fullmatch(r"[0-9a-f]{7,40}", reference):
        err(where, f"source.reference '{reference}' is not a commit sha")
    elif kind == "candidate" and not re.fullmatch(r"[^#\s]+#\S+", reference):
        err(where, f"source.reference '{reference}' is not <report-id>#<candidate-key>")


def check_entry(path, type_dir, entries):
    """Validate one entry file; add its parsed frontmatter to `entries` keyed by slug."""
    where = os.path.relpath(path)
    text = read_text(path)
    front, body = split_entry(text)
    if front is None:
        err(where, "missing frontmatter fences")
        return
    meta = parse_frontmatter(front)
    slug = meta.get("slug")
    stem = os.path.splitext(os.path.basename(path))[0]
    for field in ("slug", "type", "domain", "applicability", "tags", "summary", "created_at", "updated_at", "source"):
        if field not in meta or meta[field] in ("", None, [], {}):
            err(where, f"required field '{field}' is missing or empty")
    if slug != stem:
        err(where, f"slug '{slug}' does not match the file name '{stem}'")
    if slug and not SLUG.match(str(slug)):
        err(where, f"slug '{slug}' is not kebab-case")
    if meta.get("type") != type_dir:
        err(where, f"type '{meta.get('type')}' does not match its folder '{type_dir}'")
    tags = meta.get("tags")
    if isinstance(tags, list) and not 2 <= len(tags) <= 6:
        err(where, f"tags has {len(tags)} items (need 2-6)")
    applicability = meta.get("applicability")
    if isinstance(applicability, dict):
        for side in ("current_project", "general"):
            value = applicability.get(side)
            if not isinstance(value, int) or not 0 <= value <= 10:
                err(where, f"applicability.{side} must be an integer 0-10")
    elif "applicability" in meta:
        err(where, "applicability must be a map with current_project and general")
    summary = str(meta.get("summary", ""))
    if len(summary) > MAX_SUMMARY:
        err(where, f"summary is {len(summary)} characters (max {MAX_SUMMARY})")
    for field, allowed in (("confidence", ("high", "medium", "low")), ("priority", ("important", "normal")),
                           ("status", ("active", "obsolete"))):
        if field in meta and meta[field] not in allowed:
            err(where, f"{field} '{meta[field]}' is not one of {', '.join(allowed)}")
    if "source" in meta:
        check_source(where, meta["source"])
    if meta.get("superseded-by") and meta.get("status") != "obsolete":
        err(where, "superseded-by is set but status is not obsolete")
    if ABSOLUTE_PATH.search(text):
        err(where, "contains an absolute path (use repository-relative paths)")
    if SESSION_WORDS.search("\n".join(body)):
        warn(where, "reads like a session log ('this session', 'we just'); entries state conclusions")
    required = SECTIONS.get(type_dir, [])
    headings = [line[3:].strip() for line in body if line.startswith("## ")]
    if not any(line.startswith("# ") for line in body):
        err(where, "missing the '# Title' heading")
    missing = [name for name in required if name not in headings]
    if missing:
        err(where, f"missing section(s): {', '.join(missing)}")
    for name in headings:
        if name not in required and name not in OPTIONAL_SECTIONS.get(type_dir, []):
            err(where, f"unexpected section '## {name}' for a {type_dir}")
    for name in required:
        if name in headings and name != "Related Learnings":
            start = body.index(f"## {name}") if f"## {name}" in body else None
            if start is not None:
                content = []
                for line in body[start + 1:]:
                    if line.startswith("#"):
                        break
                    content.append(line)
                if not "".join(content).strip():
                    err(where, f"section '{name}' is empty")
    if slug in entries:
        err(where, f"slug '{slug}' is also used by {entries[slug]['path']}")
    entries[slug] = {"meta": meta, "path": where, "type": type_dir, "body": body}


def check_lineage(entries):
    """Check related, superseded-by and also-seen-in links across entries."""
    for slug, entry in entries.items():
        meta, where = entry["meta"], entry["path"]
        for other in meta.get("related", []) or []:
            if other not in entries:
                err(where, f"related '{other}' is not an entry")
        target = meta.get("superseded-by")
        if target:
            if target not in entries:
                err(where, f"superseded-by '{target}' is not an entry")
            else:
                if slug not in (entries[target]["meta"].get("related") or []):
                    err(where, f"canonical '{target}' does not list '{slug}' in related")
                if not is_active(entries[target]["meta"]):
                    warn(where, f"canonical '{target}' is itself obsolete or superseded")
        seen = meta.get("also-seen-in")
        if seen is not None and not isinstance(seen, list):
            err(where, "also-seen-in must be a list")


def parse_index_records(lines):
    """Return the records of the fenced `entries:` YAML block, or None when there is no block."""
    inside, found, records, current = False, False, [], None
    for line in lines:
        if line.strip().startswith("```yaml"):
            inside = True
            continue
        if inside and line.strip().startswith("```"):
            break
        if not inside:
            continue
        if re.match(r"^entries:\s*\[\s*\]\s*$", line):
            return []
        if re.match(r"^entries:\s*$", line):
            found = True
            continue
        start = re.match(r"^\s*-\s+filename:\s*(.+?)\s*$", line)
        if start and found:
            current = {"filename": parse_value(start.group(1))}
            records.append(current)
            continue
        field = re.match(r"^\s+([a-z]+):\s*(.*?)\s*$", line)
        if field and current is not None and found:
            current[field.group(1)] = parse_value(field.group(2))
    return records if found else None


def check_index(root, entries):
    """Compare docs/learn/index.md with the active entries on disk."""
    path = os.path.join(root, "index.md")
    where = os.path.relpath(path)
    if not os.path.isfile(path):
        err(where, "index.md is missing")
        return
    lines = read_text(path).splitlines()
    if not any(line.startswith("**Last updated:**") for line in lines):
        err(where, "missing the '**Last updated:**' line")
    records = parse_index_records(lines)
    if records is None:
        err(where, "no fenced yaml 'entries:' block")
        return
    active = {slug: entry for slug, entry in entries.items() if is_active(entry["meta"])}
    by_file = {}
    for record in records:
        name = record.get("filename")
        if name in by_file:
            err(where, f"duplicate record for {name}")
        by_file[name] = record
        extra = set(record) - {"filename", "domain", "tags", "applicability", "summary"}
        missing = {"domain", "tags", "applicability", "summary"} - set(record)
        if extra:
            err(where, f"{name}: unexpected field(s) {', '.join(sorted(extra))}")
        if missing:
            err(where, f"{name}: missing field(s) {', '.join(sorted(missing))}")
    expected = {f"docs/learn/{entry['type']}/{slug}.md": slug for slug, entry in active.items()}
    for name in by_file:
        if name not in expected:
            err(where, f"record {name} has no active entry file")
    for name, slug in expected.items():
        if name not in by_file:
            err(where, f"active entry {name} has no index record")
            continue
        record, meta = by_file[name], active[slug]["meta"]
        applicability = meta.get("applicability") or {}
        if isinstance(applicability.get("current_project"), int) and isinstance(applicability.get("general"), int):
            want = derive_applicability(applicability["current_project"], applicability["general"])
            if record.get("applicability") != want:
                err(where, f"{name}: applicability {record.get('applicability')} should be {want}")
        elif record.get("applicability") not in APPLICABILITY:
            err(where, f"{name}: applicability is not one of {', '.join(APPLICABILITY)}")
        if record.get("domain") != meta.get("domain"):
            err(where, f"{name}: domain differs from the entry")
        if record.get("tags") != meta.get("tags"):
            err(where, f"{name}: tags differ from the entry")
        if record.get("summary") != meta.get("summary"):
            err(where, f"{name}: summary differs from the entry")
    check_tables(where, lines, active, by_file)


def check_tables(where, lines, active, by_file):
    """Check the By Category counts and rows and the By Domain bullets."""
    counts = {kind: sum(1 for entry in active.values() if entry["type"] == kind) for kind in TYPES}
    headings = {}
    section, rows = None, {}
    for line in lines:
        head = re.match(r"^###\s+(Decision|Pattern|Gotcha|Workflow)\s+\((\d+)\)\s*$", line)
        if head:
            section = head.group(1).lower()
            headings[section] = int(head.group(2))
            rows[section] = []
            continue
        if line.startswith("## "):
            section = None
        row = re.match(r"^\|\s*\[([^\]]+)\]\(([^)]+)\)\s*\|(.*)\|\s*$", line)
        if row and section:
            rows[section].append((row.group(2), [cell.strip() for cell in row.group(3).split("|")]))
    for kind in TYPES:
        if kind not in headings:
            err(where, f"missing the '### {kind.capitalize()} (N)' heading")
            continue
        if headings[kind] != counts[kind]:
            err(where, f"'{kind.capitalize()}' heading says {headings[kind]} but {counts[kind]} active entries exist")
        if len(rows.get(kind, [])) != counts[kind]:
            err(where, f"'{kind.capitalize()}' table has {len(rows.get(kind, []))} rows for {counts[kind]} active entries")
        for link, cells in rows.get(kind, []):
            slug = os.path.splitext(os.path.basename(link))[0]
            if slug not in active or active[slug]["type"] != kind:
                err(where, f"table row {link} is not an active {kind}")
            elif cells and cells[-1] != by_file.get(f"docs/learn/{kind}/{slug}.md", {}).get("applicability"):
                err(where, f"table row {link}: applicability differs from the YAML record")
    domains = {}
    for line in lines:
        bullet = re.match(r"^-\s+\*\*([^*]+?):\*\*\s*(.*)$", line)
        if bullet:
            domains[bullet.group(1).strip()] = [item.strip() for item in bullet.group(2).split(",") if item.strip()]
    listed = {slug for slugs in domains.values() for slug in slugs}
    for slug, entry in active.items():
        domain = entry["meta"].get("domain")
        if slug not in domains.get(domain, []):
            err(where, f"By Domain: '{slug}' is not listed under '{domain}'")
    for slug in listed - set(active):
        err(where, f"By Domain lists '{slug}', which is not an active entry")


def main(argv):
    """Run every check over the docs/learn directory given on the command line."""
    if len(argv) != 2 or not os.path.isdir(argv[1]):
        print(__doc__)
        return 2
    root = argv[1]
    entries = {}
    for kind in TYPES:
        folder = os.path.join(root, kind)
        if not os.path.isdir(folder):
            continue
        for name in sorted(os.listdir(folder)):
            if name.endswith(".md"):
                check_entry(os.path.join(folder, name), kind, entries)
    check_lineage(entries)
    check_index(root, entries)
    for message in warnings:
        print(f"WARN  {message}")
    for message in errors:
        print(f"ERROR {message}")
    print(f"{'FAIL' if errors else 'PASS'}: {len(entries)} entries, {len(errors)} error(s), {len(warnings)} warning(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
