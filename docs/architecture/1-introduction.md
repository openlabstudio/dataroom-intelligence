# 1. Introduction

This document outlines the overall project architecture for the **DataRoom Intelligence Bot v2.0**, including backend systems, data processing pipelines, and core service components. Its primary goal is to serve as the guiding architectural blueprint for development, ensuring consistency and adherence to the chosen patterns and technologies defined in the PRD.

## 1.1. Starter Template or Existing Project

This is a **greenfield implementation** of a new RAG architecture. However, it is not being built entirely from scratch.

*   **Existing Foundation:** The project will retain and build upon the existing Python application shell, which includes the **Flask** server for health checks and the **Slack Bolt** framework for command handling.
*   **New Core Logic:** All core data processing and analysis logic (the `doc_processor`, `ai_analyzer`, and new RAG components) will be completely rebuilt as specified in the PRD.

No other external starter templates will be used.

## 1.2. Change Log

| Date | Version | Description | Author |
| :--- | :--- | :--- | :--- |
| 2025-09-22 | 1.0 | Initial Architecture draft based on PRD v1.0. | Winston (Architect) |

---
