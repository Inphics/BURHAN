
# BURHAN

### Autonomous AI Agent Safety & Verification Framework

**Every action accountable. Every decision verifiable.**

BURHAN is an independently developed Python framework prototype for evaluating AI agent actions against defined security policies, simulating permitted actions, and recording decisions in a persistent audit log.

The project explores how AI agent systems can become more transparent, accountable, and easier to inspect.

BURHAN also includes an experimental web dashboard for viewing authenticated audit history and, in future development stages, reviewing audit integrity and agent activity.

> **Project Notice:** BURHAN is a proprietary research and development project made publicly visible for portfolio demonstration and technical review. It is not open-source software, and no general license to use, modify, or redistribute its source code is granted. See [Copyright and Usage](#copyright-and-usage).

## Why BURHAN?

The name **BURHAN** originates from the Arabic word **بُرْهَان (burhān)**, meaning *proof*, *evidence*, or *clear demonstration*.

Adopted into Turkish as **Burhan**, where it is also used as a personal name, the word preserves its association with evidence and the demonstration of truth.

This shared Arabic–Turkish linguistic heritage reflects the project's central philosophy: trust should be supported by evidence, and decisions should be open to examination.

BURHAN is built around the idea that trustworthy AI systems should produce more than decisions. They should provide understandable reasons, enforceable boundaries, and inspectable records of their behavior.

## Current Features

### Policy Evaluation and Enforcement

- **Policy Evaluation:** Checks whether an authenticated AI agent is permitted to perform a requested action.
- **JSON Policy Configuration:** Loads permissions from `backend/config/policies.json`, validates the configuration, and denies unlisted agents and actions by default.
- **Permission Management:** Supports granting and revoking permissions within the running policy engine.
- **Agent Authentication:** Uses environment-configured API keys to identify supported agent roles.
- **Enforcement Prototype:** Checks permissions before simulating permitted actions. Real external tool execution is not implemented.

### Audit Logging and Verification

- **Structured Audit Logging:** Records UTC timestamps, agent identities, actions, decisions, reasons, execution statuses, and request IDs.
- **SQLite Persistence:** Stores audit records in a local SQLite database.
- **HMAC-SHA256 Audit Signing:** Supports signing audit events when a secret key is configured.
- **Audit Integrity Verification:** Detects changes to inspected, signed audit fields and classifies records as `valid`, `invalid`, or `unsigned`.
- **Protected Audit Inspection:** Provides an authenticated `GET /audit` endpoint.
- **Verification API:** Provides an authenticated `GET /audit/verify` endpoint.
- **Security Failure Handling:** Includes safeguards for missing credentials, malformed signatures, invalid configuration, and unavailable audit storage.

### Web Dashboard

- **Dashboard Interface:** Provides an experimental web interface built using HTML, CSS, and JavaScript.
- **FastAPI Integration:** Serves the dashboard through the existing FastAPI application.
- **Responsive Design:** Includes a dark-themed layout, summary cards, audit status messages, and an audit records table.
- **Authenticated Audit History Viewer:** Allows an authorized user to retrieve recent audit records using the existing audit API.
- **Safe Text Rendering:** Displays audit record values using DOM text operations rather than interpreting them as HTML.
- **Audit Loading States:** Displays messages for successful retrieval, authentication failures, and unavailable audit history.
- **Dashboard Foundation Tests:** Checks essential HTML elements, static assets, and FastAPI dashboard delivery.

**Current dashboard limitation:** The audit history viewer is functional, but the dashboard's integrity verification button and signature summary cards are not yet connected to the verification API.

### Automated Testing

**99 backend tests passing** at the latest completed Stage 31 test run.

Tests cover policy behavior, authentication, simulated enforcement, SQLite persistence, audit integrity, API security, failure scenarios, and initial dashboard functionality.

## Project Status

**Status: Experimental backend and dashboard prototype | Public portfolio demonstration | All rights reserved**

BURHAN is under active research and development.

The current application version is **`0.3.0`**.

The project has completed its initial backend foundation, API hardening, and audit verification development phases.

**Phase 4 — Dashboard and Developer Experience is in progress.**

The dashboard foundation and authenticated audit history viewer have been implemented. Further development will focus on displaying integrity verification results, visualizing agent activity, and strengthening dashboard security.

BURHAN remains a research and development prototype.

**It is not production-ready and should not be relied upon as the sole security boundary for real-world AI agent systems.**

Public availability is intended for portfolio presentation and professional evaluation. It does not grant permission to use, modify, redistribute, or incorporate the source code into other projects.

## Architecture

BURHAN combines a FastAPI backend with a lightweight browser-based dashboard.

### Main Components

| Component | Location | Responsibility |
|---|---|---|
| FastAPI Application | `backend/app/main.py` | API endpoints, request handling, and dashboard serving |
| Agent Authentication | `backend/app/security/agent_auth.py` | Resolves agent identities from configured API keys |
| Policy Engine | `backend/app/policies/policy_engine.py` | Loads and evaluates agent permissions |
| Policy Configuration | `backend/config/policies.json` | Defines permitted actions |
| Enforcement Engine | `backend/app/execution/enforcement_engine.py` | Coordinates authorization and simulated execution |
| Action Executor | `backend/app/execution/action_executor.py` | Simulates permitted actions |
| Audit Logger | `backend/app/evaluation/audit_logger.py` | Creates and optionally signs audit events |
| Audit Database | `backend/app/evaluation/audit_database.py` | Stores and retrieves SQLite audit records |
| Audit Integrity | `backend/app/evaluation/audit_integrity.py` | Calculates and verifies audit signatures |
| Dashboard HTML | `backend/app/dashboard/index.html` | Defines the dashboard structure |
| Dashboard CSS | `backend/app/dashboard/style.css` | Controls dashboard appearance |
| Dashboard JavaScript | `backend/app/dashboard/script.js` | Handles dashboard interactions and authenticated audit retrieval |

### Backend Request Flow

```text
Authenticated AI Agent / API Client
                |
                v
         FastAPI Application
                |
                v
        Agent Authentication
                |
                v
          Policy Engine
                |
                v
       Allow / Deny Decision
                |
       +--------+---------+
       |                  |
       v                  v
   /evaluate           /enforce
       |                  |
       |                  v
       |           Simulated Execution
       |                  |
       +--------+---------+
                |
                v
           Audit Logger
                |
                v
          SQLite Database
```

For authenticated enforcement requests, BURHAN generates a request ID that associates the initial and final audit records.

### Dashboard Request Flow

```text
       Web Browser
            |
            v
    BURHAN Dashboard
    HTML / CSS / JavaScript
            |
            v
    User supplies audit
       API access key
            |
            v
    GET /audit?limit=100
            |
            v
      FastAPI Backend
            |
            v
    API Key Authentication
            |
            v
     SQLite Audit Data
            |
            v
    JSON Audit Response
            |
            v
    Dashboard Records Table
```

The dashboard uses the existing authenticated audit endpoint.

The audit API key is entered by the authorized user rather than hardcoded into the dashboard source files.

The HMAC signing key remains on the server and is not sent to browser JavaScript.

**Security distinction:** Serving the dashboard page does not itself authorize access to audit records. The backend must authenticate each protected API request.

## Technical Setup and Development Reference

> **Usage restriction:** The following instructions document the project's technical setup for transparency and professional evaluation. They do not grant permission to use, modify, or redistribute BURHAN. See [Copyright and Usage](#copyright-and-usage).

### Prerequisites

- Python 3.11 or newer
- Git
- A terminal
- A modern web browser

Development and testing have primarily been performed in GitHub Codespaces. Other environments may require adjustments.

### 1. Clone the Repository

```bash
git clone https://github.com/Inphics/BURHAN.git
cd BURHAN
```

### 2. Create a Virtual Environment

On Linux, macOS, or GitHub Codespaces:

```bash
python -m venv .venv
source .venv/bin/activate
```

On Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

From the project root:

```bash
python -m pip install -r backend/requirements.txt
```

### 4. Configure API Authentication

BURHAN uses environment variables for its API credentials.

Relevant variables include:

| Environment Variable | Purpose |
|---|---|
| `BURHAN_RESEARCH_AGENT_KEY` | API key for `research_agent` |
| `BURHAN_ADMIN_AGENT_KEY` | API key for `admin_agent` |
| `BURHAN_AUDIT_API_KEY` | API key for protected audit inspection |
| `BURHAN_ENABLE_AUDIT_API` | Enables audit API access when set to `true` |
| `BURHAN_AUDIT_HMAC_KEY` | Secret used to sign and verify audit records |
| `BURHAN_REQUIRE_AUDIT_SIGNING` | Requires signing when set to `true` |
| `BURHAN_AUDIT_DB_PATH` | Optional audit database path |

For local development, configure separate, strong secrets.

Example commands:

```bash
export BURHAN_RESEARCH_AGENT_KEY="replace-with-a-unique-agent-secret"
export BURHAN_ADMIN_AGENT_KEY="replace-with-another-unique-agent-secret"
export BURHAN_AUDIT_API_KEY="replace-with-a-unique-audit-api-secret"
export BURHAN_AUDIT_HMAC_KEY="replace-with-a-separate-hmac-secret"

export BURHAN_ENABLE_AUDIT_API=true
export BURHAN_REQUIRE_AUDIT_SIGNING=true
```

These are placeholders, not real credentials.

Never commit actual API keys or HMAC secrets to the repository.

Shell environment variables configured using `export` may need to be configured again after restarting a Codespace.

### 5. Start the FastAPI Application

From the project root:

```bash
python -m uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
```

The application runs locally at:

- API: `http://127.0.0.1:8000`
- Health check: `http://127.0.0.1:8000/health`
- API documentation: `http://127.0.0.1:8000/docs`
- Dashboard: `http://127.0.0.1:8000/dashboard/`

For GitHub Codespaces, open port `8000` through the **Ports** tab and keep its visibility **Private**.

### 6. Open the Dashboard

With FastAPI running, navigate to:

```text
http://127.0.0.1:8000/dashboard/
```

The initial dashboard includes:

- BURHAN branding and project description.
- Security Overview section.
- Audit Summary cards.
- Audit Integrity section.
- Recent Audit Records table.
- Audit API Key input and Load Audit Records button.

The dashboard is part of the existing FastAPI application. No separate frontend development server is required.

### 7. Load Audit History

Before loading audit history, ensure:

1. `BURHAN_ENABLE_AUDIT_API=true` is configured.
2. `BURHAN_AUDIT_API_KEY` is configured on the FastAPI server.
3. The dashboard is running through the same FastAPI application.
4. The Codespaces forwarded port is private.

Open `/dashboard/`, enter the configured audit API key in the **Audit API Key** field, and click **Load Audit Records**.

The dashboard sends an authenticated request to:

```text
GET /audit?limit=100
```

The request includes the audit API key in the `X-API-Key` HTTP header.

If authentication succeeds, the dashboard displays the returned records.

If the key is incorrect, the interface displays an authentication failure message.

If audit inspection is disabled or unavailable, the dashboard displays an unavailable status.

**Security note:** The current development dashboard accepts an API key in the browser and sends it with an authenticated request. The key is not deliberately saved to browser storage, but it is temporarily handled in JavaScript memory. This is not a production login system.

Use it only through a trusted, protected connection.

### 8. Run Automated Tests

From the project root:

```bash
python -m pytest backend/tests/ -v
```

Latest completed test result:

**99 tests passed.**

The count may increase as Phase 4 development continues.

## Policy Configuration

BURHAN loads default agent permissions from:

`backend/config/policies.json`

Example:

```json
{
  "permissions": {
    "research_agent": [
      "read",
      "report"
    ],
    "admin_agent": [
      "read",
      "report",
      "update",
      "delete"
    ]
  }
}
```

The policy engine validates the configuration during initialization.

It checks that the configuration contains the expected structure, supported top-level fields, valid agent names, and lists of non-empty action names.

Unknown agents and unauthorized actions are denied by default.

A missing or malformed policy configuration causes initialization to fail rather than silently replacing the policy with permissive defaults.

Permission changes performed using the engine's `grant_permission()` and `revoke_permission()` methods affect the running instance and are not automatically written back to the JSON file.

**Security limitation:** Anyone who can modify the policy configuration file can potentially alter authorization decisions. Protect deployment and repository write access accordingly.

## API Reference

| Method | Endpoint | Description | Authentication |
|---|---|---|---|
| `GET` | `/` | Returns project and API information | Not required |
| `GET` | `/health` | Checks basic application health | Not required |
| `POST` | `/evaluate` | Evaluates agent permissions | Agent API key |
| `POST` | `/enforce` | Evaluates and simulates permitted actions | Agent API key |
| `GET` | `/audit` | Returns stored audit records | Audit API key |
| `GET` | `/audit/verify` | Verifies stored audit signatures | Audit API key and server-side HMAC key |
| `GET` | `/dashboard/` | Serves the dashboard interface | Static page; audit data remains protected |

### POST /evaluate

Evaluates whether an authenticated agent is permitted to perform a requested action.

Example:

```bash
curl -X POST http://127.0.0.1:8000/evaluate \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $BURHAN_RESEARCH_AGENT_KEY" \
  -d '{"action":"delete"}'
```

Example response:

```json
{
  "allowed": false,
  "reason": "Agent 'research_agent' is not permitted to perform 'delete'."
}
```

The API determines the agent identity from the API key, not from the JSON request body.

### POST /enforce

Authenticates the agent, evaluates permissions, and simulates the action when permitted.

Example:

```bash
curl -X POST http://127.0.0.1:8000/enforce \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $BURHAN_RESEARCH_AGENT_KEY" \
  -d '{"action":"read"}'
```

BURHAN records an initial audit event before attempting enforcement and a final event containing the outcome.

The two records share a generated request ID.

**Important:** An `executed` value of `true` indicates successful simulation only. BURHAN does not execute real external agent tools.

### GET /audit

Retrieves stored audit events in reverse insertion order.

Disabled unless:

```bash
export BURHAN_ENABLE_AUDIT_API=true
```

A matching audit API key is also required.

Example:

```bash
curl http://127.0.0.1:8000/audit?limit=10 \
  -H "X-API-Key: $BURHAN_AUDIT_API_KEY"
```

Illustrative response:

```json
{
  "total_events": 1,
  "events": [
    {
      "id": 1,
      "timestamp": "2026-11-20T12:00:00+00:00",
      "agent": "research_agent",
      "action": "read",
      "allowed": true,
      "reason": "Agent 'research_agent' is permitted to perform 'read'.",
      "execution_status": "not_attempted",
      "request_id": null,
      "event_hmac": null
    }
  ]
}
```

The response format includes the stored signature field, if available.

The endpoint does **not** automatically verify the integrity of returned records.

The optional `limit` parameter accepts values from `1` to `100`, with a default of `100`.

### GET /audit/verify

Authenticates the caller and verifies the HMAC signatures of the returned audit records.

Example:

```bash
curl http://127.0.0.1:8000/audit/verify?limit=10 \
  -H "X-API-Key: $BURHAN_AUDIT_API_KEY"
```

Illustrative response:

```json
{
  "total": 3,
  "valid": 1,
  "invalid": 1,
  "unsigned": 1,
  "results": [
    {
      "id": 3,
      "request_id": "request-3",
      "status": "valid"
    },
    {
      "id": 2,
      "request_id": "request-2",
      "status": "invalid"
    },
    {
      "id": 1,
      "request_id": null,
      "status": "unsigned"
    }
  ]
}
```

Verification statuses:

| Status | Meaning |
|---|---|
| `valid` | The stored HMAC matches the signed audit fields |
| `invalid` | The signature is malformed or does not match |
| `unsigned` | No HMAC signature exists |

The endpoint requires the server-side `BURHAN_AUDIT_HMAC_KEY`.

It verifies only the returned records, up to the requested limit. It does not prove the complete audit history is intact.

### GET /dashboard/

Serves the experimental BURHAN web dashboard.

The static dashboard files are available through:

```text
/dashboard/
/dashboard/style.css
/dashboard/script.js
```

The dashboard interface is accessible separately from privileged audit data.

Access to `/audit` and `/audit/verify` remains controlled by the FastAPI backend.

The current dashboard supports authenticated audit history retrieval and safe display of returned records.

Dashboard-based HMAC verification and visual summaries are planned for later Phase 4 stages.

## Dashboard Architecture and Current Capabilities

### Frontend Structure

The dashboard uses three files:

```text
backend/app/dashboard/
├── index.html
├── style.css
└── script.js
```

**`index.html` — Structure**

Defines the dashboard sections, navigation-free page layout, summary cards, audit history table, verification controls, and API key form.

**`style.css` — Appearance**

Provides dark-themed styling, responsive layouts, tables, buttons, spacing, and typography.

**`script.js` — Behaviour**

Initializes the dashboard, manages loading states, handles form submission, makes authenticated audit requests, and renders returned records.

### Current Audit History Viewer

The audit history viewer displays:

| Column | Description |
|---|---|
| Request ID | Identifies related enforcement records, when present |
| Agent | Agent identity associated with the event |
| Action | Requested action |
| Decision | Allowed or denied |
| Execution | Recorded execution status |

Older records may not contain a request ID.

The dashboard uses JavaScript `textContent` to display audit fields as text rather than executable HTML.

This reduces the risk of treating client-controlled audit values as markup.

### Current Dashboard Limitations

- The Audit Summary cards currently display placeholders rather than live metrics.
- The **Verify Audit Integrity** button is disabled.
- The dashboard does not yet invoke `/audit/verify`.
- Displayed audit records are not automatically verified when loaded.
- There is no complete production authentication session or login system.
- The current audit history request is limited to the latest 100 records.
- Dashboard authentication relies on the existing audit API key mechanism.
- The interface should be used for trusted development and demonstration, not production operations.

These capabilities will be expanded in subsequent Phase 4 stages.

## Enforcement Audit Safeguards

BURHAN's enforcement workflow is designed to improve the accountability of simulated agent actions.

For authenticated `/enforce` requests:

1. BURHAN generates a request ID.
2. It attempts to save an initial audit record before invoking the enforcement engine.
3. If the initial audit write fails, the endpoint returns HTTP `503` and does not call the executor.
4. The policy engine evaluates whether the action is permitted.
5. Permitted actions may be simulated.
6. BURHAN attempts to save a final audit event describing the outcome.

### Audit Execution Statuses

| Status | Description |
|---|---|
| `not_attempted` | Execution has not been attempted |
| `blocked` | The requested action was denied |
| `simulated` | A permitted action was successfully simulated |
| `failed` | Simulation of a permitted action failed |

### Important Limitations

The pre-execution audit record currently uses `allowed: false` as a placeholder while the decision is pending.

This does not necessarily represent a final policy denial.

If the final audit write fails, the API returns HTTP `503`, but the simulated action may already have completed.

Audit persistence and simulated execution are not transactional.

## Audit Integrity and Security Model

### HMAC-SHA256 Signing

BURHAN can sign audit records using HMAC-SHA256.

When `BURHAN_AUDIT_HMAC_KEY` is configured, new audit events receive a signature covering:

- `timestamp`
- `agent`
- `action`
- `allowed`
- `reason`
- `execution_status`
- `request_id`

The verification system recalculates the signature and compares it with the stored HMAC.

This can detect changes to inspected signed fields when the secret key remains protected.

### Strict Signing Mode

Strict signing can be enabled with:

```bash
export BURHAN_REQUIRE_AUDIT_SIGNING=true
```

When strict signing is enabled, the audit logger refuses to save new events if the HMAC key is missing.

Without strict signing, the prototype may still create unsigned audit records for development compatibility.

Strict signing is **not enabled by default**.

### Known Security Limitations

**1. Simulated Enforcement Only**

BURHAN does not intercept or control arbitrary external AI agent tool calls.

**2. Prototype Authentication**

API keys identify supported agent roles, but BURHAN does not provide a complete production identity and session-management system.

**3. No Tamper-Proof Audit Storage**

HMAC verification can detect modifications to inspected signed record fields, but it cannot detect deletion, reordering, replay, database rollback, or wholesale database replacement.

**4. Unsigned Historical Records**

Records without HMAC signatures cannot be cryptographically verified.

**5. Limited Verification Scope**

The verification endpoint checks only records returned by the database query.

A result of zero invalid signatures does not prove that no records were deleted.

**6. Optional Strict Signing**

The prototype can still store unsigned records unless strict signing is enabled.

**7. Policy Configuration Trust**

The JSON configuration is validated but is not independently protected against unauthorized modification by someone with deployment or repository write access.

**8. Dashboard Authentication**

The dashboard currently uses an API key supplied through a browser form.

It does not provide production-grade login sessions, credential lifecycle controls, or comprehensive browser security hardening.

**9. Limited Operational Hardening**

BURHAN does not yet provide comprehensive rate limiting, monitoring, external append-only audit storage, recovery controls, or production-grade secret management.

**10. Incomplete Audit Outcomes**

A failed final audit write may leave the recorded outcome incomplete after simulated execution.

**BURHAN remains experimental software and should not be used as the sole security boundary for production AI agents or sensitive systems.**

## Development Roadmap

BURHAN is developed incrementally, emphasizing clear architecture, testing, and responsible security engineering.

### Phase 1 — Backend Foundation (Completed)

- [x] Establish the Python project structure.
- [x] Implement a permission-based policy engine.
- [x] Support in-memory permission granting and revocation.
- [x] Create a FastAPI backend.
- [x] Implement action evaluation through the REST API.
- [x] Record policy decisions with UTC timestamps.
- [x] Persist audit events using SQLite.
- [x] Provide optional audit inspection.
- [x] Add automated tests.

### Phase 2 — Documentation and Backend Hardening (Completed)

- [x] Document the framework's purpose and architecture.
- [x] Add technical setup and API reference documentation.
- [x] Document the security model and limitations.
- [x] Expand authentication, authorization, and failure-path tests.
- [x] Configure SQLite audit database paths and API query limits.
- [x] Add API-key authentication for agent and audit access.
- [x] Introduce simulated enforcement and audit safeguards.
- [x] Publish the `v0.2.0` backend prototype release.

### Phase 3 — Agent Safety and Verification Hardening (Completed)

- [x] **Stage 24:** Add request IDs for enforcement audit records.
- [x] **Stage 25:** Implement HMAC audit signing and verification.
- [x] **Stage 26:** Introduce JSON policy configuration and validation.
- [x] **Stage 27:** Implement an authenticated audit verification API.
- [x] **Stage 28:** Expand security testing and failure handling.
- [x] **Stage 29:** Update documentation and prepare the v0.3.0 release.

**Phase 3 test milestone: 93 passing backend tests.**

### Phase 4 — Dashboard and Developer Experience (In Progress)

- [x] **Stage 30 — Dashboard Foundation**
  - [x] Create the dashboard folder structure.
  - [x] Build the HTML dashboard layout.
  - [x] Implement responsive dark-theme styling.
  - [x] Add JavaScript initialization.
  - [x] Preview the dashboard in GitHub Codespaces.
  - [x] Add dashboard structure and asset tests.

- [x] **Stage 31 — Audit History Viewer**
  - [x] Serve the dashboard through FastAPI.
  - [x] Add audit history loading states.
  - [x] Add an audit API key input form.
  - [x] Connect the dashboard to the authenticated `/audit` endpoint.
  - [x] Display real SQLite audit records.
  - [x] Handle authentication and retrieval errors.
  - [x] Add dashboard integration checks.
  - [x] Commit and push the completed feature.

- [ ] **Stage 32 — Audit Integrity Verification Interface**
  - [ ] Connect the dashboard to `/audit/verify`.
  - [ ] Display valid, invalid, and unsigned signature counts.
  - [ ] Present verification outcomes clearly.
  - [ ] Add verification interface tests.

- [ ] **Stage 33 — Agent Activity Visualizations**
  - [ ] Explore useful audit activity summaries.
  - [ ] Visualize permitted and denied actions.
  - [ ] Add dashboard activity indicators.
  - [ ] Expand dashboard functionality and tests.

- [ ] **Stage 34 — Dashboard Security and Testing**
  - [ ] Review dashboard authentication and credential handling.
  - [ ] Expand frontend and API integration tests.
  - [ ] Improve failure handling and security messaging.
  - [ ] Review dashboard accessibility and operational limitations.

- [ ] **Stage 35 — Documentation and v0.4.0 Release**
  - [ ] Update project documentation.
  - [ ] Review Phase 4 features and limitations.
  - [ ] Run the complete test suite.
  - [ ] Prepare and publish the next release.

**Latest Phase 4 test milestone: 99 passing backend tests.**

### Longer-Term Research Directions

- [ ] Explore integration with real AI agent tool calls.
- [ ] Investigate stronger identity and key management.
- [ ] Explore hash chaining and externally anchored audit records.
- [ ] Investigate detection of missing or deleted audit events.
- [ ] Expand policy administration capabilities.
- [ ] Improve operational monitoring and developer tooling.

Features listed as planned are not yet implemented.

## Intended Purpose

BURHAN is currently intended for:

- Portfolio demonstration and professional evaluation.
- Research into AI agent security architecture.
- Exploring permission-based authorization.
- Demonstrating persistent decision auditing.
- Developing experimental audit integrity mechanisms.
- Studying secure dashboard integration with authenticated backend APIs.
- Incremental testing of agent accountability mechanisms.

These descriptions explain the project's purpose and do not grant third parties permission to use the software.

## Responsible Development

Future development will prioritize safer authentication workflows, clearer audit verification, stronger operational controls, and continued testing.

Security concerns may be reported to the repository owner through an appropriate private communication channel.

## Copyright and Usage

**Copyright © 2026. All rights reserved.**

BURHAN is a proprietary software research and development project made publicly visible for portfolio demonstration and technical review.

**No software license is currently granted.**

Except for activities permitted by applicable law or GitHub's Terms of Service, no permission is granted to:

- Use or incorporate the source code into other software or commercial products.
- Modify, adapt, or create derivative works from the source code.
- Redistribute, republish, sublicense, or commercially exploit the source code.

Any use beyond these permissions requires prior written authorization from the copyright holder.

Public availability on GitHub does not mean that BURHAN is open-source software.

The project may be licensed under different terms in the future. Until such terms are explicitly published, all rights remain reserved.

### Disclaimer

BURHAN is experimental software provided for demonstration purposes.

No warranty is made regarding its reliability, security, or suitability for any particular purpose.