#!/usr/bin/env python3
"""Run every plugin validator and aggregate exit codes.

Run from repo root:
    python3 scripts/check_all.py
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
CHECKS = [
    "check_manifest.py",
    "check_marketplace.py",
    "check_mcp_config.py",
    "check_skills.py",
    "check_source_tags.py",
    "check_links.py",
]


def main() -> int:
    failed: list[str] = []
    for check in CHECKS:
        path = SCRIPTS / check
        if not path.exists():
            print(f"SKIP: {check} (missing)")
            continue
        print(f"--- {check}")
        result = subprocess.run([sys.executable, str(path)])
        if result.returncode != 0:
            failed.append(check)

    print()
    if failed:
        print(f"FAILED: {len(failed)}/{len(CHECKS)} check(s) failed: {', '.join(failed)}", file=sys.stderr)
        return 1
    print(f"PASSED: {len(CHECKS)} check(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
