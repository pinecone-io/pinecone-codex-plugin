#!/usr/bin/env python3
"""Validate .agents/plugins/marketplace.json.

- File parses as JSON
- Top-level `name` and `plugins` present
- Each plugin entry has a `source` resolving to a directory containing
  .codex-plugin/plugin.json
- Each entry has `policy.installation` and `policy.authentication`
- `source.path` (or string `source`) starts with `./` and stays inside the
  marketplace root

Run from repo root:
    python3 scripts/check_marketplace.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
MARKETPLACE = REPO / ".agents" / "plugins" / "marketplace.json"


def main() -> int:
    if not MARKETPLACE.exists():
        print(f"OK: {MARKETPLACE.relative_to(REPO)} not present (optional)")
        return 0

    errors: list[str] = []

    try:
        data = json.loads(MARKETPLACE.read_text())
    except json.JSONDecodeError as e:
        print(f"FAIL: {MARKETPLACE} is not valid JSON: {e}", file=sys.stderr)
        return 1

    if "name" not in data:
        errors.append("missing top-level `name`")
    plugins = data.get("plugins")
    if not isinstance(plugins, list) or not plugins:
        errors.append("`plugins` must be a non-empty array")
        plugins = []

    marketplace_root = MARKETPLACE.parent.parent.parent.resolve()
    # .agents/plugins/marketplace.json → marketplace root is the repo root.
    # For repo-scoped marketplaces, that's REPO.

    for i, entry in enumerate(plugins):
        prefix = f"plugins[{i}]"
        if "name" not in entry:
            errors.append(f"{prefix}: missing `name`")

        source = entry.get("source")
        if isinstance(source, str):
            path = source
        elif isinstance(source, dict):
            if source.get("source") == "local":
                path = source.get("path")
                if not path:
                    errors.append(f"{prefix}.source: local entry missing `path`")
                    path = None
            else:
                # Non-local sources (git-subdir, url) — skip path resolution.
                path = None
        else:
            errors.append(f"{prefix}: `source` must be a string or object")
            path = None

        if path is not None:
            if not path.startswith("./"):
                errors.append(f"{prefix}.source.path: {path!r} must start with './'")
            else:
                resolved = (MARKETPLACE.parent / path.removeprefix("./")).resolve()
                # marketplace.json lives at $REPO/.agents/plugins/marketplace.json;
                # `./` in source.path is relative to the marketplace root (the repo root for repo marketplaces).
                resolved = (REPO / path.removeprefix("./")).resolve()
                try:
                    resolved.relative_to(REPO)
                except ValueError:
                    errors.append(f"{prefix}.source.path: {path!r} escapes the repo root")
                else:
                    if not resolved.is_dir():
                        errors.append(f"{prefix}.source.path: {path!r} is not an existing directory")
                    elif not (resolved / ".codex-plugin" / "plugin.json").exists():
                        errors.append(
                            f"{prefix}.source.path: {path!r} has no .codex-plugin/plugin.json"
                        )

        policy = entry.get("policy", {})
        for required in ("installation", "authentication"):
            if required not in policy:
                errors.append(f"{prefix}.policy: missing `{required}`")

    if errors:
        print("marketplace.json validation failed:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1

    print(f"OK: {MARKETPLACE.relative_to(REPO)} ({len(plugins)} plugin entry(s))")
    return 0


if __name__ == "__main__":
    sys.exit(main())
