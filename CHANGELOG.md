# Changelog

## [1.1.0] - 2026-11-12

### Changed
- **The quickstart's Database path now builds a document index with integrated embedding.** One text field with `full_text_search` and `embed` serves two separate searches, by meaning and by exact terms, matching the [docs quickstart](https://docs.pinecone.io/guides/get-started/quickstart). The skill uses the Pinecone MCP's document-index tools (`create-document-index`, `upsert-documents`, `search-document-index`, added in `@pinecone-database/mcp` 0.4.0) when they're available, and falls back to bundled scripts when they aren't. The rerank step is gone.
- The quickstart and full-text-search scripts pin `pinecone==10.2.0`. Integrated embedding needs 10.1.0 or later.
- Full-text search `text` clauses use `fields: [...]`, since the singular `field` is deprecated. One clause can list several fields.

### Added
- `create_index.py` and `search.py` quickstart scripts, used when the MCP tools aren't available.
- `upsert.py --source` chunks your own `.md` and `.txt` files and upserts them in batches of 96. It skips hidden folders, dependency folders, and files that aren't UTF-8 text.
- An integrated embedding section in the full-text-search skill, covering the `embed` and `sparse_embed` clauses and their limits.

### Fixed
- The full-text-search skill no longer says integrated embedding can't be combined with `full_text_search`.
- Matches are read as `m.id` and `m.score`, replacing an incorrect rule against `m.score`.
- The quickstart scripts wait until documents are searchable instead of sleeping a fixed 10 seconds.
- Two broken links in the quickstart.

## [1.0.1] - 2026-09-21
- Use the `mcpServers` key in `.mcp.json` so Codex picks up the bundled Pinecone MCP server.
- Add a square plugin icon and logo.

## [1.0.0] - 2026-09-21
- First release of the official Pinecone Plugin for Codex.
- Nine skills: `quickstart`, `query`, `assistant`, `full-text-search`, `cli`, `mcp`, `docs`, `help`, `n8n`.
- Pinecone MCP server bundled via `.mcp.json` (`npx -y @pinecone-database/mcp`).
