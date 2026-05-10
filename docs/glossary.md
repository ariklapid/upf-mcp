# Glossary

This repository uses **UPF** to mean semiconductor **Unified Power Format
(`IEEE 1801`)** unless explicitly stated otherwise.

## Terms

- **UPF**: A Tcl-based standard for describing power intent for RTL and
  implementation flows.
- **Power domain**: A named region of logic that shares a common power
  intent, such as switchable or always-on behavior.
- **Voltage domain**: A region operating at a common nominal voltage.
- **Supply port**: A UPF object representing an external supply connection.
- **Supply net**: A named internal supply connection used by power intent.
- **Supply set**: A named collection of supply signals that characterize how a
  domain is powered.
- **Isolation**: Logic or strategy used to prevent invalid values from a
  powered-down domain from propagating into a live domain.
- **Level shifter**: A cell or strategy that safely bridges signals between
  domains at different voltages.
- **Retention**: A technique for preserving state across power-down events.
- **Always-on**: Logic or cells that remain powered when neighboring logic can
  be switched off.
- **Power switch**: A controllable element that gates power to a domain.
- **Power-state table (PST)**: A set of allowed combinations of supply or
  domain states.
- **Domain crossing**: A connection that passes between power domains and may
  require isolation, level shifting, retention, or an always-on controller.
- **Scope**: The hierarchical region in a design where a UPF command applies.
- **Hierarchy path**: The instance path used to locate a module or object in a
  design tree.
- **RTL graph**: The structural representation of modules, instances, ports,
  nets, and connections derived from RTL.
- **Power-intent rule**: A deterministic check that validates the consistency
  of the design and UPF model.

## Project usage

The glossary is intentionally small and operational. When a term becomes
central to implementation or evaluation, it should be defined here before the
code depends on it.

