The search for open-source and light-licensed **Unified Power Format (UPF / IEEE 1801\)** parser implementations yields a small but highly specialized set of tools. Because production-grade low-power design is traditionally dominated by closed-source commercial EDA platforms (like Synopsys VC LP or Cadence Conformal), open-source parser engines are typically built as compiler front-ends, linters, or database generators.

### **1\. Hardware Power Intent (IEEE 1801 UPF) Parsers**

* **OpenROAD’s Built-in Parser (read\_upf)**: The foundational application for open-source digital chip physical implementation, OpenROAD, features a native C++ parser with Tcl bindings in its src/upf directory. It parses a core subset of UPF 2.1 and 3.0/3.1 commands (such as create\_power\_domain, create\_power\_switch, set\_isolation, and set\_level\_shifter). Because OpenROAD is focused on the physical floorplanning, placement, and routing of voltage domains , its parser is designed to extract structural connectivity into the OpenDB database rather than evaluating dynamic, power-aware simulation models.

* **tclint (Noah Moroze)**: This is an active, open-source Tcl parser and formatter written in Python. Crucially, it includes specific parsing rules and plugins tailored to electronic design automation (EDA) formats, fully supporting Synopsys Design Constraints (SDC), Xilinx Design Constraints (XDC), and Unified Power Format (UPF). It is integrated into VS Code as a language server backend (tclsp), letting developers parse, compile, and lint UPF syntax on-the-fly.  
* **codegraph-tcl (anvanster)**: Part of the open-source Rust-based codegraph ecosystem, this package provides a high-performance Tcl, SDC, and UPF parser with dedicated EDA support. It parses UPF scripts, tokenizes commands, and populates a graph database of code and constraint relationships, which is highly useful for building custom linting or automated power intent analysis tools.  
* **sifive/upf**: An open-source repository published by SiFive containing UPF infrastructure tools. It provides a standardized JSON schema representation of UPF specifications, a custom Tcl interpreter implemented in JavaScript (tcl-js), and a JSON-to-Tcl compiler. This enables developers to store power intent in structured JSON formats and automatically translate them back to standard IEEE 1801 Tcl scripts.  
* **XLS to UPF Parser and Generator**: A free utility hosted on SourceForge. It provides a complete UPF parser that developers can integrate into custom scripts to sanitize or check UPF files, accompanied by an XLS spreadsheet template to simplify early-stage power domain planning.  
* **Baya / EDAUtils (Kanai)**: A free, mature system integration platform that includes a robust Java-based parser for IEEE 1801-2013 (UPF 2.1) scripts. It reads UPF files, populates internal data structures, and provides APIs to validate the described power intent against the physical RTL design, Netlist, or Liberty library.

### ---

**2\. Non-EDA "UPF" Parser Disambiguation**

When searching for open-source "UPF parsers" in public registries (such as GitHub, PyPI, and SourceForge), you will encounter a high volume of search collisions. It is important to distinguish the hardware power standard from these other widely used "UPF" libraries:

#### **A. Unified Pseudopotential Format (UPF) — Chemistry & Physics**

In Density Functional Theory (DFT) material modeling (e.g., Quantum Espresso or ABINIT), "UPF" is the file extension used for atomic pseudopotentials.

* **upf-tools (pseudopotential-tools)**: A Python library with Pydantic models (UPFDict) that parses and converts UPF v1 and v2 files.

* **upf-schema**: An XML schema definition designed to parse and validate UPF v2.0.1 physics structures.

* **upf\_to\_json**: A PyPI tool built to parse UPF pseudopotentials and convert them to JSON formats.

#### **B. User Plane Function (UPF) — 5G Telecom**

In 5G Core network engineering (3GPP standard), the "UPF" is the user-plane packet routing engine.

* **gtp5g / upf-bpf**: eBPF, C++, and Go-based packet-processing engines designed to parse GTP-U (GPRS Tunneling Protocol) and UDP/IP network packets in the Linux kernel at high speeds.