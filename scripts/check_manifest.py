#!/usr/bin/env python3
"""Validate .codex-plugin/plugin.json against the Codex plugin spec.

Run from repo root:
    python3 scripts/check_manifest.py
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
MANIFEST = REPO / ".codex-plugin" / "plugin.json"

KEBAB = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
SEMVER = re.compile(r"^\d+\.\d+\.\d+$")
HEX_COLOR = re.compile(r"^#[0-9A-Fa-f]{6}$")


def fail(msg: str, errors: list[str]) -> None:
    errors.append(msg)


def check_path(value: str, field: str, errors: list[str]) -> None:
    if not value.startswith("./"):
        fail(f"{field}: path {value!r} must start with './'", errors)
        return
    resolved = (REPO / value.removeprefix("./")).resolve()
    try:
        resolved.relative_to(REPO)
    except ValueError:
        fail(f"{field}: path {value!r} escapes the plugin root", errors)
        return
    if not resolved.exists():
        fail(f"{field}: path {value!r} does not resolve to an existing file or directory", errors)


def main() -> int:
    errors: list[str] = []

    if not MANIFEST.exists():
        print(f"FAIL: {MANIFEST} does not exist", file=sys.stderr)
        return 1

    try:
        data = json.loads(MANIFEST.read_text())
    except json.JSONDecodeError as e:
        print(f"FAIL: {MANIFEST} is not valid JSON: {e}", file=sys.stderr)
        return 1

    for required in ("name", "version", "description", "skills"):
        if required not in data:
            fail(f"missing required field: {required}", errors)

    name = data.get("name", "")
    if name and not KEBAB.match(name):
        fail(f"name {name!r} is not lowercase kebab-case", errors)

    version = data.get("version", "")
    if version and not SEMVER.match(version):
        fail(f"version {version!r} does not match semver X.Y.Z", errors)

    # Required per OpenAI support (2026-09-21). Without it the plugin's skills and
    # MCP server do not get a local executor, so the bundled scripts cannot run.
    # It must be the boolean true, not the string "true".
    if data.get("requires_local_executor") is not True:
        fail(
            "requires_local_executor must be present at the top level and set to true, "
            f"got {data.get('requires_local_executor')!r}",
            errors,
        )

    for field in ("skills", "mcpServers", "apps", "hooks"):
        value = data.get(field)
        if isinstance(value, str):
            check_path(value, field, errors)
        elif isinstance(value, list):
            for i, item in enumerate(value):
                if isinstance(item, str):
                    check_path(item, f"{field}[{i}]", errors)

    interface = data.get("interface", {})
    for field in ("composerIcon", "logo"):
        if field in interface:
            check_path(interface[field], f"interface.{field}", errors)
    for i, shot in enumerate(interface.get("screenshots", [])):
        check_path(shot, f"interface.screenshots[{i}]", errors)

    brand = interface.get("brandColor")
    if brand and not HEX_COLOR.match(brand):
        fail(f"interface.brandColor {brand!r} must be #RRGGBB", errors)

    if errors:
        print("plugin.json validation failed:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1

    print(f"OK: {MANIFEST.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
