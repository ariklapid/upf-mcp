# **Architectural Integration of Model Context Protocol with Unified Power Format IEEE 1801 for Autonomous Power Intent Engineering**

The semiconductor industry is currently navigating a pivotal transition where the complexity of power management has transcended the capabilities of traditional manual Register Transfer Level (RTL) design and verification methodologies. As fabrication processes advance toward 2nm and below, the quadratic dependency of power leakage on transistor density has elevated power optimization from a secondary objective to a primary architectural constraint.1 The Unified Power Format (UPF), formalized as the IEEE 1801 standard, has emerged as the definitive mechanism for specifying power intent, yet its implementation remains siloed within proprietary toolchains and complex manual scripts.2 The emergence of Large Language Models (LLMs) suggests a path toward automation, but a profound "LLM Gap" exists: these models lack sufficient exposure to high-quality, real-world UPF datasets, which are typically guarded as corporate intellectual property.2 To bridge this divide, the development of a Model Context Protocol (MCP) server for UPF offers a standardized, two-way connection that enables AI agents to move beyond simple text generation into deterministic, rule-driven power intent analysis and generation.5

## **Evolution and Taxonomy of Power Intent Standards**

The history of specifying power intent is a progression from ad-hoc, tool-specific annotations to a converged, multi-vendor IEEE standard. Initially, the industry was divided between the Common Power Format (CPF) and the original Accellera Unified Power Format 1.0.3 UPF 1.0, donated by Accellera to the IEEE in 2006, forced designers to define the physical power structure, including supply nets and ports, simultaneously with the logical design.3 This approach was often perceived as burdensome because it required hardware engineers to act as physical designers early in the RTL phase.9

The release of IEEE 1801-2009, or UPF 2.0, introduced the transformative concept of the "supply set".3 A supply set is a bundle of power functions—typically power, ground, and bias—that can be handled as a single logical entity.3 This allowed for the "Successive Refinement" methodology, where power intent is progressively detailed as the design moves from abstract constraints to physical implementation.3

| UPF Standard Version | Major Technological Contribution | Impact on AI Readiness |
| :---- | :---- | :---- |
| UPF 1.0 (2007) | Initial declarative commands; supply net centric. | High complexity for structural inference. |
| IEEE 1801-2009 (2.0) | Supply sets; Successive Refinement; add\_power\_state. | Foundation for modular, hierarchical analysis. |
| IEEE 1801-2013 (2.1) | Improved hierarchical scoping and macro support. | Enables IP-based power intent reuse. |
| IEEE 1801-2015 (3.0) | System-level modeling; power-aware virtual prototypes. | Integration with architectural-level AI agents. |
| IEEE 1801-2024 (4.0) | Virtual supplies; refinable macros; analog-digital gap. | Supports advanced heterogeneous integration AI. |

The most recent iteration, IEEE 1801-2024 (UPF 4.0), addresses the modern challenge of heterogeneous integration and chiplet-based designs.4 It introduces "value conversion methods" (VCM) and "HDL tunneling" to bridge the long-standing gap between digital logic and the analog/mixed-signal simulations required for precise power modeling.4 For an AI agent, the introduction of "refinable macros" in UPF 4.0 provides a more structured way to reason about IP components that appear in multiple power configurations across different designs.4

## **Model Context Protocol Architecture for EDA Integration**

The Model Context Protocol (MCP) acts as a "universal adapter layer" that provides AI agents with the tools to interact with actual hardware development infrastructure rather than operating in a purely linguistic vacuum.5 In the context of Electronic Design Automation (EDA), MCP solves the "N x M" integration problem, where every new AI agent would otherwise need a unique API for every EDA tool (e.g., Yosys, OpenROAD, VCS).6

### **MCP Core Primitives and Transport Mechanisms**

An MCP server for UPF leverages several core primitives to provide context to an AI agent.8 The "Resources" primitive allows the agent to pull specific files, such as RTL source code or timing libraries, while "Tools" enable the agent to execute actionable computations, such as running a linter or a logic synthesizer.8

The transport layer of MCP typically uses JSON-RPC 2.0 and can be implemented via two main methods.6 For local development environments where the AI is integrated into a desktop IDE, standard input/output (stdio) transport is preferred due to its low latency and zero network overhead.6 For large-scale EDA clusters, Server-Sent Events (SSE) provide an efficient way to stream data from remote servers back to the agent.6

| Transport Method | Deployment Context | Security Pattern |
| :---- | :---- | :---- |
| **Stdio** | Local developer machines; AI-powered IDEs. | Inherits host OS permissions; same-user trust. |
| **SSE (HTTP)** | Remote EDA clusters; centralized tool servers. | OAuth 2.0; Bearer tokens; API keys. |
| **Gateway Pattern** | Enterprise environments with multiple tools. | Centralized SSO; trusted internal tokens. |

The stateful nature of MCP is particularly vital for UPF generation.15 Unlike standard REST APIs, MCP maintains the contextual state across interactions, allowing an agent to incrementally refine a power intent file based on feedback from a synthesis tool or a simulator.15 This aligns with the "Successive Refinement" philosophy of IEEE 1801, enabling a human-in-the-loop workflow where the AI suggests a power domain, the engineer validates it, and the MCP server then implements the corresponding set\_isolation and set\_level\_shifter commands.2

## **Implementation of the Layered UPF MCP Server**

As specified in the architectural roadmap for the UPF MCP project, the server must be structured into three functional layers to provide robust, rule-driven intelligence.2

### **Layer 1: Structural Inference via Pyslang**

The first layer of the server focuses on the structural analysis of the RTL hierarchy.2 This is achieved using pyslang, a Python interface for the slang compiler.18 pyslang is distinguished from simple text parsers by its ability to perform lexing, parsing, type checking, and elaboration of SystemVerilog code.18 This elaboration process is critical for power intent generation because it resolves module parameters and interface connections, providing the agent with a "ground truth" graph of the design's connectivity.20

