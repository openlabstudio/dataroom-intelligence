# 13. Test Strategy and Standards

## 13.1. Testing Philosophy

*   **Approach:** Test-After. For the speed required by the MVP, tests will be written immediately after the functionality of a component is implemented and manually verified.
*   **Coverage Goals:** We will aim for **>80% line coverage** for all modules in the `core/` directory. The `handlers/` layer will be tested primarily via integration tests.
*   **Test Pyramid:** Our focus will be on a wide base of fast **Unit Tests**, a smaller set of **Integration Tests** for the core data pipeline, and a final manual **End-to-End Validation** as defined in Epic 4.

## 13.2. Test Types and Organization

### Unit Tests
*   **Framework:** `pytest`
*   **File Convention:** `tests/test_*.py`
*   **Location:** The `tests/` directory.
*   **Mocking Library:** Python's built-in `unittest.mock`.
*   **AI Agent Requirements:**
    *   The developer agent MUST generate unit tests for all public methods in the `core/` services.
    *   All external dependencies (especially API calls to LlamaParse and OpenAI) MUST be mocked.
    *   Tests should follow the "Arrange, Act, Assert" (AAA) pattern.

### Integration Tests
*   **Scope:** The primary integration test will validate the entire data ingestion pipeline triggered by the `/load` command, from parsing to storage.
*   **Location:** `tests/integration/`
*   **Test Infrastructure:**
    *   **External APIs:** All external APIs (LlamaParse, OpenAI) will be mocked using `unittest.mock` to ensure tests are fast and do not incur costs.
    *   **Vector Database:** Tests will run against a real, temporary ChromaDB instance on disk to verify the storage and retrieval mechanism.

## 13.3. Test Data Management

*   **Strategy:** A dedicated `tests/fixtures/` directory will be created to hold all test data.
*   **Fixtures:** This directory will contain small, representative sample documents (e.g., a 1-page PDF with a table, a sample `.txt` file) and "golden files" with the expected Markdown output after parsing.

---
