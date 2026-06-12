#!/usr/bin/env python3
"""Validate that relative markdown links in skill docs resolve.

Scans every .md under skills/ plus README.md. For each `[text](path)` where path
is not absolute (no scheme, no leading slash, no anchor-only), checks that the
target file exists relative to the linking file's directory.

Anchor fragments (`#section`) and query strings are stripped before checking.

Run from repo root:
    python3 scripts/check_links.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

LINK = re.compile(r"\[([^\]]*)\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
SCHEME = re.compile(r"^[a-z][a-z0-9+.\-]*:")


def relevant_files() -> list[Path]:
    files = list((REPO / "skills").rglob("*.md"))
    readme = REPO / "README.md"
    if readme.exists():
        files.append(readme)
    return sorted(files)


def main() -> int:
    errors: list[str] = []
    checked = 0

    for md in relevant_files():
        text = md.read_text(errors="replace")
        for m in LINK.finditer(text):
            url = m.group(2).strip()
            if not url or url.startswith("#") or url.startswith("/"):
                continue
            if SCHEME.match(url) or url.startswith("//"):
                continue
            if url.startswith("mailto:"):
                continue
            target = url.split("#", 1)[0].split("?", 1)[0]
            if not target:
                continue
            checked += 1
            resolved = (md.parent / target).resolve()
            try:
                resolved.relative_to(REPO)
            except ValueError:
                errors.append(f"{md.relative_to(REPO)}: link {url!r} escapes the repo root")
                continue
            if not resolved.exists():
                errors.append(f"{md.relative_to(REPO)}: link {url!r} does not resolve (looked for {resolved.relative_to(REPO)})")

    if errors:
        print("Link validation failed:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1

    print(f"OK: {checked} relative link(s) checked")
    return 0


if __name__ == "__main__":
    sys.exit(main())
