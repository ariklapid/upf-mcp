# AGENTS.md - UPF MCP Workspace

This repository is the seed of an industry-grade MCP server for Unified Power
Format (UPF / IEEE 1801) and power-intent engineering. Treat the current files
as strategic source material, not finished implementation.

The intended product shape is a standalone MCP project under the `ariklapid`
user, similar in posture to `pyslang-mcp`. Do not assume this repo should be
absorbed into the broader `asicdesign.ai` portal, workflows, or quizzes repos.

## Current Repository State

- GitHub repository: `git@github-ariklapid:ariklapid/upf-mcp.git`
- Default branch: `main`
- License: Apache-2.0
- Current state: foundation/documentation only. There is no runnable MCP server
  or Python package yet.
- Existing context files:
  - `README.md`
  - `AGENTS.md`
  - `PLAN.md`
  - `docs/glossary.md`
  - `upf-mcp.md`
  - `UPF_MCP_Research_and Dataset_Discovery.md`
  - `search-for-open-source-upf-parsers.md`

## Startup Context

Before making changes in this repo, read these files:

1. `AGENTS.md`
2. `README.md`
3. `PLAN.md`
4. `docs/glossary.md`
5. `upf-mcp.md`
6. `UPF_MCP_Research_and Dataset_Discovery.md`
7. `search-for-open-source-upf-parsers.md`

If a future `README.md`, `docs/`, or source tree is added, read the nearest
local guidance before editing that area.

## Mission

Build an MCP that helps AI agents:

- Read, parse, summarize, and explain UPF.
- Write valid UPF from explicit user intent and analyzed RTL structure.
- Understand power architecture concepts: power domains, voltage domains,
  supply sets, always-on logic, isolation, level shifting, retention, shutdown
  sequencing, power-state tables, and power crossings.
- Detect and explain power-intent issues before expensive downstream EDA runs.
- Act as a deterministic power-intent engine with an AI-facing interface, not
  as a generic "LLM that knows UPF".

The core differentiator is a rule-driven model of power intent that grounds
agent behavior in structural design facts and electrical constraints.

## Domain Meaning

In this repository, "UPF" means semiconductor Unified Power Format / IEEE 1801
unless explicitly stated otherwise. Do not confuse it with 5G User Plane
Function datasets, tooling, or papers.

## Architecture Direction

Design the system in separable layers:

- RTL structural analysis: parse and elaborate SystemVerilog, build hierarchy,
  instance, port, net, interface, clock/reset, and connectivity graphs. The
  initial preferred path is Python plus `pyslang`. `pyslang` is not the UPF
  parser; it supplies the elaborated RTL facts that UPF references by scope,
  instance, port, net, and control signal.
- UPF front end: parse supported UPF Tcl commands into a typed intermediate
  representation. Preserve source locations and comments where practical.
- Power intent information model: normalize domains, supply ports/nets, supply
  sets, power switches, power states, isolation strategies, level shifter
  strategies, retention strategies, always-on cells, and scope inheritance.
- Rule engine: deterministic checks for missing or inconsistent isolation,
  level shifting, retention, supply connectivity, domain crossings,
  hierarchical scope errors, voltage mismatches, control-signal reachability,
  and unsupported constructs.
- UPF writer: emit stable, formatted UPF from the intermediate model. The writer
  must avoid destructive rewrites of user files unless explicitly requested.
- MCP interface: expose focused `upf_*` tools, resources, and prompts that
  return compact structured data plus human-readable diagnostics.
- Dataset and evaluation pipeline: generate synthetic RTL + UPF + violation
  corpora and stable MCP evaluations.
- EDA adapters: build an open-source reproducible core first, with commercial
  tool adapters behind narrow interfaces from day one.

## Technical Defaults

- Prioritize UPF 2.1 and UPF 3.0 semantics for the first serious product
  target. Treat OpenROAD's supported UPF commands as an open-source validation
  and compatibility floor, not as the full project scope.
- Implement a project-owned Python Tcl/UPF front end. Keep it intentionally
  simple: parse Tcl command structure, whitelist supported UPF commands, build a
  typed project IR, preserve source locations, and report unsupported commands
  explicitly. Do not execute arbitrary Tcl.
- Treat `tclint` as the first Tcl syntax-layer spike candidate because it is
  Python-based, MIT-licensed, parses `.upf` files as Tcl, preserves source
  positions, and supports command plugins. The project should still own the UPF
  semantic collector, normalizer, typed IR, and diagnostics.
- Use OpenROAD's embedded UPF reader, SiFive's Apache-2.0 JavaScript `upf`
  tools, EDAUtils/Baya, and other report candidates as references and
  compatibility comparisons unless their licensing and APIs prove suitable.
- Prefer Python/FastMCP for the first implementation because `pyslang` is a
  likely foundation for SystemVerilog elaboration. This stack is approved for
  the initial implementation.
- Use Pydantic models for all public tool inputs, internal IR boundaries, and
  diagnostic objects.
- Use stdio transport for local developer use first. Add streamable HTTP only
  when multi-client or remote deployment requirements are clear.
- Name the server `upf_mcp`.
- Prefix MCP tools with `upf_`, for example:
  - `upf_analyze_rtl`
  - `upf_parse_upf`
  - `upf_validate_intent`
  - `upf_generate_upf`
  - `upf_explain_violation`
  - `upf_list_power_domains`
  - `upf_find_domain_crossings`
  - `upf_generate_synthetic_case`
