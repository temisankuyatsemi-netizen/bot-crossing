# Coding Tools & Resources

Tools for upgrading a Claude Code workflow. Install notes are taken from each project's README; review a project before installing it.

| # | Tool | What it does | Install (Claude Code) |
|---|------|--------------|-----------------------|
| 1 | [Ponytail](https://github.com/DietrichGebert/ponytail) | A prompt and skill that pushes agents to write less code ("the best code is the code you never wrote"). It also adds review and audit commands and a cost/usage band. | `/plugin marketplace add DietrichGebert/ponytail` then `/plugin install ponytail@ponytail` |
| 2 | [OmniRoute](https://github.com/diegosouzapw/OmniRoute) | A local AI gateway (`http://localhost:20128/v1`) that routes requests across many model providers and falls back automatically when a quota runs out. | npm (`omniroute`), Docker, or a build from source |
| 3 | [Graphify](https://github.com/Graphify-Labs/graphify) | Turns a codebase, plus its docs, SQL schemas, configs and PDFs, into a queryable knowledge graph. It uses local AST parsing and needs no vector store. | `uv tool install graphifyy` (two y's), `graphify install`, then `/graphify .` |
| 4 | [Agent Skills](https://github.com/addyosmani/agent-skills) | 25 engineering workflows (plan, build, test, review, ship) for AI coding agents. | `/plugin marketplace add addyosmani/agent-skills` then `/plugin install agent-skills@addy-agent-skills` |
