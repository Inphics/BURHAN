
"use strict";

// BURHAN Security Dashboard
// Phase 4 — Audit history authentication interface

document.addEventListener("DOMContentLoaded", function () {
    const verifyButton = document.getElementById("verify-button");
    const verificationResult = document.getElementById(
        "verification-result"
    );

    const auditHistoryStatus = document.getElementById(
        "audit-history-status"
    );

    const auditRecords = document.getElementById("audit-records");

    const auditAccessForm = document.getElementById(
        "audit-access-form"
    );

    const auditApiKeyInput = document.getElementById(
        "audit-api-key"
    );

    const totalRecords = document.getElementById("total-records");
    const validRecords = document.getElementById("valid-records");
    const invalidRecords = document.getElementById("invalid-records");
    const unsignedRecords = document.getElementById("unsigned-records");

    console.log("BURHAN dashboard initialized.");

    // Keep the audit API key temporarily in memory.
    // Do not persist credentials in browser storage.
    let activeAuditApiKey = null;

    // Keep the most recently loaded audit records for activity charts.
    let loadedAuditEvents = [];

    // Calculate policy decisions from the loaded audit records.
    function calculateDecisionCounts(events) {
        let allowed = 0;
        let denied = 0;

        events.forEach(function (event) {
            if (event.allowed === true) {
                allowed += 1;
            } else if (event.allowed === false) {
                denied += 1;
            }
        });

        return {
            allowed: allowed,
            denied: denied,
            total: allowed + denied,
        };
    }

    /**
     * Count audit events for each agent.
     * These are event counts, not unique requests.
     */
    function calculateAgentActivity(events) {
        const counts = new Map();

        events.forEach(function (event) {
            const agent = (
                typeof event.agent === "string" &&
                event.agent.trim()
            )
                ? event.agent
                : "Unknown agent";

            counts.set(agent, (counts.get(agent) || 0) + 1);
        });

        return Array.from(counts.entries())
            .map(function ([agent, count]) {
                return {
                    agent: agent,
                    count: count,
                };
            })
            .sort(function (a, b) {
                return b.count - a.count ||
                    a.agent.localeCompare(b.agent);
            });
    }

    /**
     * Display a horizontal bar chart of audit activity by agent.
     * Counts represent audit events, not unique requests.
     */
    function renderAgentChart(events) {
        const chart = document.getElementById("agent-chart");

        if (!chart) {
            return;
        }

        const agents = calculateAgentActivity(events);
        chart.replaceChildren();

        if (agents.length === 0) {
            const message = document.createElement("p");
            message.textContent = "No agent activity available.";
            chart.appendChild(message);
            return;
        }

        const highestCount = agents[0].count;

        agents.forEach(function (item) {
            const percentage = (item.count / highestCount) * 100;

            const row = document.createElement("div");
            row.className = "activity-bar-row";

            const label = document.createElement("p");
            label.textContent = `${item.agent}: ${item.count} ${item.count === 1 ? "event" : "events"}`;

            const track = document.createElement("div");
            track.className = "activity-bar-track";

            const bar = document.createElement("div");
            bar.className = "activity-bar";
            bar.style.width = `${percentage}%`;

            track.appendChild(bar);
            row.appendChild(label);
            row.appendChild(track);
            chart.appendChild(row);
        });
    }

    /**
     * Display an accessible, text-based decision chart.
     * Counts represent audit events, not unique requests.
     */
    function renderDecisionChart(events) {
        const chart = document.getElementById("decision-chart");
        if (!chart) {
            return;
        }

        const counts = calculateDecisionCounts(events);
        chart.replaceChildren();

        if (counts.total === 0) {
            const message = document.createElement("p");
            message.textContent = "No decision activity available.";
            chart.appendChild(message);
            return;
        }

        const categories = [
            { label: "Allowed", count: counts.allowed },
            { label: "Denied", count: counts.denied },
        ];

        categories.forEach(function (category) {
            const percentage = (category.count / counts.total) * 100;

            const row = document.createElement("div");
            row.className = "activity-bar-row";

            const label = document.createElement("p");
            label.textContent =
                `${category.label}: ${category.count} (${percentage.toFixed(1)}%)`;

            const track = document.createElement("div");
            track.className = "activity-bar-track";

            const bar = document.createElement("div");
            bar.className = "activity-bar";
            bar.style.width = `${percentage}%`;

            if (category.label === "Denied") {
                bar.classList.add("activity-bar-denied");
            }

            track.appendChild(bar);
            row.appendChild(label);
            row.appendChild(track);
            chart.appendChild(row);
        });
    }

    // Verification API integration is being prepared.
    verifyButton.disabled = false;

    verificationResult.textContent =
        "Verification is not connected yet.";

    // Request audit integrity verification from the backend.
    verifyButton.addEventListener("click", async function () {
        if (!activeAuditApiKey) {
            verificationResult.textContent =
                "Load audit records with your API key before verifying.";
            return;
        }

        verifyButton.disabled = true;
        verificationResult.textContent = "Verifying audit integrity...";

        try {
            const response = await fetch("/audit/verify?limit=100", {
                method: "GET",
                headers: {
                    "X-API-Key": activeAuditApiKey,
                },
                cache: "no-store",
            });

            if (response.status === 401) {
                activeAuditApiKey = null;
                verificationResult.textContent =
                    "Authentication failed. Load audit records again.";
                return;
            }

            if (response.status === 403) {
                verificationResult.textContent =
                    "Audit verification is disabled or not configured on the server.";
                return;
            }

            if (response.status === 429) {
                verificationResult.textContent =
                    "Too many requests. Please try again later.";
                return;
            }

            if (!response.ok) {
                verificationResult.textContent =
                    "Audit verification is temporarily unavailable.";
                return;
            }

            const data = await response.json();

            if (
                !data ||
                !Number.isInteger(data.total) ||
                !Number.isInteger(data.valid) ||
                !Number.isInteger(data.invalid) ||
                !Number.isInteger(data.unsigned)
            ) {
                verificationResult.textContent =
                    "Invalid verification response from the server.";
                return;
            }

            totalRecords.textContent = String(data.total);
            validRecords.textContent = String(data.valid);
            invalidRecords.textContent = String(data.invalid);
            unsignedRecords.textContent = String(data.unsigned);

            verificationResult.textContent =
                `Verification complete: ${data.valid} valid, ` +
                `${data.invalid} invalid, ` +
                `${data.unsigned} unsigned records.`;

        } catch (error) {
            verificationResult.textContent =
                "Unable to connect to the audit verification API.";
        } finally {
            verifyButton.disabled = false;
        }
    });

    // No authenticated audit data has been loaded.
    document.getElementById("total-records").textContent = "—";
    document.getElementById("valid-records").textContent = "—";
    document.getElementById("invalid-records").textContent = "—";
    document.getElementById("unsigned-records").textContent = "—";

    function setAuditHistoryStatus(status) {
        const messages = {
            disconnected: "Audit history is not connected yet.",
            loading: "Loading audit records...",
            loaded: "Audit records loaded successfully.",
            unauthorized: "Authentication failed.",
            unavailable: "Audit history is temporarily unavailable.",
            not_connected: "Audit API connection is not implemented yet.",
        };

        auditHistoryStatus.textContent =
            messages[status] || "Audit history status unknown.";

        auditHistoryStatus.dataset.status = status;
    }

    function showEmptyAuditTable() {
        auditRecords.replaceChildren();

        const emptyRow = document.createElement("tr");
        const emptyCell = document.createElement("td");

        emptyCell.colSpan = 5;
        emptyCell.textContent = "No audit records loaded.";

        emptyRow.appendChild(emptyCell);
        auditRecords.appendChild(emptyRow);
    }

    function displayAuditRecords(events) {
        auditRecords.replaceChildren();

        if (events.length === 0) {
            const row = document.createElement("tr");
            const cell = document.createElement("td");

            cell.colSpan = 5;
            cell.textContent = "No audit records found.";

            row.appendChild(cell);
            auditRecords.appendChild(row);
            return;
        }

        events.forEach(function (event) {
            const row = document.createElement("tr");

            const values = [
                event.request_id ?? "—",
                event.agent ?? "—",
                event.action ?? "—",
                event.allowed ? "Allowed" : "Denied",
                event.execution_status ?? "—",
            ];

            values.forEach(function (value) {
                const cell = document.createElement("td");
                cell.textContent = String(value);
                row.appendChild(cell);
            });

            auditRecords.appendChild(row);
        });
    }

    // Initial dashboard state.
    showEmptyAuditTable();
    setAuditHistoryStatus("disconnected");

    // Intercept the form before any browser submission occurs.
    auditAccessForm.addEventListener("submit", async function (event) {
        event.preventDefault();

        const apiKey = auditApiKeyInput.value;
        auditApiKeyInput.value = "";

        // Invalidate previously authenticated access when a new request begins.
        activeAuditApiKey = null;

        // Clear previous records before requesting new data.
        showEmptyAuditTable();
        loadedAuditEvents = [];
        renderDecisionChart([]);
        renderAgentChart([]);

        // Clear verification results from the previous audit session.
        totalRecords.textContent = "—";
        validRecords.textContent = "—";
        invalidRecords.textContent = "—";
        unsignedRecords.textContent = "—";

        verificationResult.textContent =
            "Load audit records, then verify their integrity.";

        if (!apiKey.trim()) {
            setAuditHistoryStatus("unauthorized");
            return;
        }

        setAuditHistoryStatus("loading");

        try {
            const response = await fetch("/audit?limit=100", {
                method: "GET",
                headers: {
                    "X-API-Key": apiKey,
                },
                cache: "no-store",
            });

            if (response.status === 401) {
                setAuditHistoryStatus("unauthorized");
                return;
            }

            if (!response.ok) {
                setAuditHistoryStatus("unavailable");
                return;
            }

            const data = await response.json();

            if (!data || !Array.isArray(data.events)) {
                setAuditHistoryStatus("unavailable");
                return;
            }

            // Retain the key only after a successful authenticated response.
            activeAuditApiKey = apiKey;

            // Store authenticated audit records for activity visualizations.
            loadedAuditEvents = data.events;

            displayAuditRecords(loadedAuditEvents);
            renderDecisionChart(loadedAuditEvents);
            renderAgentChart(loadedAuditEvents);
            setAuditHistoryStatus("loaded");

        } catch (error) {
            setAuditHistoryStatus("unavailable");
        }
    });
});
