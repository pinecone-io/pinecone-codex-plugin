# Pinecone Plugin for Codex

A [Codex](https://developers.openai.com/codex) plugin that integrates [Pinecone](https://www.pinecone.io) vector database capabilities directly into your Codex session — eight reusable skills plus the official Pinecone MCP server, ready to install in a single step.

## Features

- **Pinecone Assistant** — fully managed RAG service for document Q&A with citations
- **Pinecone MCP server** — bundled, no extra setup; gives Codex tools to list, describe, create, upsert, and search indexes
- **Full-text search** — schema design, safe bulk ingestion, and BM25 / hybrid query construction over Pinecone's FTS preview API
- **Quickstart, query, CLI, docs, help, MCP reference** — bundled skills covering the common Pinecone workflows
- **Natural language friendly** — skills recognize phrases like "create an assistant from my docs," "query my index for X," "upload these files," without forcing slash-command syntax

## Installation

### 1. Add the marketplace and install the plugin

This plugin is distributed as an unofficial Codex marketplace. Add the marketplace, then install the `pinecone` plugin from it:

```bash
codex plugin marketplace add pinecone-io/pinecone-codex-plugin
codex plugin add pinecone --marketplace pinecone-codex-plugins
```

This registers the marketplace named `pinecone-codex-plugins` and installs the plugin named `pinecone`.

For local development from a clone, create a temporary marketplace wrapper. Codex expects local marketplace entries to point at a plugin folder such as `./plugins/pinecone`, so the wrapper copies this repo into that layout:

```bash
PLUGIN_REPO="$(pwd)"
LOCAL_MARKETPLACE="$(mktemp -d)/pinecone-codex-marketplace"
mkdir -p "$LOCAL_MARKETPLACE/plugins"
cp -R "$PLUGIN_REPO" "$LOCAL_MARKETPLACE/plugins/pinecone"
mkdir -p "$LOCAL_MARKETPLACE/.agents/plugins"
cp "$LOCAL_MARKETPLACE/plugins/pinecone/.agents/plugins/marketplace.json" "$LOCAL_MARKETPLACE/.agents/plugins/marketplace.json"
python3 - <<'PY' "$LOCAL_MARKETPLACE/.agents/plugins/marketplace.json"
import json
import sys
from pathlib import Path

path = Path(sys.argv[1])
data = json.loads(path.read_text())
data["plugins"][0]["source"] = {"source": "local", "path": "./plugins/pinecone"}
path.write_text(json.dumps(data, indent=2) + "\n")
PY

codex plugin marketplace remove pinecone-codex-plugins 2>/dev/null || true
codex plugin marketplace add "$LOCAL_MARKETPLACE"
codex plugin add pinecone --marketplace pinecone-codex-plugins
```

Verify the install:

```bash
codex plugin list | grep pinecone
```

### 2. Set your Pinecone API key

The bundled MCP server reads `PINECONE_API_KEY` from Codex's environment. Don't have a Pinecone account? Sign up free at [app.pinecone.io](https://app.pinecone.io/?sessionType=signup).

For Codex Desktop on macOS:

```bash
launchctl setenv PINECONE_API_KEY "your-api-key-here"
launchctl getenv PINECONE_API_KEY
```

Fully quit Codex if it is already running, then launch it again:

```bash
osascript -e 'quit app "Codex"'
open -a Codex
```

You can also launch Codex normally from Spotlight, Applications, or the Dock after setting the value with `launchctl`.

For Codex CLI:

```bash
export PINECONE_API_KEY="your-api-key-here"
codex
```

### 3. Run Pinecone's quickstart

Open Codex and start a new session. Then ask:

```text
Use Pinecone's quickstart to create an index, add sample data, and run my first search.
```

Codex should invoke `pinecone:quickstart`, verify the MCP connection, create an integrated index, upsert sample records, and run a search.

### Install `uv` (required for assistant and ingest scripts)

```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Homebrew
brew install uv

# Windows
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### Install the Pinecone CLI (optional)

```bash
brew tap pinecone-io/tap
brew install pinecone-io/tap/pinecone
```

## Skills

After installing, Codex will surface these skills. You can invoke them with `@pinecone` or by name (`$<skill>`), or just describe what you want and Codex will pick the right skill.

| Skill | What it does |
|---|---|
| `pinecone:help` | Overview of every skill plus the prerequisites — start here on a fresh install. |
| `pinecone:quickstart` | Step-by-step onboarding: create an integrated index, upsert data, run your first search. |
| `pinecone:query` | Search integrated indexes using natural language via the Pinecone MCP. |
| `pinecone:assistant` | Create, upload to, sync, chat with, and search a Pinecone Assistant. Natural-language driven. |
| `pinecone:full-text-search` | Build a BM25 / hybrid full-text-search index — schema design, safe bulk ingestion, query construction. Preview API. |
| `pinecone:cli` | Use the `pc` CLI for terminal-based index and vector management across all index types. |
| `pinecone:mcp` | Reference for all bundled Pinecone MCP tools and their parameters. |
| `pinecone:docs` | Curated links to official Pinecone documentation, organized by topic. |

## Bundled MCP tools

The plugin ships the Pinecone MCP server (`@pinecone-database/mcp` via `npx`). Once installed, the following tools are available to Codex automatically:

| Tool | Description |
|------|-------------|
| `list-indexes` | List all Pinecone indexes in your project. |
| `describe-index` | Get index config and namespaces. |
| `describe-index-stats` | Record counts and namespace stats. |
| `search-records` | Search records with optional filtering and reranking. |
| `cascading-search` | Multi-stage cascading retrieval. |
| `create-index-for-model` | Create an integrated index with a built-in embedding model. |
| `upsert-records` | Insert or update records. |
| `rerank-documents` | Rerank documents using a specified reranker. |
| `search-docs` / `ask-question-about-pinecone` | Pinecone docs RAG (Inkeep). |

Full MCP docs: [Pinecone MCP Server Guide](https://docs.pinecone.io/guides/operations/mcp-server).

## Troubleshooting

**"API key not found" or 401 errors.** For Codex Desktop on macOS, run `launchctl getenv PINECONE_API_KEY`. If empty, run `launchctl setenv PINECONE_API_KEY "your-api-key-here"`, fully quit Codex, and reopen it. For Codex CLI, check `echo $PINECONE_API_KEY` in the same shell where you run `codex`.

**MCP server not responding.** The server runs via `npx`; make sure Node.js is on `PATH`. Then check your API key is valid and restart Codex.

**Query skill doesn't return results.** `pinecone:query` only works with *integrated* indexes that use a hosted Pinecone embedding model. For external-embedding indexes (OpenAI, HuggingFace, etc.), use `pinecone:cli` or the MCP tools directly.

**Assistant skill errors out.** `uv` is required. Run `uv --version`; if missing, install per the instructions above and restart your terminal.

## Contributing

This repo receives most updates as automated PRs from [`pinecone-io/skills`](https://github.com/pinecone-io/skills) on branches named `sync/skills-*`. A GitHub Action (`contextualize-skills.yml`) adapts the incoming files to Codex conventions before a maintainer reviews and merges. Manual edits are welcome too — the validators in `scripts/check_*.py` run on every PR and document the conventions.

See [`docs/index.html`](./docs/index.html) (open it in a browser) for a full walkthrough of the build, validation, and release machinery.

## License

[MIT](./LICENSE).
