
# BURHAN

### Autonomous AI Agent Safety & Verification Framework

**Every action accountable. Every decision verifiable.**

BURHAN is an independently developed Python framework prototype for evaluating AI agent actions against defined security policies, simulating permitted actions, and recording decisions in a persistent audit log.

The project explores how AI agent systems can become more transparent, accountable, and easier to inspect.

BURHAN also includes an experimental web dashboard for viewing authenticated audit history, checking audit integrity, and visualizing agent activity.

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
- **Responsive Design:** Includes a dark-themed layout, audit summary cards, status messages, activity charts, and an audit records table.
- **Authenticated Audit History Viewer:** Allows an authorized user to retrieve recent audit records through the existing audit API.
- **Audit Integrity Verification Interface:** Connects the dashboard to the protected `/audit/verify` endpoint.
- **Live Verification Summary Cards:** Displays total records checked, valid signatures, invalid signatures, and unsigned records.
- **Allowed vs. Denied Actions Chart:** Visualizes the distribution of allowed and denied audit events.
- **Activity by Agent Chart:** Displays event counts grouped by agent identity.
- **Safe Text Rendering:** Displays audit values using DOM text operations rather than interpreting them as HTML.
- **Loading and Error States:** Reports authentication failures, unavailable API responses, and empty activity data.
- **Credential Handling Improvements:** Clears the API key input, invalidates previous credentials when a new audit request begins, and retains a key for verification only after successful audit retrieval.
- **Stale Result Prevention:** Clears previously displayed audit records, activity charts, and verification summaries when a new audit history request begins.
- **Accessibility Improvements:** Includes descriptive headings, labelled form controls, accessible audit table headers, a screen-reader-friendly table caption, and status messages.
- **HTTP Security Headers:** Uses FastAPI middleware to set basic response security headers and discourage caching of protected audit API responses.
- **Dashboard Regression Tests:** Checks HTML structure, static assets, authenticated API integration, visualizations, security headers, and selected frontend security properties.

**Current dashboard limitation:** The interface is functional as a development prototype, but it is not a production-grade security console. Dashboard visualizations summarize returned audit events and do not establish the integrity of the entire audit database.

### Automated Testing

**104 backend tests passing** at the latest completed Stage 34 test run.

Tests cover policy behavior, authentication, simulated enforcement, SQLite persistence, audit integrity, API security, failure scenarios, and dashboard functionality.

Dashboard source-level regression tests are supplemented by manual browser testing. Comprehensive browser automation and a full security assessment have not been completed.

## Project Status

**Status: Experimental backend and dashboard prototype | Public portfolio demonstration | All rights reserved**

BURHAN is under active research and development.

The application version has been updated to **`0.4.0`** in preparation for its next GitHub release.

**Release status: v0.4.0 preparation in progress.**

The existing v0.3.0 release remains part of the project's release history.

### Development Progress

The following phases are complete:

- **Phase 1:** Backend Foundation
- **Phase 2:** Documentation and Backend Hardening
- **Phase 3:** Agent Safety and Verification Hardening

**Phase 4 — Dashboard and Developer Experience** has completed five development stages:

- **Stage 30:** Dashboard Foundation
- **Stage 31:** Authenticated Audit History Viewer
- **Stage 32:** Audit Integrity Verification Interface
- **Stage 33:** Agent Activity Visualizations
- **Stage 34:** Dashboard Security and Testing

**Stage 35 — Documentation and v0.4.0 Release** is currently in progress.

### Current Capabilities

BURHAN provides:

- Policy-based evaluation of authenticated AI agent actions.
- Simulated enforcement of permitted actions.
- Persistent SQLite audit logging.
- Optional HMAC-SHA256 signing and integrity verification.
- Authenticated audit history and verification APIs.
- A browser-based dashboard displaying audit records and verification summaries.
- Allowed vs. Denied Actions visualizations.
- Activity by Agent visualizations.
- Basic HTTP security headers for dashboard and API responses.
- Improved dashboard credential handling and error reporting.
- Accessible audit table headings and descriptions.
- Automated backend and dashboard regression tests.

**Latest completed test milestone: 104 passing tests.**

### Security and Production Readiness

BURHAN remains an experimental research and development prototype.

The framework does not yet execute or intercept real external AI agent tool calls.

Its dashboard uses API-key authentication and is intended for trusted development and demonstration environments.

