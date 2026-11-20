
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

    console.log("BURHAN dashboard initialized.");

    // Verification is not connected yet.
    verifyButton.disabled = true;

    verificationResult.textContent =
        "Dashboard preview only. Audit verification is not connected.";

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

        // Clear previous records before requesting new data.
        showEmptyAuditTable();

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

            displayAuditRecords(data.events);
            setAuditHistoryStatus("loaded");

        } catch (error) {
            setAuditHistoryStatus("unavailable");
        }
    });
});
