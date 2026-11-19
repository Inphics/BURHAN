
# BURHAN

### Autonomous AI Agent Safety & Verification Framework

**Every action accountable. Every decision verifiable.**

BURHAN is an independently developed Python framework prototype for evaluating AI agent actions against defined security policies, simulating permitted actions, and recording decisions in a persistent audit log.

The project explores how AI agent systems can become more transparent, accountable, and easier to inspect.

> **Project Notice:** BURHAN is a proprietary research and development project made publicly visible for portfolio demonstration and technical review. It is not open-source software, and no general license to use, modify, or redistribute its source code is granted. See [Copyright and Usage](#copyright-and-usage).

## Why BURHAN?

The name **BURHAN** originates from the Arabic word **بُرْهَان (burhān)**, meaning *proof*, *evidence*, or *clear demonstration*. Adopted into Turkish as **Burhan**, where it is also used as a personal name, the word preserves its association with evidence and the demonstration of truth. This shared Arabic–Turkish linguistic heritage reflects the project's central philosophy: trust should be supported by evidence, and decisions should be open to examination.

BURHAN is built around the idea that trustworthy AI systems should produce more than decisions. They should provide understandable reasons, enforceable boundaries, and inspectable records of their behavior.

## Current Features

- **Policy Evaluation:** Checks whether an authenticated agent is permitted to perform an action.
- **JSON Policy Configuration:** Loads permissions from `backend/config/policies.json`, validates the configuration, and denies unlisted agents and actions by default.
- **Permission Management:** Supports granting and revoking permissions in the running policy engine; these changes do not automatically update the JSON file.
- **API-Key Agent Authentication:** Associates configured API keys with supported agent identities.
- **Enforcement Prototype:** Checks permissions before simulating permitted actions; no external tools or real-world operations are executed.
- **Structured Audit Logging:** Records UTC timestamps, agents, actions, decisions, reasons, execution statuses, and request IDs.
- **SQLite Persistence:** Retains audit events between application restarts.
- **Optional HMAC-SHA256 Audit Signing:** Signs audit fields when `BURHAN_AUDIT_HMAC_KEY` is configured; strict signing can be required explicitly.
- **Audit Integrity Verification:** Checks individual and collected signatures, distinguishing `valid`, `invalid`, and `unsigned` records.
- **Protected Audit APIs:** Offers authenticated `GET /audit` and `GET /audit/verify` endpoints, both disabled unless audit inspection is enabled.
- **Failure Handling:** Includes tested safeguards for authentication failures, invalid input, malformed signatures, missing configuration, and audit database failures.
- **Automated Tests:** **93 passing backend tests** at the latest completed Stage 28 test run.

## Project Status

**Status: Experimental backend prototype | Public portfolio demonstration | All rights reserved**

BURHAN is under active research and development. The current application now reports **version `0.3.0`**. The corresponding GitHub release is being prepared and has not yet been published.

The framework includes API-key authentication, JSON-based authorization rules, simulated enforcement, persistent audit logging, and HMAC-based integrity checks. These are prototype mechanisms, not proof of production-grade security.

**BURHAN is not production-ready and should not be relied upon as the sole security boundary for real AI agents or sensitive systems.**

Public availability is intended for portfolio presentation and professional evaluation; it does not grant permission to use, modify, redistribute, or incorporate the source code into other projects.

## Architecture

BURHAN's backend consists of the following components:

| Component | Location | Responsibility |
|---|---|---|
| FastAPI Application | `backend/app/main.py` | Exposes endpoints and handles requests |
| Agent Authentication | `backend/app/security/agent_auth.py` | Resolves an agent identity from its API key |
| Policy Engine | `backend/app/policies/policy_engine.py` | Loads and checks configured permissions |
| Policy Configuration | `backend/config/policies.json` | Defines allowed actions for each agent |
| Enforcement Engine | `backend/app/execution/enforcement_engine.py` | Checks authorization and coordinates simulated execution |
| Audit Logger | `backend/app/evaluation/audit_logger.py` | Creates and optionally signs audit events |
| Audit Database | `backend/app/evaluation/audit_database.py` | Stores and retrieves SQLite audit records |
| Audit Integrity | `backend/app/evaluation/audit_integrity.py` | Calculates and verifies SHA-256 and HMAC-SHA256 values |

### Request Flow

```text
Authenticated API client
         |
         v
     FastAPI API
         |
         v
  Agent authentication
         |
         v
  JSON-backed policy engine
         |
         v
    Allow or deny
         |
         +---- POST /evaluate: record decision, return result
         |
         +---- POST /enforce: record request, simulate if allowed,
         |                   record final outcome, return result
         |
         v
       SQLite audit log
         |
         +---- GET /audit: inspect recent records (authorized)
         |
         +---- GET /audit/verify: verify returned signatures (authorized)
```

For each authenticated `POST /enforce` call, BURHAN assigns a request ID shared by its initial and final audit records. The pre-execution record is written before the enforcement engine is invoked. Execution is **simulated**, not performed against external tools.

## Technical Setup and Development Reference

> **Usage restriction:** These instructions document technical setup for transparency and professional evaluation. They do not grant permission to use, modify, or redistribute BURHAN. See [Copyright and Usage](#copyright-and-usage).

### Prerequisites

- Python 3.11 or newer
- Git
- A terminal

Development and testing have primarily been performed in GitHub Codespaces. Other environments may require adjustments.

### 1. Clone the Repository

```bash
git clone https://github.com/Inphics/BURHAN.git
cd BURHAN
```

### 2. Create a Virtual Environment

Linux, macOS, or GitHub Codespaces:

```bash
python -m venv .venv
source .venv/bin/activate
```

Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

```bash
python -m pip install -r backend/requirements.txt
```

### 4. Configure Local API Keys

The example below uses **development-only placeholders**. Replace these with separately generated, strong secrets in an authorized development environment. Never commit real keys to GitHub.

```bash
export BURHAN_RESEARCH_AGENT_KEY="replace-with-a-unique-agent-secret"
export BURHAN_ADMIN_AGENT_KEY="replace-with-another-unique-agent-secret"
export BURHAN_AUDIT_API_KEY="replace-with-a-unique-audit-api-secret"
export BURHAN_AUDIT_HMAC_KEY="replace-with-a-separate-hmac-secret"
export BURHAN_REQUIRE_AUDIT_SIGNING=true
export BURHAN_ENABLE_AUDIT_API=true
```

Setting `BURHAN_ENABLE_AUDIT_API=true` enables both audit routes. Omit it or set it to `false` to keep audit inspection disabled. `BURHAN_REQUIRE_AUDIT_SIGNING=true` requires an HMAC key before the audit logger can save a new event. Both flags use the exact lowercase value `true`.

These exports apply to the current shell session. Keep Codespaces forwarded ports **private**, use HTTPS for any network access, and do not expose prototype endpoints publicly.

### 5. Start the API

```bash
python -m uvicorn backend.app.main:app --reload
```

Local addresses:

- API: `http://127.0.0.1:8000`
- Health check: `http://127.0.0.1:8000/health`
- Interactive API documentation: `http://127.0.0.1:8000/docs`

### 6. Evaluate an Agent Action

```bash
curl -X POST http://127.0.0.1:8000/evaluate \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $BURHAN_RESEARCH_AGENT_KEY" \
  -d '{"action":"delete"}'
```

Example response (reason text comes from the active policy):

```json
{
  "allowed": false,
  "reason": "Agent 'research_agent' is not permitted to perform 'delete'."
}
```

The agent identity is derived from the API key, **not** provided by the request body.

### 7. Enforce an Agent Action (Simulation)

```bash
curl -X POST http://127.0.0.1:8000/enforce \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $BURHAN_RESEARCH_AGENT_KEY" \
  -d '{"action":"read"}'
```

The response describes the policy decision and simulated outcome. An `executed` value of `true` means **simulation succeeded**, not that a real operation occurred.

### 8. Inspect Audit Records

With audit inspection enabled and an audit API key configured:

```bash
curl http://127.0.0.1:8000/audit?limit=10 \
  -H "X-API-Key: $BURHAN_AUDIT_API_KEY"
```

### 9. Verify Audit Records

```bash
curl http://127.0.0.1:8000/audit/verify?limit=10 \
  -H "X-API-Key: $BURHAN_AUDIT_API_KEY"
```

A response summarizes the inspected records as `valid`, `invalid`, or `unsigned`. The verification endpoint requires `BURHAN_AUDIT_HMAC_KEY` on the server. It **does not** return that secret.

### 10. Run Automated Tests

```bash
python -m pytest backend/tests/ -v
```

**Latest verified result: 93 passing backend tests** after Stage 28. Test counts may change during subsequent development.

## Policy Configuration

Default permissions are stored in `backend/config/policies.json`:

```json
{
  "permissions": {
    "research_agent": ["read", "report"],
    "admin_agent": ["read", "report", "update", "delete"]
  }
}
```

The policy engine validates the configuration at startup, including the expected `permissions` object, lists of non-empty action strings, non-empty agent names, and supported top-level fields. Missing or malformed configuration causes initialization to fail rather than silently reverting to permissive hardcoded rules.

Unknown agents and actions not explicitly listed are denied by default. `grant_permission()` and `revoke_permission()` change the in-memory engine state; they are **not** a persistent policy administration interface. Protect access to the configuration file: whoever can change it can alter authorization rules.

## API Reference

| Method | Endpoint | Description | Access |
|---|---|---|---|
| `GET` | `/` | Returns project information and API status | No API key required |
| `GET` | `/health` | Returns basic application health | No API key required |
| `POST` | `/evaluate` | Evaluates an action and logs the decision | Agent API key |
| `POST` | `/enforce` | Evaluates and simulates an allowed action, with audit records | Agent API key |
| `GET` | `/audit` | Retrieves recent stored audit events | Audit API enabled and audit API key |
| `GET` | `/audit/verify` | Verifies HMAC signatures on recent audit events | Audit API enabled, audit API key, and server HMAC key |

### POST /evaluate

The JSON body contains an action:

```json
{
  "action": "read"
}
```

Clients supply `X-API-Key` to identify the agent. A missing or invalid agent key returns HTTP `401`. Successful authorization checks return a policy decision with `allowed` and `reason` fields; denied actions may still yield HTTP `200` with `allowed: false`.

### POST /enforce

Accepts the same JSON body and agent authentication header. The endpoint creates an initial audit record before attempting enforcement, checks the policy, and simulates the action only when permitted. A final audit event records the outcome.

Possible audit execution statuses include:

| Status | Meaning |
|---|---|
| `not_attempted` | Execution has not been attempted or a policy-only evaluation occurred |
| `blocked` | Policy denied the requested action |
| `simulated` | Allowed action was successfully simulated |
| `failed` | An allowed action simulation failed |

The `executed` response field indicates simulated execution only. BURHAN does not perform file deletion, system changes, external commands, or other real-world tool actions.

### GET /audit

Disabled by default. When enabled, requires the server's `BURHAN_AUDIT_API_KEY` and the matching `X-API-Key` request header.

The endpoint returns recent records in reverse insertion order:

```json
{
  "total_events": 1,
  "events": [
    {
      "id": 1,
      "timestamp": "2026-11-19T12:00:00+00:00",
      "agent": "research_agent",
      "action": "read",
      "allowed": true,
      "reason": "Agent 'research_agent' is permitted to perform 'read'.",
      "execution_status": "simulated",
      "request_id": "example-request-id",
      "event_hmac": null
    }
  ]
}
```

*Illustrative response:* `event_hmac: null` represents an unsigned event; signed events contain a 64-character hexadecimal signature. The endpoint **retrieves records but does not automatically verify their signatures**.

The optional `limit` query parameter defaults to `100` and accepts values from `1` through `100`.

### GET /audit/verify

Uses the same audit access controls and additionally requires the server-side `BURHAN_AUDIT_HMAC_KEY`.

Example response:

```json
{
  "total": 3,
  "valid": 1,
  "invalid": 1,
  "unsigned": 1,
  "results": [
    {"id": 3, "request_id": "example-3", "status": "valid"},
    {"id": 2, "request_id": "example-2", "status": "invalid"},
    {"id": 1, "request_id": null, "status": "unsigned"}
  ]
}
```

- **`valid`**: A stored signature matches the signed record fields using the configured HMAC key.
- **`invalid`**: A stored signature is malformed or does not match the record.
- **`unsigned`**: The record has no signature (`null`), as with historical records.

The endpoint verifies **only the latest returned records**, up to the `limit` (default `100`, range `1`–`100`). Its `total` is the number examined, **not** the complete database count. A result of zero invalid records is not evidence that missing or deleted records never existed.

Expected error handling includes HTTP `403` when audit inspection is disabled or its API key is not configured, HTTP `401` for missing or incorrect credentials, HTTP `503` when the HMAC verification key or audit database is unavailable, and HTTP `422` for invalid query limits.

### Interactive API Documentation

FastAPI generates development documentation at:

- Swagger UI: `http://127.0.0.1:8000/docs`
- OpenAPI schema: `http://127.0.0.1:8000/openapi.json`

## Enforcement Audit Safeguards

For authenticated requests to `/enforce`, BURHAN:

1. Attempts to save a pre-execution audit record before invoking the enforcement engine.
2. Returns HTTP `503 Service Unavailable` and does not call the executor if the initial audit write fails.
3. Evaluates the requested action against the loaded policy.
4. Simulates permitted actions; denied actions do not reach the executor.
5. Attempts to save a final audit record containing the policy decision and execution status.

The initial and final records for an enforcement request share a generated `request_id`, allowing related records to be associated.

**Important qualifications:** The pre-execution record currently stores `allowed: false` as a pending placeholder, **not** as a final policy denial. If the final audit write fails, the API returns `503`, but a permitted action might already have been simulated. Audit persistence and simulation are not a transactional unit.

## Audit Integrity and Security Model

### HMAC-SHA256 Signing

When `BURHAN_AUDIT_HMAC_KEY` is set, newly logged events receive a keyed HMAC-SHA256 signature covering these fields:

- `timestamp`
- `agent`
- `action`
- `allowed`
- `reason`
- `execution_status`
- `request_id`

Verification recomputes the signature using the same protected secret and checks whether the signed fields have changed. The database's `id` is **not** part of the signed content.

`BURHAN_REQUIRE_AUDIT_SIGNING=true` enables strict signing behavior: the logger refuses to save new events if the HMAC key is missing. Without strict signing, a missing HMAC key still permits unsigned events for prototype compatibility. **Strict mode is optional, not the default.**

The HMAC key must be protected independently of the SQLite database and source repository. Never commit the secret or display it in audit responses.

### Known Limitations

1. **Simulated enforcement only:** BURHAN does not control arbitrary external AI tools or provide a production sandbox.
2. **Prototype identity model:** API keys identify configured agent roles; there is no full identity lifecycle, role administration, or production authentication infrastructure.
3. **Not tamper-proof storage:** HMAC detects changes to inspected signed fields if the secret stays protected; it does **not** detect deletion, reordering, replay, rollback, or wholesale database replacement.
4. **Unsigned historical events:** Records created without an HMAC cannot be cryptographically verified. They are reported as `unsigned`, not `valid`.
5. **Limited verification scope:** `/audit/verify` checks only returned records, not whether the audit history is complete. `/audit` does not automatically perform verification.
6. **Optional strict signing:** The default prototype configuration can still write unsigned events if the HMAC key is absent.
7. **Configuration trust:** JSON policies are validated but are not independently signed or protected against modification by someone with repository or deployment access.
8. **Operational hardening:** The prototype does not provide comprehensive rate limiting, monitoring, recovery controls, append-only external audit storage, or production-grade secret management.
9. **Audit completion limitations:** A failed final audit write can leave the recorded outcome incomplete after a simulation.

BURHAN should not be used as the sole security boundary for production AI agents or sensitive systems.

### Responsible Development

BURHAN is intended for portfolio demonstration, professional evaluation, research into agent security architecture, and incremental testing of accountability mechanisms. Security concerns may be reported to the repository owner through an appropriate private communication channel.

## Development Roadmap

### Phase 1 — Backend Foundation (Completed)

- [x] Establish the Python project structure.
- [x] Implement a permission-based policy engine.
- [x] Support in-memory permission granting and revocation.
- [x] Create a FastAPI backend and action evaluation endpoint.
- [x] Record policy decisions with UTC timestamps.
- [x] Persist audit events using SQLite.
- [x] Provide optional audit inspection.
- [x] Add automated tests.

### Phase 2 — Documentation and Backend Hardening (Completed)

- [x] Document the framework's purpose, architecture, and limitations.
- [x] Add setup and API reference documentation.
- [x] Expand authentication, authorization, and failure-path tests.
- [x] Configure SQLite audit database paths and API query limits.
- [x] Add API-key authentication for agent and audit access.
- [x] Introduce simulated enforcement and audit safeguards.
- [x] Publish the `v0.2.0` backend prototype release.

### Phase 3 — Agent Safety and Verification Hardening (In Progress)

- [x] **Stage 24:** Add request IDs to associate enforcement audit records.
- [x] **Stage 25:** Add HMAC audit signing, verification, and optional strict signing.
- [x] **Stage 26:** Load and validate JSON policy configuration files.
- [x] **Stage 27:** Add an authenticated audit verification API.
- [x] **Stage 28:** Expand security tests and failure handling (**93 passing tests**).
- [x] **Stage 29:** Finalize documentation, update version metadata, and publish `v0.3.0`.

### Phase 4 — Dashboard and Developer Experience (Planned)

- [ ] Build a web dashboard for policy decisions and audit events.
- [ ] Add filtering and searching for audit history.
- [ ] Visualize agent activity and policy outcomes.
- [ ] Improve configuration, developer tooling, and operational visibility.

### Longer-Term Research Directions

- [ ] Investigate integrations with real AI agent tool calls and enforcement boundaries.
- [ ] Explore stronger identity and key-management mechanisms.
- [ ] Investigate hash chaining, external anchoring, and techniques for detecting missing audit records.
- [ ] Extend policy administration and verification workflows.

These are research directions, not implemented or promised capabilities.

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

BURHAN is experimental software provided for demonstration purposes. No warranty is made regarding its reliability, security, or suitability for any particular purpose.