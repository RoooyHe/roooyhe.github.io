#!/usr/bin/env python3
"""
Update project tables in a Jekyll post based on the last commit date of each
referenced repository.

Sources supported:
  - GitHub:    https://github.com/{owner}/{repo}   (via `gh api`, falls back to public API)
  - AtomGit:   https://atomgit.com/{owner}/{repo}  (GitCode API v5, public repos need no token)

It parses pipe tables that have a "Status" column, fetches the latest commit
date for every repo URL found in the row, derives an activity status, and:
  - updates the "Status" column
  - adds a "Last Commit" column (YYYY-MM-DD) if not already present

Finally it commits and pushes when the file changed.

Usage:
  python3 tools/projects-status.py --dry-run   # preview without writing/committing
  python3 tools/projects-status.py             # write + commit + push

Config (edit constants below):
  STATUS_RULES : (status label, max age in days) — first matching wins.
  POST_PATH     : markdown file to update.
"""

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from urllib.request import Request, urlopen

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
POST_PATH = "_posts/2026-08-24-hello-world.md"

# (label, max_age_days) — None means "anything older".
STATUS_RULES = [
    ("Active", 30),
    ("Work in Progress", 180),
    ("Paused", 365),
    ("Archived", None),
]

GITHUB_RE = re.compile(r"github\.com/([^/\s\)\]]+)/([^/\s\)\]\)]+)")
ATOMGIT_RE = re.compile(r"atomgit\.com/([^/\s\)\]]+)/([^/\s\)\]\)]+)")


def now_utc():
    return datetime.now(timezone.utc)


def parse_date(s):
    """Parse an ISO-8601 timestamp (with optional offset) into aware datetime."""
    s = s.strip()
    try:
        dt = datetime.fromisoformat(s.replace("Z", "+00:00"))
    except ValueError:
        dt = datetime.fromisoformat(s[:19] + "+00:00")
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def fetch_github(owner, repo):
    """Return last-commit aware datetime for a GitHub repo, or None."""
    cmd = [
        "gh", "api",
        f"repos/{owner}/{repo}/commits?per_page=1",
        "--jq", ".[0].commit.committer.date",
    ]
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    except (FileNotFoundError, subprocess.TimeoutExpired):
        out = None
    if out and out.returncode == 0 and out.stdout.strip():
        return parse_date(out.stdout.strip())
    # Fallback: unauthenticated public API (60 req/h).
    url = f"https://api.github.com/repos/{owner}/{repo}/commits?per_page=1"
    req = Request(url, headers={"User-Agent": "projects-status/1.0"})
    try:
        with urlopen(req, timeout=30) as resp:
            data = json.load(resp)
        if isinstance(data, list) and data:
            return parse_date(data[0]["commit"]["committer"]["date"])
    except Exception:
        pass
    return None


def fetch_atomgit(owner, repo):
    """Return last-commit aware datetime for an AtomGit/GitCode repo, or None."""
    url = f"https://atomgit.com/api/v5/repos/{owner}/{repo}/commits?per_page=1"
    headers = {"User-Agent": "projects-status/1.0"}
    token = os.environ.get("ATOMGIT_TOKEN")
    if token:
        headers["private-token"] = token
        headers["PRIVATE-TOKEN"] = token
    req = Request(url, headers=headers)
    try:
        with urlopen(req, timeout=30) as resp:
            data = json.load(resp)
        if isinstance(data, list) and data:
            return parse_date(data[0]["commit"]["committer"]["date"])
    except Exception:
        pass
    return None


def status_for_age(days):
    for label, max_days in STATUS_RULES:
        if max_days is None or days <= max_days:
            return label
    return STATUS_RULES[-1][0]


def find_repos(text):
    """Return ordered unique (host, owner, repo) tuples found in text."""
    seen, result = set(), []
    for m in GITHUB_RE.finditer(text):
        key = ("github", m.group(1).lower(), m.group(2).lower().rstrip("."))
        if key not in seen:
            seen.add(key)
            result.append(key)
    for m in ATOMGIT_RE.finditer(text):
        key = ("atomgit", m.group(1).lower(), m.group(2).lower().rstrip("."))
        if key not in seen:
            seen.add(key)
            result.append(key)
    return result


