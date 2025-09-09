# Project Brief: Professional Market Intelligence Evolution (Revision 3)

**Date:** September 9, 2025
**Author:** Mary, Business Analyst
**Purpose**: To serve as the foundational document for the generation of the PRD regarding the enhancement of the `/market-research` command. This document supersedes all previous versions.

---

### 1. Executive Summary
This project will transform the `/market-research` command from a critically flawed feature into a professional-grade market intelligence platform. The goal is to generate reports with the quality of a top-tier consulting firm by evaluating a solution's market potential, independent of a startup's own documentation. The key innovation is a new **Single Process Architecture**, which replaces a flawed, discarded initial concept. This new architecture will perform a deep, exhaustive analysis to generate a comprehensive report, from which a coherent executive summary will be derived for Slack. This is a strategic imperative to deliver a reliable, expert-level tool for high-stakes investment decisions.

### 2. Problem Statement
The `/market-research` command in its current state is a **critical failure** and does not meet the minimum requirements for professional use. The original plan to implement a dual-processing pipeline was re-evaluated and deemed architecturally unsound, as it would lead to incoherent and inconsistent outputs.

The current reality is even more severe:
* **Critically Incomplete Functionality**: The system **fails to produce the promised comprehensive `.md` report**. The only output is a brief Slack summary of deplorable quality, described as being like a "toy" and completely unpresentable for professional use.
* **Untrustworthy Output**: The existing Slack summary is generated from a superficial analysis that is inconsistent and lacks the required depth for a VC analyst, making the tool currently unusable for its intended purpose.
* **Strategic Failure**: The initial architectural concept was flawed. The project requires a completely new, robust, and well-thought-out solution to be viable.

This project is not an incremental improvement; it is a necessary re-architecture to correct a failed feature and build a reliable, high-quality solution from a new foundation.

### 3. Proposed Solution
We will implement a new **Single Process Architecture** for the `/market-research` command, completely replacing the original flawed concept. This workflow will execute a single, deep analysis using over 50 reliable, pay-per-use data sources to generate a professional 10-20 page report. An intelligent summarization module will then distill this comprehensive report into a concise, coherent, and actionable Slack summary.

To achieve consultant-level quality, the solution will integrate core **BMAD Framework methodologies**:
* **Hybrid BMAD Architecture**: The system will combine the strengths of our existing infrastructure (like real-time data from Tavily) with the deep analytical power of BMAD's structured synthesis, creating a "living intelligence" asset.
* **Adaptive Research Types**: The analysis will be context-aware, selecting from **8 distinct research frameworks** (e.g., product validation, competitive intelligence, market opportunity) based on the startup's stage and market characteristics.
* **Expert Persona System**: The AI will assume the role of a specific expert (e.g., Technical Product Analyst, Market Research Specialist) to ensure the analysis has the correct focus and depth.
* **Structured Prompt Generation**: We will replace generic prompts with specialized, structured instructions that guide the AI to perform analysis using professional frameworks, ensuring the output is reliable and exhaustive.
* **Adaptive Reporting**: The final report's structure will adapt based on the available information, avoiding rigid templates to maximize relevance and quality.

### 4. Goals & Success Metrics
* **Main Goal**: To produce a market report of such high quality that a VC fund would pay a top-tier consulting firm for it.
* **Quality Metric**: Increase user satisfaction from a failing 5/10 to >8.5/10.
* **Depth Metric**: Evolve from 3-4 superficial insights to 8-10 actionable, data-backed insights per report.
* **Reliability Metric**: Increase the use of synthesized sources from the current 4-6 to over 30 per report.

### 5. MVP Scope (Prototype in 3 weeks)

#### **In Scope:**
* The complete implementation of the `/market-research` command with the new **Single Process Architecture** and integrated BMAD frameworks.
* Expansion of data sources to over 50.
* Implementation of a three-tier investment recommendation with a confidence score (e.g., DO NOT PROCEED 0-30%, PROCEED WITH CAUTION 31-70%, PROCEED WITH CONFIDENCE 71-100%).
* The system must be generic and function for any niche market without hardcoding.

#### **Out of Scope:**
* Implementation of the new commands: `/verify`, `/ask-reports`, `/search`, and `/memo`.
* Infrastructure changes not directly related to achieving the quality objective (though the stack is flexible).

### 6. Technical Considerations
* **Technology Stack**: Fully flexible. Any component can be replaced if it directly contributes to achieving the primary goal of report quality.
* **APIs**: Pay-per-use APIs are approved. APIs requiring B2B contracts (e.g., Pitchbook, Crunchbase) are excluded.
* **Implementation Environment**: **No code whatsoever will be implemented for `TEST_MODE=true`**. The solution must be developed and tested exclusively on the real system (`TEST_MODE=false`) without the use of any mocks.

### 7. Constraints & Assumptions
* **Time Constraint**: A functional prototype must be ready for a demo in **less than 3 weeks**.
* **Core Assumption**: A deep, coherent analysis (2-3 minutes) is infinitely more valuable to a VC analyst than a fast but low-quality, inconsistent summary.

### 8. Risks & Open Questions
* **Open Question**: The exact sections to eliminate from a traditional consulting report to maximize value for time-sensitive VCs need to be defined, ideally through direct user interviews.

---

### **Handoff for the Product Manager (PM) Agent**

This Project Brief contains the full context and strategic directives for the evolution of the `/market-research` command. Please initiate the **`*create-brownfield-prd`** task. Your objective is to translate these critical, high-level requirements into a detailed and actionable PRD that will guide the development team in building this professional-grade market intelligence system from this new architectural foundation.
