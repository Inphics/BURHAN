
from pathlib import Path


def test_dashboard_html_contains_required_elements():
    """Check that the dashboard contains its essential HTML elements."""

    dashboard_path = (
        Path(__file__).resolve().parents[1]
        / "app"
        / "dashboard"
        / "index.html"
    )

    html = dashboard_path.read_text(encoding="utf-8")

    assert "<title>BURHAN | Security Dashboard</title>" in html

    assert 'id="total-records"' in html
    assert 'id="valid-records"' in html
    assert 'id="invalid-records"' in html
    assert 'id="unsigned-records"' in html

    assert 'id="verify-button"' in html
    assert 'id="verification-result"' in html
    assert 'id="audit-records"' in html

    assert 'href="style.css"' in html
    assert 'src="script.js"' in html


def test_dashboard_verification_button_disabled_by_default():
    """The dashboard must not offer unconnected verification actions."""

    dashboard_path = (
        Path(__file__).resolve().parents[1]
        / "app"
        / "dashboard"
        / "index.html"
    )

    html = dashboard_path.read_text(encoding="utf-8")

    assert 'id="verify-button" type="button" disabled' in html

    assert "Verification is not connected yet." in html


def test_dashboard_assets_exist_and_are_linked():
    """Check that dashboard CSS and JavaScript files are available."""

    dashboard_directory = (
        Path(__file__).resolve().parents[1]
        / "app"
        / "dashboard"
    )

    html_path = dashboard_directory / "index.html"
    css_path = dashboard_directory / "style.css"
    javascript_path = dashboard_directory / "script.js"

    assert html_path.is_file()
    assert css_path.is_file()
    assert javascript_path.is_file()

    html = html_path.read_text(encoding="utf-8")
    css = css_path.read_text(encoding="utf-8")
    javascript = javascript_path.read_text(encoding="utf-8")

    # HTML must link to the correct dashboard assets.
    assert 'href="style.css"' in html
    assert 'src="script.js"' in html

    # Check for essential styling and initialization code.
    assert ".dashboard-header" in css
    assert ".summary-cards" in css
    assert ".audit-section" in css

    assert "DOMContentLoaded" in javascript
    assert 'getElementById("verify-button")' in javascript


def test_fastapi_serves_dashboard_and_assets():
    """FastAPI should serve the dashboard and its static assets."""

    from fastapi.testclient import TestClient
    from backend.app.main import app

    client = TestClient(app)

    # Check the HTML page.
    page_response = client.get("/dashboard/")

    assert page_response.status_code == 200
    assert "BURHAN | Security Dashboard" in page_response.text
    assert "text/html" in page_response.headers["content-type"]

    # Check the CSS file.
    css_response = client.get("/dashboard/style.css")

    assert css_response.status_code == 200
    assert ".dashboard-header" in css_response.text

    # Check the JavaScript file.
    js_response = client.get("/dashboard/script.js")

    assert js_response.status_code == 200
    assert "DOMContentLoaded" in js_response.text

def test_dashboard_javascript_uses_authenticated_audit_api():
    """Check that the dashboard requests audit data with an API key."""

    dashboard_directory = (
        Path(__file__).resolve().parents[1]
        / "app"
        / "dashboard"
    )

    javascript = (
        dashboard_directory / "script.js"
    ).read_text(encoding="utf-8")

    assert 'fetch("/audit?limit=100"' in javascript
    assert '"X-API-Key": apiKey' in javascript
    assert "event.preventDefault()" in javascript

    # Audit values must be rendered as text, not executable HTML.
    assert "cell.textContent = String(value)" in javascript

    # Credentials must not be saved to browser storage.
    assert "localStorage" not in javascript
    assert "sessionStorage" not in javascript


