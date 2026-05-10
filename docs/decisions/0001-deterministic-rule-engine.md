# ADR 0001: Deterministic Rule Engine With LLM Interface

## Status

Accepted.

## Context

UPF describes electrical and structural power intent. Incorrect behavior can
lead to unsafe crossings, invalid shutdown behavior, and expensive downstream
EDA failures. LLMs are useful for interaction and explanation, but they should
not be the authority for whether power intent is valid.

The project needs an MCP interface for AI agents while preserving deterministic
behavior for parsing, normalization, validation, and generation.

## Decision

`upf_mcp` will separate the deterministic power-intent engine from the LLM-facing
interface.

The core engine owns:

- UPF command collection and typed IR construction.
- RTL structural facts from parser/elaboration backends.
- Power graph construction.
- Rule registration and execution.
- Diagnostics with evidence, source locations, assumptions, and suggested next
  actions.
- Stable UPF emission for supported constructs.

The LLM-facing MCP layer owns:

- Tool schemas and pagination.
- Compact JSON and optional Markdown formatting.
- Explanations grounded in diagnostics.
- Safe workflow guidance for users and agents.

Generation tools must require explicit engineer-confirmed strategy input for
domains, supplies, states, isolation, level shifting, and retention. Inferred
architecture is advisory until confirmed.

## Consequences

- The MVP should support a small command subset well instead of broad language
  coverage with uncertain semantics.
- Rules must identify whether they are project-defined, methodology-defined, or
  adapter-specific.
- Unsupported UPF constructs are diagnostics, not ignored text.
- Tool-specific quirks belong in adapters or rule packs, not the core model.
- Tests must cover parser behavior, IR serialization, and each rule's valid and
  invalid cases.

This approach keeps AI assistance useful while making the MCP server the
grounded source of engineering facts.
