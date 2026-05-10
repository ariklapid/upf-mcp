# PLAN.md - UPF MCP Roadmap

## North Star

Create an industry-grade MCP server that lets AI agents safely reason about,
read, validate, generate, explain, and iteratively refine semiconductor power
intent expressed in UPF / IEEE 1801.

The product should become a deterministic power-intent engineering layer exposed
through MCP. The LLM should handle interaction, explanation, and strategy
exploration; the MCP should provide grounded facts, rule checks, structured
models, and safe generation.

## Strategic Thesis

Current LLMs have weak public exposure to real UPF and power-aware verification
flows. Public "UPF" datasets are mostly 5G User Plane Function material and are
irrelevant to hardware power intent. The useful path is therefore:

- Build a precise intermediate representation for RTL structure and UPF intent.
- Encode deterministic power rules outside the LLM.
- Generate license-clean synthetic RTL + UPF + diagnostics datasets.
- Expose the result through compact MCP tools that agents can compose.
- Build an open-source reproducible core first, with commercial-flow adapter
  boundaries from day one.

## Definition of Industry-Grade

The MCP is industry-grade when it can:

- Parse and normalize a meaningful subset of UPF with source locations.
- Analyze elaborated RTL hierarchy and signal connectivity.
- Build a power architecture graph across RTL and UPF.
- Detect unsafe domain crossings and missing strategies deterministically.
- Generate stable, reviewable UPF for supported patterns.
- Explain violations in engineering language with evidence and source paths.
- Integrate into an agent loop without flooding context.
- Run repeatable CI on open-source fixtures.
- Maintain clean data provenance and avoid restricted IEEE/vendor content.
- Support extensible rule packs for methodology and tool-specific behavior.

## Assumed Initial Stack

- Language: Python.
- MCP framework: FastMCP from the official Python MCP SDK.
- Validation: Pydantic v2.
- RTL analysis: `pyslang`.
- UPF target: prioritize IEEE 1801 / UPF 2.1 and 3.0. Use OpenROAD's UPF
  support as an open-source compatibility floor and test reference, not as the
  full language scope.
- UPF parsing: implement a project-owned Python Tcl/UPF front end. Keep it
  intentionally simple: parse Tcl command structure, whitelist supported UPF
  commands, build a typed project IR, preserve source locations, and report
  unsupported commands explicitly. Do not execute arbitrary Tcl. Spike `tclint`
  first as the Tcl syntax-layer candidate, while keeping the UPF semantic
  collector, normalizer, typed IR, and diagnostics project-owned. Use OpenROAD's
  embedded UPF reader, SiFive's Apache-2.0 JavaScript `upf` tools, EDAUtils/Baya,
  and other report candidates as references and compatibility comparisons unless
  their licensing and APIs prove suitable.
- Local transport: stdio.
- Later transport: streamable HTTP for enterprise/shared deployments.
- CI: pytest, ruff, mypy or pyright, golden fixture tests, MCP inspector smoke.

These are defaults, not immutable decisions. Revisit only if implementation
evidence shows the stack cannot support the target workflow.

## Phase 0: Product and Scope Foundation (0-5%)

Goal: turn the idea into a crisp engineering target.

Deliverables:

- `AGENTS.md` with local development guidance.
- `PLAN.md` with staged roadmap.
- `README.md` with project mission, quick start placeholder, and legal warning.
- `docs/glossary.md` defining UPF, power domain, voltage domain, supply set,
  isolation, level shifter, retention, always-on, PST, power switch, and
  crossing.
- `docs/scope.md` listing supported, planned, and explicitly unsupported UPF
  constructs.
- Initial ADR: "Deterministic rule engine plus LLM interface."

Decisions to make:

- Target UPF baseline: 2.1 and 3.0 first. Defer full 4.0 coverage until the
  core parser, rule engine, and generator are stable.
- First target users: RTL designers, low-power verification engineers, CAD/EDA
  methodology owners, or AI coding agents.
- First target flow: open-source only, Synopsys-like, Cadence-like,
  Siemens-like, or adapter-neutral.

Exit criteria:

- The project can be explained in one paragraph.
- The MVP command subset and non-goals are explicit.
- Legal/data boundaries are written down.

## Phase 1: Repo and Tooling Skeleton (5-10%)

Goal: make the project buildable and testable.

Deliverables:

- Python package skeleton under `src/upf_mcp/`.
- `pyproject.toml` with pinned minimum Python version and dev dependencies.
- `tests/` with smoke tests.
- CLI entry point for local experiments, for example `upf-mcp`.
- MCP server entry point, initially exposing `upf_ping` and metadata.
- Logging configured to stderr for stdio safety.
- CI workflow for lint, type check, and tests.

