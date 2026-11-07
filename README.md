
# BURHAN

### Autonomous AI Agent Safety & Verification Framework

**Every action accountable. Every decision verifiable.**

BURHAN is an open-source Python framework prototype for evaluating AI agent actions against defined security policies and recording the resulting decisions in a persistent audit log.

The project explores how AI agent systems can become more transparent, accountable, and easier to inspect.

## Why BURHAN?

The name **BURHAN** originates from the Arabic word **بُرْهَان (burhān)**, meaning *proof*, *evidence*, or *clear demonstration*. Adopted into Turkish as **Burhan**, where it is also used as a personal name, the word preserves its original association with evidence, certainty, and the demonstration of truth. This shared Arabic–Turkish linguistic heritage reflects the project's central philosophy: that trust should be supported by evidence, and every decision should be open to examination.

This shared linguistic heritage reflects the project's central philosophy:

**Every action accountable. Every decision verifiable.**

BURHAN is built around the idea that trustworthy AI systems should produce more than decisions. They should provide understandable reasons, enforceable boundaries, and inspectable records of their behavior.

The name represents the project's long-term ambition: moving from simply trusting AI agents toward systems in which actions can be examined and justified.

## Current Features

- **Policy Evaluation:** Checks whether an agent is permitted to perform a requested action.
- **Permission Management:** Supports granting and revoking permissions within the policy engine.
- **REST API:** Provides FastAPI endpoints for evaluating actions and checking application health.
- **Audit Logging:** Records policy decisions with UTC timestamps, agent names, actions, and reasons.
- **SQLite Persistence:** Stores audit events in a local SQLite database so records survive application restarts.
- **Audit Inspection:** Provides an optional `/audit` endpoint, disabled by default.
- **Automated Testing:** Includes 17 passing tests covering policy behavior, audit logging, persistence, and API responses.

## Project Status

**Status: Early-stage backend prototype**

BURHAN currently provides policy evaluation and persistent audit logging. It does not yet authenticate agents, enforce decisions on external tools, or provide tamper-proof audit records.

It is intended for development, experimentation, and learning—not production security enforcement.

## Architecture

BURHAN currently consists of three main backend components:

1. **FastAPI Application:** Receives action evaluation requests and exposes API endpoints.
2. **Policy Engine:** Evaluates requested actions against predefined agent permissions.
3. **Audit System:** Records policy decisions and persists them in SQLite.

### Request Flow

```text
          AI Agent / API Client
                   |
                   v
          FastAPI Application
             POST /evaluate
                   |
                   v
              Policy Engine
                   |
                   v
            Policy Decision
           (Allowed / Denied)
                   |
                   v
               Audit Logger
                   |
                   v
             SQLite Database
                   |
                   v
            Persistent Record
```

When an API client submits an evaluation request, BURHAN:

1. Receives the agent name and requested action.
2. Checks the action against the policy engine's permissions.
3. Produces an allow-or-deny decision with a reason.
4. Records the decision with a UTC timestamp.
5. Saves the audit event in SQLite.
6. Returns the policy decision to the client.

### Main Components

| Component | Location | Responsibility |
|-----------|----------|----------------|
| FastAPI Application | `backend/app/main.py` | API endpoints and request handling |
| Policy Engine | `backend/app/policies/policy_engine.py` | Permission checks and policy decisions |
| Audit Logger | `backend/app/evaluation/audit_logger.py` | Creates timestamped audit events |
| Audit Database | `backend/app/evaluation/audit_database.py` | Stores and retrieves SQLite audit records |

**Security note:** BURHAN currently evaluates requested actions but does not execute or intercept external agent tools. Agent identities are supplied by API clients and are not authenticated.


## Installation and Quick Start

### Prerequisites

- Python 3.11 or newer
- Git
- A terminal (Linux, macOS, Windows, or GitHub Codespaces)

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

### 4. Start the API

```bash
python -m uvicorn backend.app.main:app --reload
```