An agent using the analyze\_rtl API can traverse the elaborated AST to identify functionally distinct blocks.2 For instance, a block instantiating a Large Memory Array (LMA) or a complex Neural Processing Unit (NPU) can be identified as a candidate for a dedicated power domain that can be shut down when the processor is in an idle state.22 The structural analysis layer also extracts "power control signals," such as resets and enables, which will eventually be mapped to UPF commands like set\_isolation\_control and set\_retention\_control.24

### **Layer 2: Deterministic Rule Engine for Power Compliance**

The second layer functions as the "brain" of the MCP server, implementing a deterministic rule engine that encodes the logic of IEEE 1801\.2 This layer is the primary differentiator of the project, as it ensures that the AI's suggestions are electrically and logically valid.2 The rule engine focuses on domain crossing validation: whenever a signal moves from a switchable domain to an always-on domain, the engine mandates the insertion of an isolation cell.2

| Design Condition | Rule Engine Requirement | Generated UPF Command |
| :---- | :---- | :---- |
| Signal crosses to always-on domain. | Isolation required to prevent corruption. | set\_isolation |
| Signal crosses between different voltages. | Level shifting required for electrical safety. | set\_level\_shifter |
| Block must maintain state during sleep. | Sequential element retention strategy. | set\_retention |
| Nested hierarchy in power gating. | Support for hierarchical supply sets. | associate\_supply\_set |

The engine also performs "power-aware linting".25 It identifies illegal domain crossings where two domains are powered down by different, non-synchronized control signals.25 It can also detect "voltage orphans"—modules that have been logic-assigned to a domain but lack a valid primary supply connection in the UPF script.2 By offloading these mechanical, rule-based checks to a deterministic engine, the AI agent's limited context window is reserved for higher-level architectural reasoning.5

### **Layer 3: LLM Interface and Natural Language Translation**

The final layer is the user-facing interface that leverages LLMs to interpret intent and explain violations.2 A significant challenge in modern EDA is the obscurity of error messages; a junior designer may struggle to understand why a "supply set handle" error has occurred.27 The UPF MCP server uses the LLM to translate these technical violations into natural language.2 For example, instead of a raw parser error, the agent can explain: "The isolation cell for the encryption block is missing its control signal because the wake-up timer is in a different power domain that is currently off".2

The translation layer also facilitates the conversion between different power formats.2 Although UPF is the dominant standard, legacy designs may still utilize the Common Power Format (CPF).9 The AI agent can assist in the translation of CPF commands to their UPF equivalents, such as mapping a CPF create\_power\_domain \-shutoff\_condition to a UPF add\_power\_state \-simstate CORRUPT.9

## **Research into Available UPF and Power Intent Resources**

A primary goal of this research was to identify open-source or light-licensed resources that can be utilized to train or ground a UPF-aware AI agent while avoiding the legal risks associated with copyrighted IEEE specifications.2

### **Open-Source EDA Tooling and Reference Implementations**

The OpenROAD project provides the most robust open-source reference for UPF command implementation.33 The src/upf directory in the OpenROAD repository contains C++ and Tcl code for parsing a core subset of UPF 2.1 and 3.0 commands.35 This code is licensed under the permissive BSD-3 license, making it a safe and valuable reference for building the MCP server's structural analysis layer.33

