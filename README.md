# UPF MCP

UPF MCP is a deterministic Model Context Protocol server for semiconductor
power-intent engineering.

It is meant to help AI agents and engineers:

- read and summarize UPF / IEEE 1801 intent,
- analyze RTL structure and power-domain crossings,
- validate power intent with deterministic rules,
- generate valid UPF from explicit intent and design structure,
- explain violations clearly before expensive EDA runs.

## Current status

This repository is still in the foundation stage.

The first milestone is to establish:

- project scope,
- glossary and terminology,
- package skeleton,
- typed internal models,
- a minimal parser and rule engine.

## Legal and data boundaries

- Project code is licensed under Apache-2.0.
- Do not copy restricted IEEE 1801 standard text into the repo.
- Do not embed proprietary vendor examples or customer UPF.
- Prefer public, licensed, or synthetic examples.
- Keep vendor-specific behavior in adapters, not the core model.

## Roadmap

The working roadmap lives in `PLAN.md`.

The current near-term sequence is:

1. Write foundational docs.
2. Create the Python package skeleton.
3. Define core data models.
4. Implement a minimal UPF parser and writer.
5. Build the first RTL-to-graph analysis and rule checks.

## Reference docs

- `PLAN.md` — staged roadmap and backlog
- `upf-mcp.md` — product framing and strategy
- `UPF_MCP_Research_and Dataset_Discovery.md` — research notes and source map

## Quick start

There is no runnable server yet.
When the implementation lands, this section will cover install and local
development commands.

## License

Apache-2.0. See [LICENSE](./LICENSE).
