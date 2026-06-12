# Changelog

## [0.1.0] - 2026-05-20
- Initial release of the Pinecone Codex plugin.
- Eight skills synced from `pinecone-io/skills` and contextualized for Codex: `quickstart`, `query`, `assistant`, `full-text-search`, `cli`, `mcp`, `docs`, `help`.
- Pinecone MCP server bundled via `.mcp.json` (`npx -y @pinecone-database/mcp`).
- GitHub Actions wired up: `contextualize-skills.yml` adapts incoming sync PRs, `release.yml` bumps version and tags releases, `validate.yml` runs plugin validators on every PR.
- Validator scripts under `scripts/` enforce Codex plugin conventions on every change.