HMAC verification can detect changes to inspected signed audit fields, but it cannot prove that records have not been deleted, reordered, or replaced.

Activity visualizations summarize returned audit events rather than necessarily representing unique agent requests or complete historical activity.

The current dashboard includes basic security improvements, but it does not provide production-grade authentication sessions, comprehensive browser security controls, or a complete security monitoring platform.

**BURHAN is not production-ready and must not be relied upon as the sole security boundary for real-world AI agent systems.**

Public availability is intended for portfolio presentation and professional evaluation. It does not grant permission to use, modify, redistribute, or incorporate BURHAN's source code into other projects.

See [Copyright and Usage](#copyright-and-usage) for the project's proprietary licensing terms.

## Architecture

BURHAN combines a FastAPI backend with a lightweight browser-based dashboard.

### Main Components

| Component | Location | Responsibility |
|---|---|---|
| FastAPI Application | `backend/app/main.py` | API endpoints, security middleware, request handling, and dashboard serving |
| Agent Authentication | `backend/app/security/agent_auth.py` | Resolves agent identities from configured API keys |
| Policy Engine | `backend/app/policies/policy_engine.py` | Loads and evaluates agent permissions |
| Policy Configuration | `backend/config/policies.json` | Defines permitted actions |
| Enforcement Engine | `backend/app/execution/enforcement_engine.py` | Coordinates authorization and simulated execution |
| Action Executor | `backend/app/execution/action_executor.py` | Simulates permitted actions |
| Audit Logger | `backend/app/evaluation/audit_logger.py` | Creates and optionally signs audit events |
| Audit Database | `backend/app/evaluation/audit_database.py` | Stores and retrieves SQLite audit records |
| Audit Integrity | `backend/app/evaluation/audit_integrity.py` | Calculates and verifies audit signatures |
| Dashboard HTML | `backend/app/dashboard/index.html` | Defines dashboard structure and visualization containers |
| Dashboard CSS | `backend/app/dashboard/style.css` | Controls dashboard appearance, accessibility styling, and charts |
| Dashboard JavaScript | `backend/app/dashboard/script.js` | Handles authenticated audit retrieval, verification, activity charts, and frontend state |

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
             HTML / CSS / JS
                     |
                     v
            User enters Audit
                API Key
                     |
           +---------+----------+
           |                    |
           v                    v
    GET /audit?limit=100  GET /audit/verify?limit=100
           |                    |
           v                    v
     Authenticated API     Authenticated API
           |                    |
           v                    v
     Stored Audit Data     HMAC Verification
           |                    |
           v                    v
     Audit Records Table   Verification Summary
           |
           v
     Activity Calculations
           |
     +-----+------+
     |            |
     v            v
Allowed/Denied   Activity by Agent
     Chart           Chart
```

The dashboard uses the existing authenticated audit endpoints.

The Audit API Key is supplied by the authorized user rather than hardcoded into dashboard source files.

The HMAC signing key remains on the server and is not sent to browser JavaScript.

**Security distinction:** Serving the dashboard page does not itself authorize access to audit records. The backend authenticates protected API requests.

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

BURHAN uses environment variables for its API credentials and signing configuration.

| Environment Variable | Purpose |
|---|---|
| `BURHAN_RESEARCH_AGENT_KEY` | API key for `research_agent` |
| `BURHAN_ADMIN_AGENT_KEY` | API key for `admin_agent` |
| `BURHAN_AUDIT_API_KEY` | API key for protected audit inspection |
| `BURHAN_ENABLE_AUDIT_API` | Enables audit API access when set to `true` |
| `BURHAN_AUDIT_HMAC_KEY` | Secret used to sign and verify audit records |
| `BURHAN_REQUIRE_AUDIT_SIGNING` | Requires signing when set to `true` |
| `BURHAN_AUDIT_DB_PATH` | Optional audit database path |

For development, configure separate, strong secrets.

Example placeholder configuration:

```bash
export BURHAN_RESEARCH_AGENT_KEY="replace-with-a-unique-agent-secret"
export BURHAN_ADMIN_AGENT_KEY="replace-with-another-unique-agent-secret"
export BURHAN_AUDIT_API_KEY="replace-with-a-unique-audit-api-secret"
export BURHAN_AUDIT_HMAC_KEY="replace-with-a-separate-hmac-secret"

export BURHAN_ENABLE_AUDIT_API=true
export BURHAN_REQUIRE_AUDIT_SIGNING=true
```

These are placeholders, not real credentials.

Never commit actual API keys or HMAC signing secrets to the repository.

### GitHub Codespaces Secrets

For persistent development credentials, use GitHub Codespaces secrets rather than storing keys in source files.

The development environment uses these four secret names:

```text
BURHAN_AUDIT_HMAC_KEY
BURHAN_AUDIT_API_KEY
BURHAN_RESEARCH_AGENT_KEY
BURHAN_ADMIN_AGENT_KEY
```

Configure the secrets through GitHub Codespaces settings and restrict repository access as appropriate.

Codespaces secrets can be made available as environment variables when the Codespace starts. Newly added or updated secrets may require restarting the Codespace.

For an existing Codespace, check that the variables are available without displaying their values:

```bash
for key in \
    BURHAN_AUDIT_HMAC_KEY \
    BURHAN_AUDIT_API_KEY \
    BURHAN_RESEARCH_AGENT_KEY \
    BURHAN_ADMIN_AGENT_KEY
do
    if [ -n "${!key}" ]; then
        echo "$key: configured"
    else
        echo "$key: MISSING"
    fi
done
```

The switches `BURHAN_ENABLE_AUDIT_API` and `BURHAN_REQUIRE_AUDIT_SIGNING` are configuration values rather than secrets.

**Important:** Preserve the original HMAC key. Replacing it can make previously signed audit records fail verification.

### 5. Start the FastAPI Application

From the project root:

```bash
export BURHAN_ENABLE_AUDIT_API=true
export BURHAN_REQUIRE_AUDIT_SIGNING=true

python -m uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
```

The configuration above assumes the relevant API keys and HMAC key are already available as environment variables.

Local addresses:

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

The dashboard includes:

- BURHAN branding and security overview.
- Audit Summary cards.
- Audit Integrity verification controls.
- Agent Activity charts.
- Recent Audit Records table.
- Audit API Key input and Load Audit Records button.

The dashboard is part of the FastAPI application. No separate frontend development server is required.

### 7. Load Audit History

Before loading audit history, ensure:

1. `BURHAN_ENABLE_AUDIT_API=true` is configured.
2. `BURHAN_AUDIT_API_KEY` is available to the FastAPI process.
3. The dashboard is running through the same FastAPI application.
4. The Codespaces forwarded port is private.

Open `/dashboard/`, enter the configured Audit API Key in the **Audit API Key** field, and click **Load Audit Records**.

The dashboard requests:

```text
GET /audit?limit=100
```

It includes the Audit API Key in the `X-API-Key` header.

If authentication succeeds and a valid response is received, the dashboard displays the returned records and updates the two Agent Activity charts.

If the key is incorrect, it displays an authentication failure message.

If audit inspection is disabled or unavailable, it displays an unavailable status.

### 8. Verify Audit Integrity

First, load audit records using the Audit API Key.

Then click **Verify Audit Integrity**.

The dashboard requests:

```text
GET /audit/verify?limit=100
```

The backend uses its server-side HMAC key to verify returned signed records.

The dashboard displays:

- Total records checked.
- Valid signatures.
- Invalid signatures.
- Unsigned records.

It also displays a verification result message.

Example:

```text
Verification complete: 1 valid, 0 invalid, 4 unsigned records.
```

This is an illustrative development result, not a permanent expected value.

The total represents the records returned by the verification endpoint, up to the requested limit.

**A successful verification request does not establish that the entire audit database is intact.**

### 9. View Agent Activity

After authenticated audit history loads, the **Agent Activity** section displays two charts.

**Allowed vs. Denied Actions**

Shows counts and percentages of audit events whose `allowed` field is `true` or `false`.

**Activity by Agent**

Groups audit events by agent identity and displays horizontal bars scaled relative to the most active agent.

Charts use the records already retrieved from `/audit`. They do not require separate chart-specific API endpoints.

The charts display counts using text and CSS-based horizontal bars.

**Important:** These are counts of audit events, not necessarily unique requests. A single enforcement request may generate multiple audit events.

### 10. Run Automated Tests

From the project root:

```bash
python -m pytest backend/tests/ -q
```

Latest completed test result:

**104 tests passed.**

The count may increase as development continues.

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

It checks for the expected structure, supported top-level fields, valid agent names, and lists of non-empty action names.

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
| `GET` | `/audit/verify` | Verifies stored audit signatures | Audit API key; verification uses server-side HMAC key |
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

A matching Audit API Key is also required.

Example:

```bash
curl "http://127.0.0.1:8000/audit?limit=10" \
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

Authenticates the caller and verifies HMAC signatures of returned audit records.

Example:

```bash
curl "http://127.0.0.1:8000/audit/verify?limit=10" \
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

It verifies only returned records, up to the requested limit. It does not prove that the complete audit history is intact.

### GET /dashboard/

Serves the experimental BURHAN web dashboard.

Static dashboard assets are available through:

```text
/dashboard/
/dashboard/style.css
/dashboard/script.js
```

The dashboard interface is accessible separately from privileged audit data.

Access to `/audit` and `/audit/verify` remains controlled by the FastAPI backend.

The dashboard currently supports authenticated audit retrieval, signature verification summaries, and agent activity visualizations.

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

Defines dashboard sections, summary cards, the audit history table, verification controls, activity chart containers, and the API key form.

**`style.css` — Appearance**

Provides dark-themed styling, responsive layouts, tables, buttons, spacing, typography, horizontal chart bars, and screen-reader-friendly hidden text.

**`script.js` — Behaviour**

Initializes the dashboard, manages loading states, handles form submission, makes authenticated audit requests, verifies audit integrity, calculates activity summaries, and renders records and charts.

### Authenticated Audit History Viewer

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

### Audit Integrity Verification Interface

The **Verify Audit Integrity** button connects to the protected `/audit/verify` endpoint.

The dashboard sends the Audit API Key in the `X-API-Key` HTTP header.

The API returns signature verification results, which populate four summary cards:

| Card | Meaning |
|---|---|
| Total Audit Records | Number of records checked in the returned verification batch |
| Valid Signatures | Number of signatures matching the current HMAC key |
| Invalid Signatures | Number of signatures that fail verification |
| Unsigned Records | Number of records without HMAC signatures |

The interface also displays a textual verification summary.

The HMAC secret is not transmitted to the browser.

**Security limitation:** These counters describe the returned verification batch, not the entire stored audit history.

### Agent Activity Visualizations

The Agent Activity section contains two charts.

#### Allowed vs. Denied Actions

This chart counts the values of the `allowed` field in the loaded audit records.

It displays:

- Allowed event count.
- Allowed event percentage.
- Denied event count.
- Denied event percentage.

Only explicit Boolean values are included in these calculations.

The chart uses horizontal CSS bars and readable text labels.

#### Activity by Agent

This chart groups loaded audit events by agent name.

It displays:

- Agent identity.
- Number of audit events associated with that agent.
- A horizontal bar representing relative activity.

Agents are ordered by event count, highest first.

Missing agent names are grouped under `Unknown agent`.

The chart uses the most active agent as the relative bar-width reference.

Therefore, its bar widths represent activity **relative to the most active agent**, rather than percentages of all events.

#### Chart Data Source

Both charts reuse the authenticated records returned by:

```text
GET /audit?limit=100
```

They do not issue separate network requests.

The data is temporarily held in JavaScript memory.

When a new audit history request begins, previous chart data is cleared.

If no records are available, the interface displays appropriate empty-data messages.

#### Counting Limitations

These charts summarize **audit events**, not unique authenticated requests.

A single enforcement workflow may create multiple audit records.

Additionally, pre-execution audit events may use `allowed: false` as a pending-state placeholder.

Consequently, the Allowed vs. Denied chart should not be interpreted as a definitive count of unique policy decisions without additional event-state filtering.

### Dashboard Security Improvements

Stage 34 introduced several additional safeguards.

#### 1. Credential Handling

The dashboard accepts the Audit API Key through a password input.

The key is sent to protected endpoints through the `X-API-Key` header rather than being placed in the request URL.

When an audit history request begins:

1. The dashboard reads the entered key.
2. It clears the password input field.
3. It invalidates the previously retained key.
4. It requests authenticated audit history.
5. It retains the new key in memory only after a successful response containing the expected audit event structure.

The retained key can then be reused for audit integrity verification.

The dashboard does not deliberately save the key in browser storage.

**Limitation:** The key is still handled by JavaScript and temporarily retained in page memory. This is not equivalent to a production authentication session.

#### 2. Verification Error Handling

The verification interface distinguishes several failure cases.

| Condition | Dashboard Behaviour |
|---|---|
| Missing retained Audit API Key | Requests that the user load audit records first |
| HTTP `401` | Reports an authentication failure and invalidates the retained key |
| HTTP `403` | Reports that verification is disabled or not configured |
| HTTP `429` | Displays a rate-limit-related message |
| Other unsuccessful HTTP responses | Reports temporary unavailability |
| Unexpected response structure | Reports an invalid verification response |
| Network or JavaScript processing error | Displays a connection-related error message |

Handling HTTP `429` in the frontend does not mean BURHAN currently implements rate limiting.

These messages improve troubleshooting but do not replace proper server-side security controls.

#### 3. Stale Result Prevention

When a new audit history request begins, BURHAN clears:

- Previously displayed audit records.
- The Allowed vs. Denied Actions chart.
- The Activity by Agent chart.
- Previous verification summary counts.
- The previous verification result message.

This reduces the risk of displaying results from an earlier authenticated request as though they belong to the current request.

**Limitation:** This reset does not itself guarantee safe handling of every possible overlapping or out-of-order asynchronous request. More comprehensive request-state handling remains a future improvement.

#### 4. Safe DOM Rendering

Audit records and chart labels are rendered using DOM text operations such as `textContent`.

This prevents those values from being interpreted as HTML by the browser.

The dashboard avoids common unsafe HTML insertion patterns in its reviewed JavaScript source.

**Limitation:** Source-level checks are not a complete cross-site scripting security assessment.

#### 5. Accessibility Improvements

The dashboard includes:

- A clear heading hierarchy.
- Descriptive form labels.
- Named buttons.
- Status messages using `role="status"`.
- A labelled Agent Activity section.
- A descriptive audit table caption.
- Explicit `scope="col"` attributes for audit table column headers.
- Visually hidden text that remains available to assistive technologies.

These improvements support accessibility but do not establish compliance with a complete accessibility standard.

#### 6. HTTP Security Headers

The FastAPI application applies basic security headers through HTTP middleware.

| Header | Value | Purpose |
|---|---|---|
| `X-Content-Type-Options` | `nosniff` | Reduces MIME-type sniffing risks |
| `Referrer-Policy` | `no-referrer` | Prevents referrer information from being sent |
| `Cache-Control` | `no-store` | Discourages caching of protected audit API responses |

The `Cache-Control: no-store` header is applied to:

```text
/audit
/audit/verify
```

The `nosniff` and `no-referrer` headers are applied to the application responses handled by the middleware, including dashboard and audit API responses.

The middleware was checked using FastAPI's test client, including responses where audit access was disabled.

**Limitations:**

- These headers do not replace HTTPS.
- A comprehensive Content Security Policy has not been implemented.
- The current middleware does not establish a complete browser security policy.
- Static dashboard assets are not all assigned the same no-store policy as protected audit responses.

### Dashboard Security and Testing

Stage 34 expanded the project's security checks.

The automated tests now include checks for:

- Security headers on dashboard and protected audit responses.
- Selected credential-handling properties in the dashboard JavaScript source.
- Avoidance of browser storage APIs for credentials.
- Avoidance of selected unsafe HTML insertion patterns.
- Text-based rendering of audit fields.
- Credential invalidation logic.
- Verification summary reset logic.

The dashboard was also manually tested to confirm:

1. Valid authentication loads audit records.
2. Integrity verification updates the summary cards.
3. Both activity charts display returned audit data.
4. An incorrect API key produces an authentication failure.
5. Previous records, activity charts, and verification summaries clear when a new audit history request begins.

**Latest completed test milestone: 104 passing tests.**

These tests provide useful regression coverage but are not a penetration test, a complete security assessment, or comprehensive automated browser testing.

### Current Dashboard Limitations

- The dashboard is a development prototype, not a production operations console.
- Audit history is limited to a maximum of 100 returned records per request.
- Activity charts summarize returned records, not necessarily the entire database.
- Activity counts represent audit events rather than unique requests.
- The charts do not currently provide advanced filtering or time-based analysis.
- The dashboard relies on an API key entered through a browser form.
- The Audit API Key is temporarily retained in JavaScript memory after successful authentication.
- The dashboard does not provide production-grade user sessions or identity management.
- The frontend does not independently verify HMAC signatures.
- Successful signature checks do not prove that records have not been deleted.
- More comprehensive request-concurrency handling remains unimplemented.
- A complete Content Security Policy has not been introduced.
- Comprehensive frontend security assessment and automated browser coverage remain future work.

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

**8. Browser Credential Handling**

The dashboard currently accepts an Audit API Key through a browser form and temporarily retains it in JavaScript memory for verification requests.

This is not a production authentication solution.

**9. Activity Chart Interpretation**

The activity charts count audit events. They do not establish unique request counts, actual external tool executions, or complete historical coverage.

**10. Limited Operational Hardening**

BURHAN does not yet provide comprehensive rate limiting, monitoring, external append-only audit storage, recovery controls, or production-grade secret management.

**11. Incomplete Audit Outcomes**

A failed final audit write may leave the recorded outcome incomplete after simulated execution.

**12. Limited Browser Security Hardening**

Basic HTTP security headers and selected frontend safeguards have been implemented, but a comprehensive Content Security Policy, hardened browser sessions, and full frontend security testing remain outstanding.

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
  - [x] Add an Audit API Key input form.
  - [x] Connect the dashboard to the authenticated `/audit` endpoint.
  - [x] Display real SQLite audit records.
  - [x] Handle authentication and retrieval errors.
  - [x] Add dashboard integration checks.

- [x] **Stage 32 — Audit Integrity Verification Interface**
  - [x] Connect the dashboard to `/audit/verify`.
  - [x] Use the existing authenticated audit API mechanism.
  - [x] Display valid, invalid, and unsigned signature counts.
  - [x] Populate the four Audit Summary cards with live verification data.
  - [x] Present verification outcomes clearly.
  - [x] Verify a signed audit event through the dashboard.
  - [x] Add verification interface regression tests.
  - [x] Configure persistent development secrets in GitHub Codespaces.

- [x] **Stage 33 — Agent Activity Visualizations**
  - [x] Add an Agent Activity dashboard section.
  - [x] Create responsive activity chart styling.
  - [x] Reuse authenticated audit history data.
  - [x] Calculate allowed and denied audit event counts.
  - [x] Display the Allowed vs. Denied Actions chart.
  - [x] Calculate audit activity by agent.
  - [x] Display the Activity by Agent chart.
  - [x] Connect both charts to real audit records.
  - [x] Handle empty activity data and clear stale results.
  - [x] Correct singular and plural event labels.
  - [x] Add visualization regression tests.

- [x] **Stage 34 — Dashboard Security and Testing**
  - [x] Review dashboard security and credential handling.
  - [x] Retain Audit API Keys only after successful authenticated retrieval.
  - [x] Improve verification error handling.
  - [x] Clear outdated audit records, charts, and verification summaries.
  - [x] Review safe DOM rendering and XSS-related patterns.
  - [x] Improve dashboard table accessibility.
  - [x] Add baseline FastAPI HTTP security headers.
  - [x] Apply no-store caching instructions to protected audit API responses.
  - [x] Add automated HTTP security-header tests.
  - [x] Add dashboard security regression tests.
  - [x] Complete manual dashboard and browser checks.

- [ ] **Stage 35 — Documentation and v0.4.0 Release**
  - [x] Verify repository state and existing test baseline.
  - [x] Review application version references.
  - [x] Update the FastAPI application version to `0.4.0`.
  - [x] Finalize README documentation for the completed Phase 4 features.
  - [ ] Review project security limitations and release documentation.
  - [ ] Run the complete test suite and final release checks.
  - [ ] Prepare the release changes.
  - [ ] Publish and verify the GitHub `v0.4.0` release.

**Latest Phase 4 test milestone: 104 passing backend tests.**

### Longer-Term Research Directions

- [ ] Explore integration with real AI agent tool calls.
- [ ] Investigate stronger identity and key management.
- [ ] Explore hash chaining and externally anchored audit records.
- [ ] Investigate detection of missing or deleted audit events.
- [ ] Expand policy administration capabilities.
- [ ] Improve operational monitoring and developer tooling.
- [ ] Investigate safer browser authentication workflows.
- [ ] Add comprehensive automated browser and accessibility testing.
- [ ] Explore stronger audit verification and data provenance mechanisms.

Features listed as planned are not yet implemented.

## Intended Purpose

BURHAN is currently intended for:

- Portfolio demonstration and professional evaluation.
- Research into AI agent security architecture.
- Exploring permission-based authorization.
- Demonstrating persistent decision auditing.
- Developing experimental audit integrity mechanisms.
- Studying secure dashboard integration with authenticated backend APIs.
- Visualizing agent activity and policy outcomes.
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