| Resource | Repository/Provider | License | Specific Value |
| :---- | :---- | :---- | :---- |
| **OpenROAD** | [github.com/The-OpenROAD-Project](https://github.com/The-OpenROAD-Project) | BSD-3 | Permissive C++/Tcl implementation of UPF reading. |
| **Hammer** | [github.com/ucb-bar/hammer](https://github.com/ucb-bar/hammer) | BSD | YAML-based abstraction of power intent. |
| **SiliconCompiler** | [github.com/siliconcompiler](https://github.com/siliconcompiler) | Apache 2.0 | Integrated flow supporting UPF input formats. |
| **PULP Platform** | pulp-platform.org | Apache 2.0 | Complex SoC designs with real-world supply planning. |
| **upf-tools** | [github.com/pseudopotential-tools](https://github.com/pseudopotential-tools) | MIT | Python Pydantic models for UPF-like dictionaries. |

The Hammer physical design flow from UC Berkeley provides an alternative, higher-level abstraction for power intent.33 Instead of writing raw Tcl, Hammer users specify power and ground pins in a YAML configuration file, which the tool then converts into the appropriate UPF or CPF commands for various commercial back-ends.38 This YAML-based schema is an ideal candidate for fine-tuning an AI agent, as it provides a structured, JSON-like representation of power architecture that is more easily processed by LLMs than standard Tcl scripts.38

### **Niche Technical Sources and Engineering Forums**

Engineering forums and technical blogs provide insights into the practical challenges of UPF implementation that are often missing from official standard documents.25 The Synopsys "Chip Design" blog features articles on "Practical Power Management," illustrating how to move from static spreadsheets of power data to dynamic UPF 3.0 models for memories like DDR4.39 These examples highlight the need for AI agents to reason about "power state space granularity"—deciding whether to model every single transistor state or to reduce the complexity to high-level states like Active, Idle, and Off.39

The SemiWiki and Verification Academy communities also offer tutorials on the verification of power-managed designs.26 A recurring theme in these discussions is the "X-propagation" problem: the danger of an un-isolated signal from a powered-down domain being interpreted as a logical 1 or 0 by an always-on block, potentially causing silent data corruption.40 These niche sources emphasize that static verification (linting and formal) should always precede dynamic simulation to ensure that the UPF is "correct by construction".40

## **Evaluating the Existence of AI-Ready UPF Datasets**

A critical requirement of the research was to determine if an AI-ready UPF dataset currently exists. The search reveals a dichotomy: while there are massive datasets for 5G User Plane Functions, datasets for hardware Unified Power Format are essentially non-existent in the public domain.2

### **The User Plane Function (UPF) Disambiguation**

Search agents frequently encounter a "collision of acronyms" between the semiconductor UPF and the 5G telecom UPF.42 In the context of 5G, UPF refers to the User Plane Function—the network component responsible for packet routing and forwarding.42 This field has numerous open-source datasets, such as the 5GAD2022 dataset, which contains millions of telemetry packets for deep learning-based DDoS attack detection.47 While these projects demonstrate sophisticated AI/ML integration (e.g., using Convolutional Neural Networks on P4-programmable switches), they provide no training value for hardware power intent agents.42

### **Hardware UPF: The Foundational Data Crisis**

In the hardware domain, the industry is only now beginning to release "Foundation Data" for AI research.49 The **iDATA** project, associated with the **AiEDA** library, is the first large-scale attempt to provide AI-ready datasets derived from 50 real 28nm chip designs.49 This 600GB dataset includes multi-level structured data spanning from netlists to layouts, intended for tasks like wirelength prediction and congestion optimization.49 However, the inclusion of comprehensive UPF intent files within iDATA has not yet been confirmed in the public documentation, and the full dataset is still being prepared for release.49

Another potential source is the OpenROAD\_Discussions dataset on Hugging Face.36 This is a text-based dataset containing technical discussions and issue reports from the OpenROAD project.36 While it provides context for "common problems" encountered with UPF 2.1, it does not offer the "Golden RTL \+ UPF" pairs required for supervised training of a generation model.36

## **Synthetic Data Generation for Power Intent**

The "Safe Data Strategy" identified in upf-mcp.txt is to generate synthetic datasets to train the AI agent.2 This approach is necessitated by the restrictive licensing of the official IEEE standard, which explicitly forbids the use of its materials for creating or training AI systems without written consent.31

### **Mechanism for Automated Design Synthesis**

Synthetic generation must focus on producing a high volume of diverse RTL hierarchies and corresponding power strategies.2 This can be accomplished through a "Perturbation and Validation" loop:

1. **Seed Designs:** Start with a collection of small, open-source designs, such as simple processors (e.g., Ibex, Rocket) or peripheral cores (e.g., AES, SPI).51  
2. **Permute Parameters:** Programmatically vary the number of modules, the bit-widths of signals, and the complexity of control logic to create thousands of unique top-level hierarchies.54  
3. **Apply Heuristic Power Intent:** Use a standard rule-set to generate valid UPF files for these designs.2 For instance, always gating a high-activity module or always isolating a low-voltage bus.25  
4. **Inject Synthetic Bugs:** Create a corresponding set of "invalid" UPF files by intentionally removing isolation cells, using the wrong retention signals, or assigning incompatible voltages.2  
5. **Formal Verification Oracle:** Run these synthetic pairs through a commercial or open-source formal tool (e.g., Jasper or EBMC) to confirm the presence of violations.5

This process yields a clean, labeled dataset of "Design \+ Power Intent \+ Violation Report" that can be used to fine-tune an AI agent or a specialized linter model.2 This methodology mimics the data augmentation techniques used in other domains (like biological transposase generation) to overcome the lack of diverse training data.59

## **Benchmarking Existing AI Agents in Silicon Development**

To design a competitive UPF MCP, it is instructive to analyze the successes and limitations of existing agentic frameworks in the EDA space.

### **Kiro: Agentic AI for Silicon Lifecycle**

Kiro represents the state-of-the-art in "infrastructure-aware" AI agents.5 Kiro addresses the semiconductor industry's proprietary language and closed toolchain constraints by using MCP as a bridge to standard-build flows and custom scripts.5 One of Kiro’s key innovations is "Intelligent Compilation," where the agent reads an internal markdown tutorial and then calls the team’s actual build infrastructure via an MCP server.5 This ensures that the agent follows institutional knowledge about how modules should be compiled, rather than hallucinating generic settings.5

Kiro also demonstrates effective log analysis for hardware verification.5 When a regression log contains millions of lines—typical for a power-aware simulation—Kiro’s MCP server uses built-in analysis functions to extract failure patterns and stack traces.5 The agent receives only these structured "insights," allowing it to reason about the root cause of a power failure without overflowing its context window.5

### **AMIQ DVT MCP Server**

The AMIQ DVT MCP Server provides a specialized benchmark for language-correctness in hardware agents.20 While generic agents are effective with common programming languages (Python, Java), they frequently struggle with domain-specific languages like SystemVerilog and UPF.21 The DVT MCP server grounds AI reasoning in the elaborated design hierarchy, allowing assistants like Claude to correctly identify signal paths across complex projects.20 If an AI-generated UPF script makes a subtle language error, the DVT server catches it instantly and provides a quick, tight feedback loop for the agent to correct its own code.21

## **The Convergence of AI and Physical Design Flows**

The final phase of building a UPF MCP is integration with the automated flows that transform power intent into silicon.2 Modern flows utilize a combination of open-source and commercial tools, each with their own power-aware capabilities.33

### **Automated Floorplanning and Power Grids**

The OpenROAD flow incorporates an automated power distribution network (PDN) generation phase.33 During this stage, the logical power domains defined in the UPF are mapped to physical areas on the die.33 The MCP server can facilitate this by generating "halo constraints" and "well tie insertion" instructions based on the UPF domain partitioning.33

| Physical Design Stage | UPF MCP Contribution | Target Tool / Project |
| :---- | :---- | :---- |
| **Logic Synthesis** | Synthesize RTL \+ UPF to gated netlist. | Yosys / Design Compiler 64 |
| **Floorplanning** | Automatic domain-based area assignment. | OpenROAD / Innovus 33 |
| **Power Planning** | PDN creation based on supply sets. | OpenROAD / iEDA 33 |
| **Routing** | DRC-correct power net routing. | OpenROAD / CUGR 33 |
| **Signoff** | Power-aware Equivalence Checking. | Kepler-Formal / PrimeTime 55 |

The integration with tools like Yosys through an MCP server (as implemented in mcp4eda) allows the agent to validate that the power gating logic has been correctly inferred from the UPF during synthesis.62 This prevents cases where the UPF describes a power-down strategy, but the logic gates are never actually mapped to power-controllable cells in the library.22

### **Predictive Modeling for PPA Optimization**

The convergence of power intent with Machine Learning (ML) is also driving improvements in Performance, Power, and Area (PPA) prediction.66 ML-based predictive models can estimate power-performance trade-offs based on historical verification data, allowing architects to optimize their UPF strategy before entering the time-intensive synthesis phase.58 For example, supervised learning models can be trained on past designs to predict the likelihood of "IR drop" violations in a given power grid configuration, permitting the AI agent to suggest proactive modifications to the domain voltage.54

## **Nuanced Challenges in Autonomous Power Intent Engineering**

While the architecture for a UPF MCP is technically feasible, several nuanced challenges remain for the developer to resolve during the prototyping phase.2

### **Automatic Inference of Hierarchical Scopes**

One of the most complex aspects of IEEE 1801 is hierarchical scoping.12 A design may have dozens of levels of nesting, and a power domain at a lower level may inherit supply sets from its parent or define its own.24 The MCP server's structural analysis layer must be sophisticated enough to maintain an "Information Model" that tracks these hierarchical relationships, ensuring that a set\_scope command in the UPF correctly aligns with the intended instance in the elaborated RTL.35

### **Addressing Undefined UPF Specifications**

There are certain scenarios where the current IEEE 1801 standard lacks the ability to define specific connectivity requirements.25 For example, the control signal connectivity for "hard macros" like RAMs is often undefined in standard UPF.25 Chips often contain multiple RAM cells, and their internal architecture—including how they handle sleep and retention—is critical for low-power optimization.25 Standard UPF does not provide a mechanism to check internal isolation control or polarity for these internally isolated macro pins.25 An advanced AI agent must therefore supplement its UPF knowledge with library-specific data extracted from Liberty (.lib) files to ensure that macro connectivity is consistent at the SoC level.25

### **Mitigating Token Saturation and Cost**

In production-grade agentic loops, runaway costs and context window saturation are significant risks.8 When an agent iterates through hundreds of potential power domain configurations, each simulation run generates massive amounts of data.71 The MCP server must act as a "switchboard," filtering and prioritizing the most critical failure signatures to the LLM.14 Best practices include implementing per-session tool call budgets and using the "Response-as-Instruction" pattern, where the tool's output actively guides the agent on what to do next (e.g., "The isolation failed at signal A, try checking the supply set handle of Domain B").8

## **Conclusions and Strategic Recommendations**

The research indicates that the path toward a fully functional UPF Model Context Protocol server is constrained not by a lack of architectural standards, but by the scarcity of open, AI-ready datasets.2 While the IEEE 1801 standard is exhaustive in its capabilities, it is protected by copyrights that necessitate a shift toward synthetic data generation for training AI models.31

The developer should prioritize the construction of a robust, pyslang-based structural analysis layer that serves as the foundation for all power intent reasoning.2 This should be coupled with a deterministic rule engine that handles the logical validation of domain crossings, ensuring that the AI agent remains grounded in the physical and electrical realities of the design.2

For training and evaluation, the project must implement an automated pipeline to generate synthetic RTL-to-UPF pairs.2 By programmatically varying hierarchies and injecting intentional power architecture violations, the developer can create a proprietary "synthetic golden dataset" that bypasses the limitations of public data scarcity.2

Finally, the MCP server must be designed for multi-tool orchestration.73 By connecting to open-source physical design tools like OpenROAD and fast simulators like Verilator, the UPF MCP can provide the tight feedback loops necessary for "Correct by Construction" hardware design.5 This approach not only addresses the critical "LLM Gap" in current AI models but also aligns with the broader semiconductor industry's evolution toward autonomous, context-aware, and intelligent EDA workflows.73

#### **Works cited**

1. THE NEW ERA ON LOW POWER DESIGN AND VERIFICATION METHODOLOGY \- DigitalXplore, accessed May 5, 2026, [https://www.digitalxplore.org/up\_proc/pdf/226-146285901253-58.pdf](https://www.digitalxplore.org/up_proc/pdf/226-146285901253-58.pdf)  
2. upf-mcp.txt  
3. What's New in IEEE 1801 and Why? \- DVCon Proceedings, accessed May 5, 2026, [https://dvcon-proceedings.org/wp-content/uploads/1034.pdf](https://dvcon-proceedings.org/wp-content/uploads/1034.pdf)  
4. Accellera Announces IEEE Standard 1801™-2024 is Available Through IEEE GET Program, accessed May 5, 2026, [https://www.accellera.org/news/press-releases/414-accellera-announces-ieee-standard-1801-2024-is-available-through-ieee-get-program](https://www.accellera.org/news/press-releases/414-accellera-announces-ieee-standard-1801-2024-is-available-through-ieee-get-program)  
5. Bringing agentic AI to silicon development \- Kiro, accessed May 5, 2026, [https://kiro.dev/blog/bringing-agentic-ai-to-silicon-development/](https://kiro.dev/blog/bringing-agentic-ai-to-silicon-development/)  
6. What is Model Context Protocol (MCP)? A guide | Google Cloud, accessed May 5, 2026, [https://cloud.google.com/discover/what-is-model-context-protocol](https://cloud.google.com/discover/what-is-model-context-protocol)  
7. What is the Model Context Protocol (MCP)?, accessed May 5, 2026, [https://modelcontextprotocol.io/docs/getting-started/intro](https://modelcontextprotocol.io/docs/getting-started/intro)  
8. Model Context Protocol (MCP): The Complete Engineering Guide — Architecture, Internals, and Real-World Use Cases | by Rishabh Kumar | Mar, 2026 | Medium, accessed May 5, 2026, [https://medium.com/@rishabhkr954/model-context-protocol-mcp-the-complete-engineering-guide-architecture-internals-and-0d7b5d988b08](https://medium.com/@rishabhkr954/model-context-protocol-mcp-the-complete-engineering-guide-architecture-internals-and-0d7b5d988b08)  
9. Power Intent Formats: Light at the End of the Tunnel? \- EE Times, accessed May 5, 2026, [https://www.eetimes.com/power-intent-formats-light-at-the-end-of-the-tunnel/](https://www.eetimes.com/power-intent-formats-light-at-the-end-of-the-tunnel/)  
10. Overview of Unified Power Format (UPF) | PDF | Computing \- Scribd, accessed May 5, 2026, [https://www.scribd.com/document/266231751/Unified-Power-Format](https://www.scribd.com/document/266231751/Unified-Power-Format)  
11. Unified Power Format \- Wikipedia, accessed May 5, 2026, [https://en.wikipedia.org/wiki/Unified\_Power\_Format](https://en.wikipedia.org/wiki/Unified_Power_Format)  
12. Successive Refinement: A Methodology for Incremental Specification of Power Intent \- DVCon Proceedings, accessed May 5, 2026, [https://dvcon-proceedings.org/wp-content/uploads/successive-refinement-a-methodology-for-incremental-specification-of-power-intent.pdf](https://dvcon-proceedings.org/wp-content/uploads/successive-refinement-a-methodology-for-incremental-specification-of-power-intent.pdf)  
13. Workshop: Introduction of IEEE 1801-2024 (UPF 4.0) \- Accellera Systems Initiative, accessed May 5, 2026, [https://www.accellera.org/resources/videos/introduction-of-ieee-1801-2024-upf-4-0](https://www.accellera.org/resources/videos/introduction-of-ieee-1801-2024-upf-4-0)  
14. What is Model Context Protocol (MCP)? \- IBM, accessed May 5, 2026, [https://www.ibm.com/think/topics/model-context-protocol](https://www.ibm.com/think/topics/model-context-protocol)  
15. What is the Model Context Protocol (MCP)? \- Databricks, accessed May 5, 2026, [https://www.databricks.com/blog/what-is-model-context-protocol](https://www.databricks.com/blog/what-is-model-context-protocol)  
16. Model Context Protocol \- Wikipedia, accessed May 5, 2026, [https://en.wikipedia.org/wiki/Model\_Context\_Protocol](https://en.wikipedia.org/wiki/Model_Context_Protocol)  
17. Context Engineering & Model Context Protocol: Conversational AI in 2026 \- Indigo.ai, accessed May 5, 2026, [https://indigo.ai/en/blog/context-engineering/](https://indigo.ai/en/blog/context-engineering/)  
18. Testbench Linting – open-source way PySlint \- DVCon Proceedings, accessed May 5, 2026, [https://dvcon-proceedings.org/wp-content/uploads/92146.pdf](https://dvcon-proceedings.org/wp-content/uploads/92146.pdf)  
19. Highlights of DVCon EU 2023 \- AMIQ Consulting, accessed May 5, 2026, [https://www.consulting.amiq.com/2023/11/20/highlights-of-dvcon-eu-2023/](https://www.consulting.amiq.com/2023/11/20/highlights-of-dvcon-eu-2023/)  
20. DVT MCP Server for Verilog, SystemVerilog, VHDL, and e \- AMIQ EDA, accessed May 5, 2026, [https://eda.amiq.com/products/dvt-mcp-server](https://eda.amiq.com/products/dvt-mcp-server)  
21. AMIQ EDA Gives AI Agents Access to Essential Design and Verification Data \- SemiWiki, accessed May 5, 2026, [https://semiwiki.com/forum/threads/amiq-eda-gives-ai-agents-access-to-essential-design-and-verification-data.24440/](https://semiwiki.com/forum/threads/amiq-eda-gives-ai-agents-access-to-essential-design-and-verification-data.24440/)  
22. a systolic array-based power-efficient reconfigurable AI accelerator, accessed May 5, 2026, [https://www.fitee.zjujournals.com/rc-pub/front/front-article/download/133321495/lowqualitypdf/SAPER-AI%E5%8A%A0%E9%80%9F%E5%99%A8%EF%BC%9A%E4%B8%80%E7%A7%8D%E5%9F%BA%E4%BA%8E%E8%84%89%E5%8A%A8%E9%98%B5%E5%88%97%E7%9A%84%E4%BD%8E%E8%83%BD%E8%80%97%E5%8F%AF%E9%87%8D%E6%9E%84%E4%BA%BA%E5%B7%A5%E6%99%BA%E8%83%BD%E5%8A%A0%E9%80%9F%E5%99%A8.pdf](https://www.fitee.zjujournals.com/rc-pub/front/front-article/download/133321495/lowqualitypdf/SAPER-AI%E5%8A%A0%E9%80%9F%E5%99%A8%EF%BC%9A%E4%B8%80%E7%A7%8D%E5%9F%BA%E4%BA%8E%E8%84%89%E5%8A%A8%E9%98%B5%E5%88%97%E7%9A%84%E4%BD%8E%E8%83%BD%E8%80%97%E5%8F%AF%E9%87%8D%E6%9E%84%E4%BA%BA%E5%B7%A5%E6%99%BA%E8%83%BD%E5%8A%A0%E9%80%9F%E5%99%A8.pdf)  
23. Power-Intent Systolic Array Using Modified Parallel Multiplier for Machine Learning Acceleration \- PMC, accessed May 5, 2026, [https://pmc.ncbi.nlm.nih.gov/articles/PMC10181616/](https://pmc.ncbi.nlm.nih.gov/articles/PMC10181616/)  
24. Getting Started with Unified Power Format (UPF) | Part 1 \- Neurealm, accessed May 5, 2026, [https://www.neurealm.com/blogs/getting-started-with-unified-power-format-upf-part-1/](https://www.neurealm.com/blogs/getting-started-with-unified-power-format-upf-part-1/)  
25. Unified Power Format Expands Low-Power IC Design | Synopsys Blog, accessed May 5, 2026, [https://www.synopsys.com/blogs/chip-design/unified-power-format-low-power-ic-design.html](https://www.synopsys.com/blogs/chip-design/unified-power-format-low-power-ic-design.html)  
26. A Guide to UPF-based Power Intent Verification with Questa One, accessed May 5, 2026, [https://verificationacademy.com/topics/low-power/a-guide-to-upf-based-power-intent-verification-questa-one/](https://verificationacademy.com/topics/low-power/a-guide-to-upf-based-power-intent-verification-questa-one/)  
27. Verdi UPF Architect: Automated UPF Generation \- Synopsys, accessed May 5, 2026, [https://www.synopsys.com/verification/debug/verdi-upf-architect.html](https://www.synopsys.com/verification/debug/verdi-upf-architect.html)  
28. AI Agents with Model Context Protocol \- Coursera, accessed May 5, 2026, [https://www.coursera.org/learn/ai-agents-model-context-protocol](https://www.coursera.org/learn/ai-agents-model-context-protocol)  
29. Power-Aware Verification: A Growing Skill You Should Learn \- Inskill, accessed May 5, 2026, [https://inskill.in/training/vlsi/why-to-learn-power-aware-verification-in-vlsi/](https://inskill.in/training/vlsi/why-to-learn-power-aware-verification-in-vlsi/)  
30. Hierarchical methods for power intent specification \- Design And Reuse, accessed May 5, 2026, [https://www.design-reuse.com/article/60040-hierarchical-methods-for-power-intent-specification/](https://www.design-reuse.com/article/60040-hierarchical-methods-for-power-intent-specification/)  
31. IEEE Standard for Design and Verification of Low-Power Energy- Aware Electronic Systems, accessed May 5, 2026, [https://ieeexplore.ieee.org/iel8/10910080/10910081/10910082.pdf](https://ieeexplore.ieee.org/iel8/10910080/10910081/10910082.pdf)  
32. IEEE Standard for Design and Verification of Low-Power Integrated Circuits, accessed May 5, 2026, [https://ieeexplore.ieee.org/iel7/6521325/6521326/06521327.pdf](https://ieeexplore.ieee.org/iel7/6521325/6521326/06521327.pdf)  
33. GitHub \- The-OpenROAD-Project/OpenROAD: OpenROAD's unified application implementing an RTL-to-GDS Flow. Documentation at https://openroad.readthedocs.io/en/latest/ · GitHub, accessed May 5, 2026, [https://github.com/The-OpenROAD-Project/OpenROAD](https://github.com/The-OpenROAD-Project/OpenROAD)  
34. OpenROAD \- An Open-Source, Autonomous RTL-GDSII Flow for Chip Design, accessed May 5, 2026, [https://ucsc-ospo.github.io/project/osre24/openroad/openroad/](https://ucsc-ospo.github.io/project/osre24/openroad/openroad/)  
35. Read UPF Utility \- OpenROAD documentation, accessed May 5, 2026, [https://openroad.readthedocs.io/en/latest/main/src/upf/README.html](https://openroad.readthedocs.io/en/latest/main/src/upf/README.html)  
36. procodec/OpenROAD\_Discussions · Datasets at Hugging Face, accessed May 5, 2026, [https://huggingface.co/datasets/procodec/OpenROAD\_Discussions/viewer/default/train](https://huggingface.co/datasets/procodec/OpenROAD_Discussions/viewer/default/train)  
37. Towards Scalable Sub-THz Massive MIMO: Beamforming ASICs and 3D Die-to-Die Interconnects \- EECS, accessed May 5, 2026, [https://www2.eecs.berkeley.edu/Pubs/TechRpts/2024/EECS-2024-178.pdf](https://www2.eecs.berkeley.edu/Pubs/TechRpts/2024/EECS-2024-178.pdf)  
38. hammer/hammer/config/defaults.yml at master · ucb-bar/hammer \- GitHub, accessed May 5, 2026, [https://github.com/ucb-bar/hammer/blob/master/hammer/config/defaults.yml](https://github.com/ucb-bar/hammer/blob/master/hammer/config/defaults.yml)  
39. Practical Power Management: How the UPF 3.0 Standard is Transforming SoC Design, accessed May 5, 2026, [https://www.synopsys.com/blogs/chip-design/practical-power-management.html](https://www.synopsys.com/blogs/chip-design/practical-power-management.html)  
40. Recipes for Low Power Verification \- Synopsys \- SemiWiki, accessed May 5, 2026, [https://semiwiki.com/eda/synopsys/6650-recipes-for-low-power-verification/](https://semiwiki.com/eda/synopsys/6650-recipes-for-low-power-verification/)  
41. Simulation-based verification of power aware System-on-Chip designs using UPF IEEE 1801 | Request PDF \- ResearchGate, accessed May 5, 2026, [https://www.researchgate.net/publication/251916268\_Simulation-based\_verification\_of\_power\_aware\_System-on-Chip\_designs\_using\_UPF\_IEEE\_1801](https://www.researchgate.net/publication/251916268_Simulation-based_verification_of_power_aware_System-on-Chip_designs_using_UPF_IEEE_1801)  
42. Towards Real-Time Intrusion Detection in P4-Programmable 5G User Plane Functions \- IMDEA Networks Principal, accessed May 5, 2026, [https://dspace.networks.imdea.org/bitstream/handle/20.500.12761/1846/europ4\_postprint.pdf?sequence=4](https://dspace.networks.imdea.org/bitstream/handle/20.500.12761/1846/europ4_postprint.pdf?sequence=4)  
43. README.md \- 5GOpenUPF/openupf \- GitHub, accessed May 5, 2026, [https://github.com/5GOpenUPF/openupf/blob/master/README.md](https://github.com/5GOpenUPF/openupf/blob/master/README.md)  
44. 5GOpenUPF/openupf: A 3GPP R16 compliant open source 5G core UPF (User Plane Function). \- GitHub, accessed May 5, 2026, [https://github.com/5GOpenUPF/openupf](https://github.com/5GOpenUPF/openupf)  
45. docs/5g-core/5g-upf-architecture.md at main · ngkore/docs \- GitHub, accessed May 5, 2026, [https://github.com/ngkore/docs/blob/main/5g-core/5g-upf-architecture.md?plain=true](https://github.com/ngkore/docs/blob/main/5g-core/5g-upf-architecture.md?plain=true)  
46. omec-project/upf: 4G/5G Mobile Core User Plane \- GitHub, accessed May 5, 2026, [https://github.com/omec-project/upf](https://github.com/omec-project/upf)  
47. 5GDAD: A Deep Learning Approach for DDoS Attack Detection in 5G P4-based UPF \- IRIS, accessed May 5, 2026, [https://www.iris.sssup.it/retrieve/fb54113f-5e6f-4c86-bbdb-ee43b6c7ed7d/5GDAD\_A\_Deep\_Learning\_Approach\_for\_DDoS\_Attack\_Detection\_in\_5G\_P4-based\_UPF.pdf](https://www.iris.sssup.it/retrieve/fb54113f-5e6f-4c86-bbdb-ee43b6c7ed7d/5GDAD_A_Deep_Learning_Approach_for_DDoS_Attack_Detection_in_5G_P4-based_UPF.pdf)  
48. 5GDAD: A Deep Learning Approach for DDoS Attack Detection in 5G P4-based UPF \- Zenodo, accessed May 5, 2026, [https://zenodo.org/records/15472926/files/hpsr2024\_Paolucci.pdf?download=1](https://zenodo.org/records/15472926/files/hpsr2024_Paolucci.pdf?download=1)  
49. AiEDA: An Open-Source AI-Aided Design Library for Design-to-Vector \- arXiv, accessed May 5, 2026, [https://arxiv.org/html/2511.05823v1](https://arxiv.org/html/2511.05823v1)  
50. AiEDA: An Open-Source AI-Aided Design Library for Design-to-Vector \- ResearchGate, accessed May 5, 2026, [https://www.researchgate.net/publication/397481418\_AiEDA\_An\_Open-Source\_AI-Aided\_Design\_Library\_for\_Design-to-Vector](https://www.researchgate.net/publication/397481418_AiEDA_An_Open-Source_AI-Aided_Design_Library_for_Design-to-Vector)  
51. Devipriya1921/VSDBabySoC\_ICC2 \- GitHub, accessed May 5, 2026, [https://github.com/Devipriya1921/VSDBabySoC\_ICC2](https://github.com/Devipriya1921/VSDBabySoC_ICC2)  
52. ireneann713/VSDBABYSoC\_ICC2 \- GitHub, accessed May 5, 2026, [https://github.com/ireneann713/VSDBABYSoC\_ICC2](https://github.com/ireneann713/VSDBABYSoC_ICC2)  
53. OpenROAD API, accessed May 5, 2026, [https://openroad.readthedocs.io/en/latest/main/src/README.html](https://openroad.readthedocs.io/en/latest/main/src/README.html)  
54. 4\. Revision History and Change Log — SiliconCompiler v0.36.1 Manual, accessed May 5, 2026, [https://docs.siliconcompiler.com/en/v0.36.1/reference\_manual/appendix/changelog.html](https://docs.siliconcompiler.com/en/v0.36.1/reference_manual/appendix/changelog.html)  
55. siliconcompiler/Changes at main \- GitHub, accessed May 5, 2026, [https://github.com/siliconcompiler/siliconcompiler/blob/main/Changes](https://github.com/siliconcompiler/siliconcompiler/blob/main/Changes)  
56. Arch: An AI-Native Hardware Description Language for Register-Transfer Clocked Hardware Design \- arXiv, accessed May 5, 2026, [https://arxiv.org/html/2604.05983](https://arxiv.org/html/2604.05983)  
57. Arch: An AI-Native Hardware Description Language for Register-Transfer Clocked Hardware Design \- arXiv, accessed May 5, 2026, [https://arxiv.org/html/2604.05983v2](https://arxiv.org/html/2604.05983v2)  
58. Leveraging Machine Learning for Enhanced Low-Power Semiconductor \- ResearchGate, accessed May 5, 2026, [https://www.researchgate.net/publication/384480636\_Leveraging\_Machine\_Learning\_for\_Enhanced\_Low-Power\_Semiconductor](https://www.researchgate.net/publication/384480636_Leveraging_Machine_Learning_for_Enhanced_Low-Power_Semiconductor)  
59. (PDF) Discovery and protein language model-guided design of hyperactive transposases, accessed May 5, 2026, [https://www.researchgate.net/publication/396130742\_Discovery\_and\_protein\_language\_model-guided\_design\_of\_hyperactive\_transposases](https://www.researchgate.net/publication/396130742_Discovery_and_protein_language_model-guided_design_of_hyperactive_transposases)  
60. AMIQ EDA Gives AI Agents Access to Essential Design and Verification Data, accessed May 5, 2026, [https://eda.amiq.com/press-releases/amiq-eda-gives-ai-agents-access-to-essential-design-and-verification-data](https://eda.amiq.com/press-releases/amiq-eda-gives-ai-agents-access-to-essential-design-and-verification-data)  
61. Giving AI Agents Access to a Compiled Design and Verification Database \- SemiWiki, accessed May 5, 2026, [https://semiwiki.com/eda/amiq-eda/366471-giving-ai-agents-access-to-a-compiled-design-and-verification-database/](https://semiwiki.com/eda/amiq-eda/366471-giving-ai-agents-access-to-a-compiled-design-and-verification-database/)  
62. mcp4eda \- Awesome MCP Servers, accessed May 5, 2026, [https://mcpservers.org/servers/ssql2014/mcp4eda](https://mcpservers.org/servers/ssql2014/mcp4eda)  
63. 4\. Revision History and Change Log — SiliconCompiler v0.21.0 Manual, accessed May 5, 2026, [https://docs.siliconcompiler.com/en/v0.21.0/reference\_manual/appendix/changelog.html](https://docs.siliconcompiler.com/en/v0.21.0/reference_manual/appendix/changelog.html)  
64. ecc/bch\_dec/decoder128/build-rvt/dc-syn/rm\_notes/README.DC-RM.txt at master \- GitHub, accessed May 5, 2026, [https://github.com/pansygrass/ecc/blob/master/bch\_dec/decoder128/build-rvt/dc-syn/rm\_notes/README.DC-RM.txt](https://github.com/pansygrass/ecc/blob/master/bch_dec/decoder128/build-rvt/dc-syn/rm_notes/README.DC-RM.txt)  
65. Machine Learning for VLSI Runtime Prediction | PDF \- Scribd, accessed May 5, 2026, [https://www.scribd.com/document/928249152/Runtime-Prediction-for-VLSI-Physical-Design-Processes-Using-Machine-Learning](https://www.scribd.com/document/928249152/Runtime-Prediction-for-VLSI-Physical-Design-Processes-Using-Machine-Learning)  
66. Integrating Traditional Low-Power Techniques with AI/ML for Low-Power and High-Efficiency VLSI Chips \- R Discovery, accessed May 5, 2026, [https://discovery.researcher.life/article/integrating-traditional-low-power-techniques-with-ai-ml-for-low-power-and-high-efficiency-vlsi-chips/1b4df7a92b1932868228bd6531c2b55f](https://discovery.researcher.life/article/integrating-traditional-low-power-techniques-with-ai-ml-for-low-power-and-high-efficiency-vlsi-chips/1b4df7a92b1932868228bd6531c2b55f)  
67. Power Intent and Standards \- maaldaar, accessed May 5, 2026, [http://www.maaldaar.com/index.php/vlsi-cad-design-flow/vlsi-power/power-intent-and-standards](http://www.maaldaar.com/index.php/vlsi-cad-design-flow/vlsi-power/power-intent-and-standards)  
68. Example of UPF concepts | Download Scientific Diagram \- ResearchGate, accessed May 5, 2026, [https://www.researchgate.net/figure/Example-of-UPF-concepts\_fig2\_220799671](https://www.researchgate.net/figure/Example-of-UPF-concepts_fig2_220799671)  
69. Unified Power Format (UPF) \- Semiconductor Engineering, accessed May 5, 2026, [https://semiengineering.com/knowledge\_centers/standards-laws/standards/unified-power-format/](https://semiengineering.com/knowledge_centers/standards-laws/standards/unified-power-format/)  
70. Floorplanning and Power Grid \- PULP Platform, accessed May 5, 2026, [https://pulp-platform.org/docs/efclseminar2026/track1\_ex/ex04.pdf](https://pulp-platform.org/docs/efclseminar2026/track1_ex/ex04.pdf)  
71. Using Data And AI More Effectively In EDA \- Semiconductor Engineering, accessed May 5, 2026, [https://semiengineering.com/using-data-and-ai-more-effectively-in-eda/](https://semiengineering.com/using-data-and-ai-more-effectively-in-eda/)  
72. Addressing power efficiency challenges in AI hardware through verification, accessed May 5, 2026, [https://journals.scipubhouse.com/IJSIE/article/view/248](https://journals.scipubhouse.com/IJSIE/article/view/248)  
73. Siemens launches Fuse EDA AI Agent, accessed May 5, 2026, [https://news.siemens.com/en-us/siemens-fuse-eda-ai-agent/](https://news.siemens.com/en-us/siemens-fuse-eda-ai-agent/)  
74. A Look at Agentic AI in the EDA Engineering Workflow \- Embedded, accessed May 5, 2026, [https://www.embedded.com/a-look-at-agentic-ai-in-the-eda-engineering-workflow/](https://www.embedded.com/a-look-at-agentic-ai-in-the-eda-engineering-workflow/)  
75. Using Data And AI More Effectively In EDA \- Custom IC, accessed May 5, 2026, [https://blogs.sw.siemens.com/cicv/2026/03/12/using-data-and-ai-more-effectively-in-eda/](https://blogs.sw.siemens.com/cicv/2026/03/12/using-data-and-ai-more-effectively-in-eda/)  
76. EDA AI Agents: Intelligent Automation in Semiconductor & PCB Design \- EE Times, accessed May 5, 2026, [https://www.eetimes.com/eda-ai-agents-intelligent-automation-in-semiconductor-pcb-design/](https://www.eetimes.com/eda-ai-agents-intelligent-automation-in-semiconductor-pcb-design/)