Exit criteria:

- A fresh clone can install dependencies and run tests.
- MCP inspector can connect to the server.
- Tool schemas are validated by tests.

## Phase 2: Core Data Models (10-18%)

Goal: establish typed internal representations before parsing complexity grows.

Deliverables:

- RTL design graph models:
  - design
  - module
  - instance
  - port
  - net
  - connection
  - clock/reset candidate
  - hierarchy path
- UPF intent models:
  - scope
  - power domain
  - supply port
  - supply net
  - supply set
  - power state
  - isolation strategy
  - level shifter strategy
  - retention strategy
  - power switch
  - always-on attribute
- Cross-domain graph models:
  - endpoint
  - crossing
  - source domain
  - sink domain
  - voltage relation
  - power-state relation
  - required protection
- Diagnostic model:
  - rule id
  - severity
  - message
  - evidence
  - source location
  - suggested fix
  - confidence and assumptions

Exit criteria:

- Models serialize to stable JSON.
- Unit tests cover validation and edge cases.
- The models can represent the examples from `upf-mcp.md`.

## Phase 3: Minimal UPF Front End (18-28%)

Goal: parse a trustworthy subset of UPF into the project IR.

Initial command subset:

- `set_scope`
- `create_power_domain`
- `create_supply_port`
- `create_supply_net`
- `connect_supply_net`
- `create_supply_set`
- `associate_supply_set`
- `add_power_state`
- `set_isolation`
- `set_isolation_control`
- `set_level_shifter`
- `set_retention`
- `set_retention_control`

Deliverables:

- UPF lexer/parser approach selected and documented.
- Parser that preserves source locations.
- Explicit unsupported-command diagnostics.
- Normalizer that resolves scope and hierarchy references where possible.
- UPF writer for the supported subset.
- Round-trip tests for parse -> IR -> write -> parse.

Exit criteria:

- Supported constructs parse deterministically.
- Unsupported constructs fail usefully.
- Generated UPF is stable enough for code review diffs.

## Phase 4: RTL Structural Analysis MVP (28-38%)

Goal: derive a reliable structural graph from small SystemVerilog projects.

Deliverables:

- `pyslang` integration spike.
- File-list handling.
- Include directory and define handling.
- Top-module selection.
- Elaborated hierarchy extraction.
- Port direction and width extraction.
- Instance connection extraction.
- Basic clock/reset/enable signal heuristics.
- CLI and MCP tool for RTL analysis.

Initial MCP tool:

- `upf_analyze_rtl`

Exit criteria:

- Works on small synthetic SystemVerilog examples.
- Produces stable JSON graph output.
- Emits useful diagnostics for parse/elaboration failures.

## Phase 5: Power Architecture Graph (38-48%)

Goal: join RTL structure and UPF intent into one analyzable graph.

Deliverables:

- Domain assignment resolver.
- Scope inheritance resolver.
- Supply set association resolver.
- Signal endpoint domain mapper.
- Voltage-domain model.
- Always-on domain annotation.
- Power-state relation model.
- Domain crossing detector.

MCP tools:

- `upf_parse_upf`
- `upf_build_power_graph`
- `upf_list_power_domains`
- `upf_find_domain_crossings`

Exit criteria:

- Given RTL plus UPF, the MCP can list domains and crossings.
- Crossings include source/sink hierarchy paths and relevant supplies.
- Ambiguous mappings are reported, not guessed silently.

## Phase 6: Rule Engine MVP (48-60%)

Goal: catch the highest-value low-power bugs with deterministic checks.

Initial rule families:

- Missing isolation from switchable/off domain to active domain.
- Missing level shifter across incompatible voltage domains.
- Retention required but strategy missing for marked stateful blocks.
- Isolation control signal sourced from a domain that may be off.
- Level shifter placement inconsistent with source/sink strategy.
- Domain without primary supply.
- Instance matched by multiple conflicting domains.
- UPF references unresolved RTL hierarchy path.

Deliverables:

- Rule registry.
- Rule severity system.
- Rule documentation.
- Diagnostic generation with evidence.
- Unit tests and invalid fixtures per rule.
- Configurable methodology policy file.

MCP tool:

- `upf_validate_intent`

Exit criteria:

- Every rule has valid and invalid fixtures.
- Diagnostics point to source files and hierarchy paths.
- False positives are documented and configurable.

## Phase 7: UPF Generation MVP (60-68%)

Goal: generate reviewable UPF for simple but realistic power architectures.