The API will be available at:

- API: http://127.0.0.1:8000
- Interactive API documentation: http://127.0.0.1:8000/docs
- Health check: http://127.0.0.1:8000/health

### 5. Evaluate an Agent Action

Open another terminal and run:

```bash
curl -X POST http://127.0.0.1:8000/evaluate \
  -H "Content-Type: application/json" \
  -d '{"agent":"research_agent","action":"delete"}'
```

Expected response:

```json
{
  "allowed": false,
  "reason": "Agent 'research_agent' is not permitted to perform 'delete'."
}
```

BURHAN records this policy decision in its SQLite audit database.

### 6. Run Automated Tests

From the project root:

```bash
python -m pytest backend/tests/ -v
```

The current test suite contains 17 tests covering policy evaluation, permission management, audit logging, SQLite persistence, and API behavior.

### Audit Inspection

The `GET /audit` endpoint is disabled by default.

For local development only, start the API with audit inspection enabled:

```bash
BURHAN_ENABLE_AUDIT_API=true python -m uvicorn backend.app.main:app --reload
```

Then visit:

http://127.0.0.1:8000/audit

**Warning:** This configuration does not provide authentication. Anyone with network access to the enabled endpoint can read audit records. Use it only in a trusted local development environment. Keep Codespaces forwarded ports private.


## API Reference

BURHAN exposes four HTTP endpoints through FastAPI.

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Returns basic project information and API status. |
| `GET` | `/health` | Returns the application's health status. |
| `POST` | `/evaluate` | Evaluates an agent's requested action against the policy engine and records the decision. |
| `GET` | `/audit` | Retrieves stored audit events when explicitly enabled. Disabled by default. |

### GET /health

Checks whether the API is responding.

Example response:

```json
{
  "status": "healthy"
}
```

### POST /evaluate

Evaluates whether an agent is permitted to perform a requested action.

Example request:

```json
{
  "agent": "research_agent",
  "action": "read"
}
```

Example response:

```json
{
  "allowed": true,
  "reason": "Agent 'research_agent' is permitted to perform 'read'."
}
```

Example denied request:

```json
{
  "agent": "research_agent",
  "action": "delete"
}
```

Example response:

```json
{
  "allowed": false,
  "reason": "Agent 'research_agent' is not permitted to perform 'delete'."
}
```

Both permitted and denied decisions are recorded in the audit database.

**Note:** A denied policy decision currently returns HTTP 200 with `"allowed": false`. The endpoint evaluates actions; it does not execute them.

### GET /audit

Returns stored audit events in reverse insertion order.

This endpoint is disabled by default and returns HTTP 403 unless the environment variable `BURHAN_ENABLE_AUDIT_API` is set to `true`.

Example response when enabled:

```json
{
  "total_events": 1,
  "events": [
    {
      "id": 1,
      "timestamp": "2026-11-07T10:30:00+00:00",
      "agent": "research_agent",
      "action": "delete",
      "allowed": false,
      "reason": "Agent 'research_agent' is not permitted to perform 'delete'."
    }
  ]
}
```

The timestamp above is illustrative. Actual events use their creation time in UTC.

**Security limitation:** The audit endpoint has no user authentication or authorization when enabled. Do not expose it on an untrusted network.

### Interactive API Documentation

FastAPI automatically generates interactive API documentation:

- Swagger UI: `http://127.0.0.1:8000/docs`
- OpenAPI schema: `http://127.0.0.1:8000/openapi.json`

These pages describe the API's request and response structures.


## Security Model and Known Limitations

BURHAN is an experimental AI agent safety framework focused on policy evaluation, decision transparency, and auditability.

Its current security model is based on predefined permissions and a default-deny approach to unknown agents and unauthorized actions.

### Current Security Capabilities