def test_dashboard_verification_updates_summary_cards():
    """Check that audit verification is connected to dashboard cards."""

    dashboard_directory = (
        Path(__file__).resolve().parents[1]
        / "app"
        / "dashboard"
    )

    javascript = (
        dashboard_directory / "script.js"
    ).read_text(encoding="utf-8")

    # Verification must call the protected backend endpoint.
    assert 'fetch("/audit/verify?limit=100"' in javascript
    assert '"X-API-Key": activeAuditApiKey' in javascript

    # Summary card elements must be declared before they are updated.
    card_ids = {
        "totalRecords": "total-records",
        "validRecords": "valid-records",
        "invalidRecords": "invalid-records",
        "unsignedRecords": "unsigned-records",
    }

    for variable, element_id in card_ids.items():
        declaration = (
            f'const {variable} = '
            f'document.getElementById("{element_id}");'
        )
        update = f"{variable}.textContent = String(data."

        assert declaration in javascript
        assert update in javascript
        assert javascript.index(declaration) < javascript.index(update)

def test_dashboard_contains_agent_activity_charts():
    """Ensure both Agent Activity chart containers exist."""

    dashboard_directory = (
        Path(__file__).resolve().parents[1]
        / "app"
        / "dashboard"
    )

    html = (
        dashboard_directory / "index.html"
    ).read_text(encoding="utf-8")

    assert 'id="activity-heading"' in html
    assert 'id="decision-chart"' in html
    assert 'id="agent-chart"' in html

    assert "Allowed vs. Denied Actions" in html
    assert "Activity by Agent" in html

def test_dashboard_agent_activity_javascript():
    """Check chart rendering and authenticated audit data integration."""

    dashboard_directory = (
        Path(__file__).resolve().parents[1]
        / "app"
        / "dashboard"
    )

    javascript = (
        dashboard_directory / "script.js"
    ).read_text(encoding="utf-8")

    # Both activity calculations must exist.
    assert "function calculateDecisionCounts(events)" in javascript
    assert "function calculateAgentActivity(events)" in javascript

    # Both chart renderers must exist.
    assert "function renderDecisionChart(events)" in javascript
    assert "function renderAgentChart(events)" in javascript

    # Chart values must use safe text rendering.
    assert "label.textContent" in javascript

    # Charts must update after authenticated audit data loads.
    assert "renderDecisionChart(loadedAuditEvents);" in javascript
    assert "renderAgentChart(loadedAuditEvents);" in javascript

    # Clear old chart data before making another request.
    assert "renderDecisionChart([]);" in javascript
    assert "renderAgentChart([]);" in javascript

    # Handle singular and plural event labels.
    assert 'item.count === 1 ? "event" : "events"' in javascript

def test_dashboard_and_audit_security_headers():
    """Ensure dashboard and protected audit responses include security headers."""

    from fastapi.testclient import TestClient
    from backend.app.main import app

    client = TestClient(app)

    for path in ["/dashboard/", "/audit", "/audit/verify"]:
        response = client.get(path)

        assert response.headers["X-Content-Type-Options"] == "nosniff"
        assert response.headers["Referrer-Policy"] == "no-referrer"

        if path.startswith("/audit"):
            assert response.headers["Cache-Control"] == "no-store"

def test_dashboard_security_regressions():
    """Check key frontend security protections remain in place."""

    dashboard_directory = (
        Path(__file__).resolve().parents[1]
        / "app"
        / "dashboard"
    )

    javascript = (
        dashboard_directory / "script.js"
    ).read_text(encoding="utf-8")

    # Do not persist credentials in browser storage.
    assert "localStorage" not in javascript
    assert "sessionStorage" not in javascript

    # Avoid inserting untrusted audit values as HTML.
    unsafe_operations = [
        "innerHTML",
        "outerHTML",
        "insertAdjacentHTML",
        "document.write(",
        "eval(",
    ]

    for operation in unsafe_operations:
        assert operation not in javascript

    assert "cell.textContent = String(value)" in javascript

    # Previous authentication must be invalidated on reload.
    assert "activeAuditApiKey = null;" in javascript

    # Previous verification summaries must be cleared.
    for variable in (
        "totalRecords",
        "validRecords",
        "invalidRecords",
        "unsignedRecords",
    ):
        assert f'{variable}.textContent = "—";' in javascript