Deliverables:

- Strategy config schema:
  - domain partition
  - supplies
  - voltages
  - shutdown states
  - isolation policy
  - level shifter policy
  - retention policy
  - naming conventions
- Generator for the Phase 3 supported command subset.
- Generated comments that record assumptions without copying standards text.
- Validation loop: generated UPF must pass the project rule engine.
- Diff mode against existing UPF.

MCP tools:

- `upf_generate_upf`
- `upf_suggest_power_strategy`
- `upf_diff_intent`

Exit criteria:

- Agent can generate a simple multi-domain UPF from explicit strategy config.
- The generator refuses under-specified unsafe requests.
- Generated output is stable and readable.

## Phase 8: Explanation and Agent UX (68-74%)

Goal: make the MCP usable by AI agents and human engineers.

Deliverables:

- Diagnostic explanations with concise engineering rationale.
- "Next action" hints in tool results.
- Prompt templates:
  - explain a UPF file
  - review a power architecture
  - propose missing isolation
  - debug a violation
  - summarize assumptions
- Response size budgets and truncation strategy.
- Markdown and JSON response modes.

MCP tool:

- `upf_explain_violation`

Exit criteria:

- Explanations are grounded in diagnostic evidence.
- Tool output is compact enough for agent loops.
- No explanation invents unsupported rules.

## Phase 9: Synthetic Dataset Pipeline (74-82%)

Goal: create license-clean training and evaluation material.

Deliverables:

- Seed RTL fixture library.
- Synthetic hierarchy generator.
- Domain partition generator.
- Voltage and power-state generator.
- Valid UPF generator.
- Bug injector:
  - remove isolation
  - wrong isolation clamp
  - missing level shifter
  - conflicting domain assignment
  - missing supply association
  - retention control unreachable
  - invalid hierarchy reference
- Dataset manifest with provenance and license fields.
- Small committed fixture set plus script to generate larger local corpora.

MCP tools or scripts:

- `upf_generate_synthetic_case`
- `upf_validate_dataset_case`

Exit criteria:

- Dataset can generate reproducible valid/invalid cases.
- Every generated case has expected diagnostics.
- No restricted source material is required.

## Phase 10: Evaluations and Benchmarks (82-88%)

Goal: measure whether AI agents are better with the MCP than without it.

Deliverables:

- 10-20 stable read-only MCP evaluation questions.
- Task suites:
  - parse and summarize UPF
  - find unsafe crossing
  - propose missing strategy
  - compare two UPF files
  - explain downstream error
  - generate simple UPF from architecture
- Golden answers.
- Baseline comparison against no-tool LLM behavior.
- Metrics:
  - correctness
  - diagnostic precision
  - context tokens returned
  - tool calls per solved task
  - runtime

Exit criteria:

- Evaluations catch regressions.
- The MCP shows measurable benefit on realistic tasks.
- Failures feed back into rule and UX improvements.

## Phase 11: EDA Flow Integrations (88-94%)

Goal: connect the MCP to real tool feedback while preserving adapter boundaries.

Open-source first:

- OpenROAD UPF read/reference behavior.
- Yosys or synthesis-adjacent experiments where applicable.
- Verilator for simulation-adjacent fixture validation.
- Optional SiliconCompiler/Hammer integration for flow orchestration.

Commercial later, behind adapters:

- Synopsys-style low-power verification flow.
- Cadence-style flow.
- Siemens/Questa-style flow.

Deliverables:

- Adapter interface.
- Tool availability detection.
- Log summarizer for massive reports.
- Structured extraction of errors, warnings, rule ids, object paths, and source
  locations.
- No hard dependency on commercial tools in CI.

MCP tools:

- `upf_run_flow_check`
- `upf_summarize_tool_log`
- `upf_map_tool_error`

Exit criteria:

- Open-source flow checks run in CI or local dev.
- Commercial adapters can be enabled locally without polluting the core.
- Tool logs are reduced to actionable summaries.

## Phase 12: Hardening, Security, and Enterprise Readiness (94-98%)

Goal: make the MCP safe for real repositories and large designs.

Deliverables:

- Path sandboxing and allow-list config.
- File-size and timeout limits.
- Tool-call budget controls.
- Cache for parsed RTL and UPF graphs.
- Incremental analysis support.
- Structured telemetry without source exfiltration.
- Redaction of sensitive paths or identifiers where configured.
- Streamable HTTP deployment option if required.
- Authentication and authorization for remote mode.
- Performance tests on larger synthetic designs.

Exit criteria:

- The MCP can run on a non-trivial design without runaway context or runtime.
- Security review issues are tracked and closed.
- Remote deployment has clear auth and network boundaries.

## Phase 13: Public/Private Release Line (98-100%)

Goal: prepare a release that can be trusted by engineers and extended by teams.

Deliverables:

- Stable README and installation docs.
- Versioned command support matrix.
- Rule reference documentation.
- Example designs and walkthroughs.
- MCP client configuration examples.
- Contributor guide.
- License and data provenance documentation.
- Release checklist.

Exit criteria:

- New users can run the MCP on examples in under 10 minutes.
- The supported subset is clear.
- Known limitations are explicit.
- The project has a path for private enterprise rule packs and adapters.

## Initial MCP Tool Surface

Start small:

- `upf_ping`: server health and version.
- `upf_analyze_rtl`: parse/elaborate RTL and return a design graph.
- `upf_parse_upf`: parse UPF into a normalized IR.
- `upf_build_power_graph`: combine RTL graph and UPF IR.
- `upf_find_domain_crossings`: list crossings with domain and voltage context.
- `upf_validate_intent`: run deterministic rules.
- `upf_explain_violation`: explain one diagnostic.
- `upf_generate_upf`: generate UPF from explicit strategy config.

Delay until foundations are stable:

- CPF conversion.
- Full UPF 4.0 support.
- Commercial EDA execution.
- ML prediction.
- Automatic domain inference without explicit user constraints.

## Suggested Repository Layout

```text
src/upf_mcp/
  server.py
  models/
    rtl.py
    upf.py
    power_graph.py
    diagnostics.py
  rtl/
    pyslang_analyzer.py
  upf/
    parser.py
    writer.py
    normalizer.py
  rules/
    registry.py
    isolation.py
    level_shifter.py
    retention.py
    supplies.py
  datasets/
    synthetic.py
  adapters/
    openroad.py
    logs.py
  prompts/
    review_power_intent.md
tests/
examples/
docs/
scripts/
datasets/fixtures/
```

## Near-Term Implementation Backlog

1. Create `README.md` and `docs/glossary.md`.
2. Create Python package skeleton and CI.
3. Define Pydantic models for RTL graph, UPF IR, and diagnostics.
4. Implement `upf_ping`.
5. Implement a minimal parser for `create_power_domain` and `set_scope`.
6. Implement `upf_parse_upf` with source-location diagnostics.
7. Build first synthetic two-domain RTL + UPF fixture.
8. Integrate `pyslang` enough to list hierarchy and connections.
9. Implement domain assignment and crossing detection.
10. Implement missing-isolation rule.
11. Expose `upf_validate_intent`.
12. Add the first-demo path: lint existing UPF, summarize main design blocks,
    list power crossings, and explain top diagnostics.
13. Implement UPF writer golden tests.
14. Create five stable MCP evaluation questions.

## Confirmed Decisions

- First serious UPF language priorities: UPF 2.1 and UPF 3.0.
- OpenROAD's UPF command support is a useful open-source reference and
  compatibility floor, not the full target scope.
- MVP flow strategy: build an open-source reproducible core first, with clean
  adapter boundaries for later Synopsys/Cadence/Siemens log and rule mapping.
- First user/workflow priority: an engineer using an AI agent to debug UPF and
  understand the design's power intent.
- Second workflow priority: generating UPF through an interactive
  engineer-agent process, after the analysis/debugging foundation is solid.
- Repository/product placement: `upf-mcp` should remain a standalone MCP project
  under the `ariklapid` user, similar in posture to `pyslang-mcp`. It should not
  be coupled to the broader `asicdesign.ai` portal/workflows/quizzes repos.
- License: Apache-2.0.
- Runtime direction: Python/FastMCP plus `pyslang` is approved for the initial
  implementation.
- Parser direction: create a project-owned Python Tcl/UPF parser/front end,
  kept as simple as possible and limited to supported UPF command collection.
  After reviewing `search-for-open-source-upf-parsers.md`, the implementation
  should first spike `tclint` for Tcl syntax parsing, but keep UPF semantics,
  IR, normalization, and diagnostics under this project's control.
- Data policy: private/internal UPF examples are allowed for local validation,
  but committed fixtures and datasets must be public license-compatible or
  synthetic.
- Generation policy: explicit strategy input first. MCP-inferred domains,
  voltages, states, isolation, and retention should be advisory suggestions
  until an engineer confirms them.
- First demo: lint an existing UPF and infer the main design blocks and power
  crossings from it.
- Second demo: generate UPF from RTL.

## Questions for Arik

No open planning questions at this stage.