- Tools that list data must support limits and pagination.
- Tool responses should support machine-readable JSON. Provide concise Markdown
  when helpful for humans.
- Add MCP tool annotations: read-only, destructive, idempotent, and open-world
  hints.

## Legal and Data Guardrails

- Project code is licensed under Apache-2.0.
- Do not embed, redistribute, scrape, or train on copyrighted IEEE 1801 standard
  text unless explicit license permission exists.
- Do not copy restricted vendor training material, paid standard examples, or
  confidential customer UPF.
- Safe inputs include original code, public open-source examples under compatible
  licenses, permissively licensed tool implementations, public tutorials where
  usage is allowed, and synthetic examples generated by this project.
- Private/internal UPF examples may be used locally for validation and learning,
  but must not be committed. Commit only public license-compatible examples and
  synthetic examples generated by this project.
- Record provenance for every dataset seed.
- Treat generated synthetic UPF as project-owned only if all source ingredients
  are license-compatible.
- Keep vendor-specific behavior in adapters or rule packs. Do not hard-code a
  commercial tool's quirks into the core model.

## Quality Bar

Industry-grade means:

- Deterministic behavior for parsing, linting, generation, and diagnostics.
- Source-location-aware errors wherever possible.
- Stable formatting and round-trip tests for supported UPF constructs.
- Golden tests for every rule.
- Synthetic valid and invalid cases for every major power-intent concept.
- Clear "unsupported construct" diagnostics instead of silent acceptance.
- Explicit assumptions in generated UPF.
- No hallucinated IEEE rules. If a rule is project-defined, label it that way.
- Minimal, focused MCP outputs that avoid flooding the LLM context window.
- Path validation and command-injection resistance for any file or tool access.
- Adapters that can run without commercial EDA tools for open-source CI.

## Testing Expectations

As the implementation grows, keep tests close to the behavior:

- Unit tests for UPF IR models, parsers, writers, and individual rules.
- Integration tests using tiny synthetic RTL designs.
- Golden text tests for generated UPF.
- Regression tests for invalid examples and expected diagnostics.
- MCP tool tests that verify schemas, annotations, response sizes, and error
  guidance.
- Evaluation questions that require realistic multi-tool reasoning by an agent.

## Repository Hygiene

- Keep source docs and generated data separated.
- Do not commit large generated corpora without an explicit decision. Prefer
  scripts plus small fixtures.
- Keep examples small, readable, and license-clean.
- Document every important design decision in `PLAN.md`, `README.md`, or an ADR
  under `docs/decisions/` once that directory exists.
- When adding code, follow the existing repo structure. If none exists, create a
  conservative Python package layout:
  - `src/upf_mcp/`
  - `tests/`
  - `examples/`
  - `docs/`
  - `scripts/`
  - `datasets/fixtures/`

## Check-In Policy

The repo is still in foundation mode, so direct pushes to `main` are acceptable
for explicit owner-requested bootstrap/docs/admin changes. Move quickly, but keep
history intentional.

From the first Python package skeleton onward, use pull requests for:

- Parser, IR, rule-engine, generator, MCP server, or adapter code.
- Dependency and packaging changes.
- Test fixtures and synthetic-data generators.
- CI, release, security, or branch-protection changes.
- Any change that affects public behavior or supported UPF semantics.

Target branch protection once CI exists:

- Require PRs into `main`.
- Require lint, type check, unit tests, parser golden tests, and MCP smoke tests.
- Require passing checks before merge.
- Keep direct pushes reserved for emergency/admin-only changes.

## Immediate Next Work

The next engineer/agent should move from planning to a minimal runnable
foundation:

1. Add `docs/scope.md` with the first supported UPF command subset and
   explicitly unsupported constructs.
2. Add `docs/decisions/0001-deterministic-rule-engine.md`.
3. Create the Python project skeleton: `pyproject.toml`, `src/upf_mcp/`,
   `tests/`, `examples/`, and `datasets/fixtures/`.
4. Add `upf_ping` through FastMCP and a CLI entry point.
5. Spike `tclint` as the Tcl syntax layer and decide whether to depend on it or
   vendor/build a smaller Tcl command tokenizer.
6. Define Pydantic models for UPF IR, diagnostics, RTL graph, and power graph.
7. Implement the first parser path for `set_scope` and `create_power_domain`.
8. Add the first synthetic two-domain RTL + UPF fixture.
9. Integrate enough `pyslang` to list hierarchy and top-level instance paths.
10. Implement the first validation path: parse existing UPF, summarize main
    domains/blocks, and report unsupported commands with source locations.

## Product Posture

The MVP should be narrow and trustworthy. A small subset of UPF with excellent
analysis, explanations, and tests is more valuable than broad command coverage
that produces unsafe power intent.

The first user workflow is an engineer using an AI agent to debug existing UPF
and understand the design's power intent. UPF generation is the second priority
and should be interactive: the engineer and agent refine strategy together, then
the deterministic MCP layer emits and validates reviewable UPF.

The first demo should lint an existing UPF and infer the main design blocks and
power crossings from it. The second demo should generate UPF from RTL.

For generation workflows, require explicit engineer-confirmed strategy input
first. MCP-inferred domains, voltages, states, isolation, and retention are
advisory suggestions only until confirmed by the engineer.

When uncertain, ask for the intended foundry/tool flow, UPF version, and target
user workflow before encoding assumptions.
