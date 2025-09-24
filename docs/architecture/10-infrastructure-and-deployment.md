# 10. Infrastructure and Deployment

## 10.1. Infrastructure as Code

*   **Tool:** Railway Native Configuration (`railway.toml`)
*   **Location:** Root of the repository.
*   **Approach:** We will use Railway's built-in "Infrastructure as Code" capabilities to define our services and build/start commands.

## 10.2. Deployment Strategy

*   **Strategy:** Continuous Deployment.
*   **CI/CD Platform:** GitHub Actions.
*   **Trigger:** Every merge to the `main` branch will automatically trigger the CI/CD pipeline to run tests and deploy to production.

## 10.3. Environments

*   **`development`:** The local machines of our developers.
*   **`production`:** The live environment hosted on Railway.

## 10.4. Environment Promotion Flow

The promotion flow is simple and automated:
`Local Development` -> `Git Push to main` -> `GitHub Actions (Run Tests)` -> `Deploy to Production on Railway`

## 10.5. Rollback Strategy

*   **Primary Method:** Manual one-click rollback via the Railway platform UI.
*   **Rationale:** Railway maintains a history of all deployments, allowing for instant rollback to a previous stable version in case of a critical issue.

## 10.6. Local Development Workflow

*   **Problem:** Slack requires a public URL to send events, but a developer's local server is not public.
*   **Solution:** We will use a tunneling service (`ngrok`) and a dedicated "Development" Slack App to allow developers to test their local code live without affecting the production application.
*   **Workflow:**
    1.  A separate "Development" Slack App with its own API tokens will be used.
    2.  The developer runs the application locally, using the development tokens.
    3.  The developer starts `ngrok` to create a secure, public URL that tunnels to their local server.
    4.  The developer temporarily sets their `ngrok` URL as the "Request URL" in the Development Slack App's configuration.
    5.  This provides perfect isolation, allowing for safe and rapid testing in a private channel or test workspace.

---
