# UPF MCP Scope

This document defines the first implementation scope for `upf_mcp`. It is a
support matrix for engineering work, tests, and user-facing diagnostics.

The MVP is intentionally narrow: parse and summarize existing UPF, preserve
source locations, and report unsupported commands explicitly. Generation and
deep semantic validation come after the parser and rule model are stable.

## Target Baseline

- Primary UPF targets: UPF 2.1 and UPF 3.0 semantics.
- Compatibility floor: command patterns commonly accepted by OpenROAD's UPF
  reader, where they overlap with this project's supported subset.
- Transport target: local MCP stdio first.
- Inputs: user-provided RTL and UPF files under an explicit project root.
- Outputs: compact structured JSON diagnostics plus concise Markdown when
  helpful.

This project does not embed IEEE 1801 standard text. Behavior is implemented
from project-owned models, public compatible references, and synthetic tests.

## First Supported Command Subset

The first parser path should recognize these commands and collect typed IR for
the arguments needed by the early lint workflow:

| Command | First MVP handling |
| --- | --- |
| `set_scope` | Track current UPF scope and source location. |
| `create_power_domain` | Capture domain name, scoped elements, include-scope intent, and source location. |
| `create_supply_port` | Capture supply port name, direction when present, and source location. |
| `create_supply_net` | Capture supply net name, domain binding when present, reuse intent when present, and source location. |
| `connect_supply_net` | Capture supply net to port/pin connections and source location. |
| `create_supply_set` | Capture supply set name and function bindings at a shallow structural level. |
| `associate_supply_set` | Capture supply set to domain or handle association. |
| `add_power_state` | Capture state names and raw state expressions for later semantic normalization. |
| `set_isolation` | Capture strategy name, domain, clamp value, applies-to direction, and elements when present. |
| `set_isolation_control` | Capture strategy name, isolation signal, sense, location, and source location. |
| `set_level_shifter` | Capture strategy name, domain, applies-to direction, location, rule, and elements when present. |
| `set_retention` | Capture strategy name, domain, retention supply bindings, and elements when present. |
| `set_retention_control` | Capture strategy name, save/restore controls, sense, and source location. |

For MVP parsing, unsupported options on otherwise supported commands should
produce diagnostics without discarding the command name or source location.

## Explicitly Unsupported In The MVP

These constructs are out of scope until the parser, source-location model, and
first rule checks are stable:

- Full Tcl execution, variable substitution, command substitution, sourced
  scripts, loops, procedures, conditionals, and arbitrary expression execution.
- Full UPF 4.0 support.
- CPF conversion.
- Power-aware simulation semantics.
- Liberty macro power modeling.
- Vendor-specific rule packs and commercial tool behavior.
- Automatic domain inference as an authoritative result.
- Destructive rewrites of user UPF.
- Large generated corpora checked into the repository.

Unsupported constructs must be reported as diagnostics. Silent acceptance is not
acceptable for power-intent behavior.

## Planned Next Commands

After the first linting workflow works end to end, extend support in this order:

1. Supply and state modeling commands needed by realistic two-domain fixtures.
2. Isolation, level-shifter, and retention variants needed by rule fixtures.
3. Writer support for the parser-supported subset.
4. Adapter-specific command interpretation behind narrow interfaces.

## Success Criteria For This Scope

- `upf_parse_upf` can parse supported commands deterministically.
- Every unsupported command gets a source-location-aware diagnostic.
- Parsed objects serialize to stable JSON.
- Small synthetic valid and invalid fixtures cover every supported command.
- Tool output remains compact enough for repeated agent calls.
