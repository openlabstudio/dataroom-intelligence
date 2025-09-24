# 12. Coding Standards

These standards are mandatory for all code committed to the repository.

## 12.1. Core Standards

*   **Language:** Python 3.11+
*   **Style & Linting:** The project will use **Black** for uncompromising code formatting and **Ruff** for linting. A pre-commit hook should be configured to automatically format and lint code before every commit.
*   **Test Organization:** Test files must be located in the `tests/` directory and follow the `test_*.py` naming convention.

## 12.2. Naming Conventions

*   Standard **PEP 8** will be followed: `snake_case` for functions, methods, and variables; `PascalCase` for classes.

## 12.3. Critical Rules

1.  **Type Hinting is Mandatory:** All function and method signatures, including arguments and return values, MUST use Python's standard type hints.
    *   *Rationale:* This is critical for static analysis, code completion, and ensuring data flows correctly between components. It is the single most important rule for preventing bugs in a project of this nature.
2.  **Strict Separation of Concerns:** Logic must be delegated to the appropriate layer. Handlers in the `handlers/` directory should contain no business logic; their role is to parse requests and call services in the `core/` directory.
    *   *Rationale:* This enforces our component-based architecture, making the system modular and testable.
3.  **No Hardcoded Secrets:** API keys, tokens, and other secrets MUST NOT be written in the source code. They must be loaded exclusively from environment variables via the configuration system.
    *   *Rationale:* This is a fundamental security requirement.
4.  **Use the Structured Logger:** All diagnostic output must use the configured structured logger. `print()` statements are forbidden in committed code.
    *   *Rationale:* This ensures our logs are consistent, machine-readable, and useful for debugging in production.

---
