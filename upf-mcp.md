UPF MCP (IEEE 1801) — AI Agent Integration

# UPF MCP (IEEE 1801) — AI Agent Integration

## Overview

This project explores building a **Model Context Protocol (MCP)** for AI agents around **UPF (Unified Power Format, IEEE 1801)**.

The goal is to enable AI agents to:
- Understand power intent
- Generate UPF from RTL
- Validate correctness of power architecture
- Assist in debugging power-related issues

---

## Why This Matters

### LLM Gap

Large language models currently:
- Lack sufficient exposure to UPF examples
- Struggle with real-world power intent flows
- Cannot reliably generate correct UPF for complex designs

Most UPF knowledge is:
- Proprietary (internal company flows)
- Tool-specific (Synopsys, Cadence)
- Poorly represented in public datasets

➡️ This creates a strong opportunity for MCP-based augmentation.

---

## Why UPF Fits MCP Well

UPF is:

- Declarative (commands and constraints)
- Structural (tied to RTL hierarchy)
- Rule-driven (isolation, retention, level shifting)

This makes it ideal for:
- Static analysis
- Rule engines
- Graph-based reasoning

---

## Core Capabilities

### 1. UPF Generation
- Infer power domains from RTL hierarchy
- Generate:
  - `create_power_domain`
  - `create_supply_set`
  - `set_isolation`
  - `set_retention`

---

### 2. Validation / Linting

Detect:
- Missing isolation cells
- Missing level shifters
- Illegal domain crossings
- Incorrect retention strategies

---

### 3. Power Intent Analysis

- Map signals across power domains
- Identify unsafe crossings
- Highlight always-on vs switchable logic

---

### 4. Translation

- RTL → UPF
- UPF → explanation (natural language)
- CPF ↔ UPF (future)

---

## Architecture

### Layer 1 — Structural Analysis
- Parse RTL (e.g. via pyslang)
- Build hierarchy graph
- Extract connectivity

---

### Layer 2 — Rule Engine (Core IP)
- Define power rules:
  - Isolation requirements
  - Level shifter placement
  - Retention conditions

➡️ This is the main differentiator

---

### Layer 3 — LLM Interface
- Translate user intent → UPF
- Explain violations
- Suggest fixes

---

## Data Strategy (Critical)

### Safe Sources

Use only:

- Public UPF examples
- Open-source designs
- Accellera / IEEE public annexes (if available)
- Synthetic generated datasets

---

### Synthetic Data Generation

Generate:
- Random RTL hierarchies
- Power domain partitions
- Valid + invalid UPF cases

Use this for:
- Training
- Testing
- Evaluation

---

## Licensing & Legal Constraints

### IEEE 1801 Status

- The standard is **copyrighted**
- Most versions require **paid access**

---

### What NOT to do

❌ Do not:
- Embed IEEE spec text in the MCP
- Train on the official PDF
- Distribute structured versions of the spec
- Copy examples directly from restricted documents

---

### What IS allowed

✅ You can:
- Use general concepts (not copyrighted)
- Implement your own rules
- Use public examples
- Generate synthetic UPF

---

## Differentiation Strategy

This project should NOT be:

> “LLM that knows UPF”

Instead, it should be:

> **Rule-driven power intent engine with AI interface**

---

## Initial MVP Scope

### Phase 1

- RTL parsing
- Basic domain inference
- Minimal UPF generation
- Simple checks:
  - Missing isolation
  - Cross-domain signals

---

### Phase 2

- Level shifter inference
- Retention logic
- Multi-domain support
- Better diagnostics

---

### Phase 3

- Full linting engine
- Design rule database
- Integration with flows

---

## Example MCP APIs (Draft)

### Analyze RTL
analyze_rtl(file_paths: List[str]) -> DesignGraph

---

### Generate UPF
generate_upf(design_graph, strategy_config) -> upf_script

---

### Validate UPF
validate_upf(design_graph, upf_script) -> List[Violations]

---

### Explain Violation
explain_violation(violation) -> string

---

## Open Questions

- How to infer power domains automatically?
- How to model tool-specific constraints?
- How to validate correctness without golden UPF?
- How to integrate with synthesis / P&R flows?

---

## Strategic Value

This aligns with:

- AI-native EDA tooling
- Design automation for power intent
- Gaps in current LLM capabilities

---

## Bottom Line

✅ Strong technical opportunity  
⚠️ Requires careful handling of licensing  
🚀 High potential as a differentiated ASIC AI tool  

---

## Next Steps

- Define minimal rule set
- Build RTL → graph pipeline
- Implement first UPF generator
- Create synthetic dataset generator