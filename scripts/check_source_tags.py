#!/usr/bin/env python3
"""Validate that every Pinecone() source_tag uses the codex_plugin: namespace.

For each .py under skills/ that uses source_tag=, the literal must match:
    ^codex_plugin:[a-z0-9_]+(:[a-z0-9_]+)?$

This catches leakage from upstream / sibling plugins:
    pinecone_skills:*       (base repo)
    claude_code_plugin:*    (Claude plugin)
    cursor_plugin:*         (Cursor plugin)
    gemini_cli:*            (Gemini extension)

Run from repo root:
    python3 scripts/check_source_tags.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SKILLS = REPO / "skills"

SOURCE_TAG_LITERAL = re.compile(r"""source_tag\s*=\s*["']([^"']+)["']""")
VALID_TAG = re.compile(r"^codex_plugin:[a-z0-9_]+(:[a-z0-9_]+)?$")


def main() -> int:
    errors: list[str] = []
    checked = 0

    for py in sorted(SKILLS.rglob("*.py")):
        if "__pycache__" in py.parts:
            continue
        text = py.read_text(errors="replace")
        for m in SOURCE_TAG_LITERAL.finditer(text):
            checked += 1
            tag = m.group(1)
            rel = py.relative_to(REPO)
            if not VALID_TAG.match(tag):
                errors.append(
                    f"{rel}: source_tag {tag!r} must match ^codex_plugin:[a-z0-9_]+(:[a-z0-9_]+)?$"
                )

    if errors:
        print("source_tag validation failed:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1

    print(f"OK: {checked} source_tag literal(s) checked")
    return 0


if __name__ == "__main__":
    sys.exit(main())
