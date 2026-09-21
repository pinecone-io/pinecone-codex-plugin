#!/usr/bin/env python3
"""Validate bundled MCP config against the current Codex plugin docs.

The Codex plugin directory requires `.mcp.json` to be a JSON object with a
top-level `mcpServers` map. An earlier version of this file required the
snake_case `mcp_servers` instead, which is how a non-compliant config passed
every check until the directory review caught it.

Run from repo root:
    python3 scripts/check_mcp_config.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
MCP = REPO / ".mcp.json"


def server_map(payload: dict) -> dict | None:
    value = payload.get("mcpServers")
    return value if isinstance(value, dict) else None


def main() -> int:
    if not MCP.exists():
        print(f"OK: {MCP.relative_to(REPO)} not present (optional)")
        return 0

    errors: list[str] = []

    try:
        payload = json.loads(MCP.read_text())
    except json.JSONDecodeError as e:
        print(f"FAIL: {MCP.relative_to(REPO)} is not valid JSON: {e}", file=sys.stderr)
        return 1

    if not isinstance(payload, dict):
        errors.append(".mcp.json must contain a JSON object")
        servers = {}
    else:
        servers = server_map(payload)
        if "mcpServers" not in payload:
            errors.append("`mcpServers` is required at the top level")
            servers = {}
        elif servers is None:
            errors.append("`mcpServers` must be an object")
            servers = {}
        if "mcp_servers" in payload:
            errors.append("`mcp_servers` is not recognised; the key is `mcpServers`")

    if not servers:
        errors.append("no MCP servers configured")

    for name, server in servers.items():
        if not isinstance(name, str) or not name:
            errors.append("MCP server names must be non-empty strings")
            continue
        if not isinstance(server, dict):
            errors.append(f"server {name!r} must be an object")
            continue
        has_stdio = isinstance(server.get("command"), str) and bool(server["command"])
        has_http = isinstance(server.get("url"), str) and bool(server["url"])
        if not has_stdio and not has_http:
            errors.append(f"server {name!r} must define `command` or `url`")
        if "cwd" in server and "CLAUDE_PLUGIN_ROOT" in str(server["cwd"]):
            errors.append(f"server {name!r} uses stale CLAUDE_PLUGIN_ROOT cwd")
        env_vars = server.get("env_vars")
        if env_vars is not None and not (
            isinstance(env_vars, list) and all(isinstance(item, str) for item in env_vars)
        ):
            errors.append(f"server {name!r} `env_vars` must be an array of strings")

    if errors:
        print("MCP config validation failed:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1

    print(f"OK: {MCP.relative_to(REPO)} ({len(servers)} server(s))")
    return 0


if __name__ == "__main__":
    sys.exit(main())
