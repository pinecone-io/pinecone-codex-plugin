#!/usr/bin/env python3
"""Validate every SKILL.md under skills/ against this plugin's conventions.

- frontmatter parses, has `name` and `description`
- `name` matches parent directory name
- `name` does NOT start with `pinecone-` (catches a mis-rendered sync)
- no `allowed-tools` frontmatter key (Codex doesn't use it)
- `description` is a single line, <=1000 chars
- body does not reference `AskUserQuestion`

Run from repo root:
    python3 scripts/check_skills.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SKILLS = REPO / "skills"

FRONTMATTER = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.DOTALL)


def parse_frontmatter(text: str) -> dict[str, str] | None:
    m = FRONTMATTER.match(text)
    if not m:
        return None
    out: dict[str, str] = {}
    for line in m.group(1).splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        out[key.strip()] = value.strip()
    return out


def main() -> int:
    errors: list[str] = []

    if not SKILLS.is_dir():
        print(f"FAIL: {SKILLS} does not exist", file=sys.stderr)
        return 1

    skill_dirs = sorted(d for d in SKILLS.iterdir() if d.is_dir())
    if not skill_dirs:
        errors.append("no skill directories found under skills/")

    for skill_dir in skill_dirs:
        skill_md = skill_dir / "SKILL.md"
        rel = skill_md.relative_to(REPO)

        if not skill_md.exists():
            errors.append(f"{rel}: missing SKILL.md")
            continue

        text = skill_md.read_text()
        fm = parse_frontmatter(text)
        if fm is None:
            errors.append(f"{rel}: missing or malformed YAML frontmatter")
            continue

        if "name" not in fm:
            errors.append(f"{rel}: frontmatter missing required field `name`")
        if "description" not in fm:
            errors.append(f"{rel}: frontmatter missing required field `description`")

        name = fm.get("name", "")
        if name.startswith("pinecone-"):
            errors.append(
                f"{rel}: name {name!r} still has `pinecone-` prefix — check skill_name in targets/codex.yaml upstream"
            )
        if name and name != skill_dir.name:
            errors.append(
                f"{rel}: frontmatter name {name!r} does not match directory {skill_dir.name!r}"
            )

        if "allowed-tools" in fm:
            errors.append(
                f"{rel}: `allowed-tools` is a Claude Code field; Codex skills should not declare it"
            )

        desc = fm.get("description", "")
        if "\n" in desc:
            errors.append(f"{rel}: description must be a single line")
        if len(desc) > 1000:
            errors.append(f"{rel}: description is {len(desc)} chars (max 1000)")

        body = text[len(FRONTMATTER.match(text).group(0)):] if FRONTMATTER.match(text) else text
        if "AskUserQuestion" in body:
            errors.append(
                f"{rel}: body references `AskUserQuestion`, which is a Claude-only tool name"
            )

    if errors:
        print("Skill validation failed:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1

    print(f"OK: {len(skill_dirs)} skill(s) under skills/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