def split_row(line):
    """Split a pipe-table row into trimmed cells, dropping the empty ends."""
    cells = [c.strip() for c in line.strip().strip("|").split("|")]
    return cells


def process_tables(text, fetchers):
    """Return new markdown text and a human-readable change log."""
    lines = text.split("\n")
    out = []
    changes = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip().startswith("|"):
            out.append(line)
            i += 1
            continue

        # Collect a contiguous table block.
        block = []
        while i < len(lines) and lines[i].strip().startswith("|"):
            block.append(lines[i])
            i += 1

        header = split_row(block[0])
        if "Status" not in header and "Last Commit" not in header:
            out.extend(block)
            continue

        status_idx = header.index("Status") if "Status" in header else None
        last_idx = header.index("Last Commit") if "Last Commit" in header else None
        url_idx = header.index("URL") if "URL" in header else None
        has_last_col = last_idx is not None

        # If no Last Commit column, append one to header + separator.
        if not has_last_col:
            header.append("Last Commit")
            block[0] = "|" + "|".join(header) + "|"
            block[1] = "|" + "|".join(["---"] * len(header)) + "|"
            last_idx = len(header) - 1
            has_last_col = True

        new_block = [block[0], block[1]]
        for row in block[2:]:
            cells = split_row(row)
            # Normalize width to header length.
            while len(cells) < len(header):
                cells.append("")
            cells = cells[: len(header)]

            # Only scan the URL column (and project-name link column) for
            # repo URLs; never the Description column, which may reference
            # upstream dependencies like github.com/alibaba/MNN.
            scan_text = cells[url_idx] if url_idx is not None and url_idx < len(cells) else ""
            scan_text += " " + cells[0]
            repos = find_repos(scan_text)
            dates = []
            for host, owner, repo in repos:
                d = fetchers[(host, owner, repo)]
                if d is not None:
                    dates.append(d)
            last_dt = max(dates) if dates else None

            name = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", cells[0]) or cells[0]
            if last_dt is not None:
                days = (now_utc() - last_dt).days
                new_status = status_for_age(days)
                cells[last_idx] = last_dt.strftime("%Y-%m-%d")
                if status_idx is not None:
                    old_status = cells[status_idx]
                    if old_status != new_status:
                        changes.append(
                            f"{name}: {old_status} -> {new_status} "
                            f"(last commit {cells[last_idx]}, {days}d ago)"
                        )
                    cells[status_idx] = new_status
            else:
                cells[last_idx] = "N/A"

            new_block.append("|" + "|".join(cells) + "|")

        out.extend(new_block)

    return "\n".join(out) + "\n", changes


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="preview only, no write/commit")
    args = ap.parse_args()

    with open(POST_PATH, encoding="utf-8") as f:
        text = f.read()

    # Discover every repo and fetch its last commit once.
    fetchers = {}
    for host, owner, repo in find_repos(text):
        if host == "github":
            fetchers[(host, owner, repo)] = fetch_github(owner, repo)
        else:
            fetchers[(host, owner, repo)] = fetch_atomgit(owner, repo)

    new_text, changes = process_tables(text, fetchers)

    for (host, owner, repo), dt in fetchers.items():
        print(f"{host:8s} {owner}/{repo:40s} "
              f"{dt.strftime('%Y-%m-%d') if dt else 'FETCH_FAILED'}")

    if not changes:
        print("\nNo changes.")
        return 0

    print("\nChanges:")
    for c in changes:
        print("  -", c)

    if args.dry_run:
        print("\n[dry-run] not writing file.")
        return 0

    if new_text == text:
        print("\nNo content change after processing; skipping commit.")
        return 0

    with open(POST_PATH, "w", encoding="utf-8") as f:
        f.write(new_text)

    subprocess.run(["git", "add", POST_PATH], check=True)
    subprocess.run(
        ["git", "commit", "-m", "chore: refresh project status & last commit"],
        check=True,
    )
    subprocess.run(["git", "push"], check=True)
    print("\nCommitted and pushed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