- **Permission-Based Evaluation:** Checks requested actions against permissions assigned to agent names.
- **Default-Deny Decisions:** Unknown agents and actions without explicit permission are denied.
- **Decision Explanations:** Returns a reason for every policy decision.
- **Persistent Audit Logging:** Records evaluation results in SQLite with UTC timestamps.
- **Audit Inspection Safeguard:** Disables the `/audit` endpoint unless explicitly enabled through configuration.
- **Automated Verification:** Tests policy behavior, API responses, audit logging, and database persistence.

### Known Limitations

**1. No Agent Authentication**

The API accepts agent names supplied by clients. It does not verify that a caller is genuinely the agent it claims to be.

**2. No External Action Enforcement**

BURHAN evaluates whether an action is permitted but does not currently intercept or prevent actions performed by external AI agents or tools.

**3. No Tamper-Proof Audit Storage**

SQLite provides persistent storage, but audit records are not cryptographically signed or protected against modification by someone with database access.

**4. No API Authentication or Rate Limiting**

The API does not currently authenticate callers or enforce request rate limits.

**5. Audit Inspection Is Not Access-Controlled When Enabled**

The `/audit` endpoint is disabled by default. When enabled, it can be accessed by anyone who can reach the API.

**6. Development-Oriented Policy Configuration**

Permissions are currently defined in Python code and are not managed through a production-grade policy administration system.

**7. Limited Operational Hardening**

The prototype does not yet include comprehensive monitoring, database backup and recovery, or production deployment controls.

### Intended Use

BURHAN is suitable for:

- Learning about AI agent security architecture.
- Experimenting with permission-based policy evaluation.
- Demonstrating persistent decision auditing.
- Developing and testing future safety mechanisms.

BURHAN should not currently be used as the sole security boundary for production AI agents or sensitive systems.

### Responsible Development

Future improvements will prioritize authenticated agent identities, stronger policy enforcement, protected audit access, and more robust verification mechanisms.

Security-related contributions and responsible vulnerability reports are welcome.


## Development Roadmap

BURHAN is being developed incrementally, with an emphasis on clear architecture, testability, and responsible security engineering.

### Phase 1 — Backend Foundation (Completed)

- [x] Establish the Python project structure.
- [x] Implement a permission-based policy engine.
- [x] Support permission granting and revocation.
- [x] Create a FastAPI backend.
- [x] Implement action evaluation through the REST API.
- [x] Record policy decisions with UTC timestamps.
- [x] Persist audit events using SQLite.
- [x] Provide an optional audit inspection endpoint.
- [x] Add automated tests for policy evaluation, auditing, and persistence.

### Phase 2 — Documentation and Backend Hardening (In Progress)

- [x] Document the framework's purpose and architecture.
- [x] Add installation and API usage instructions.
- [x] Document the security model and known limitations.
- [ ] Expand automated tests for edge cases and failure scenarios.
- [ ] Improve audit database configuration and query limits.
- [ ] Introduce authenticated access to sensitive API functionality.
- [ ] Add structured error handling and operational safeguards.
- [ ] Prepare a documented backend release.

### Phase 3 — Agent Integration and Verification (Planned)

- [ ] Integrate policy checks with actual AI agent tool calls.
- [ ] Introduce authenticated agent identities.
- [ ] Expand the policy model beyond predefined permissions.
- [ ] Investigate stronger audit integrity mechanisms.
- [ ] Develop verification workflows for agent actions and outcomes.

### Phase 4 — Dashboard and Developer Experience (Planned)

- [ ] Build a web dashboard for policy decisions and audit events.
- [ ] Add filtering and searching for audit history.
- [ ] Visualize agent activity and policy outcomes.
- [ ] Improve configuration and developer tooling.

### Long-Term Vision

BURHAN aims to evolve into a framework that helps developers evaluate, constrain, and inspect autonomous AI agent behavior.

The long-term goal is to make agent actions more accountable through enforceable policies, reliable audit records, and stronger verification mechanisms.

Features listed as planned are not yet implemented.
