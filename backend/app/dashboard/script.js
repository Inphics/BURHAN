
"use strict";

// BURHAN Security Dashboard
// Phase 4 — Audit history status management

document.addEventListener("DOMContentLoaded", function () {
    const verifyButton = document.getElementById("verify-button");
    const verificationResult = document.getElementById(
        "verification-result"
    );

    const auditHistoryStatus = document.getElementById(
        "audit-history-status"
    );

    const auditRecords = document.getElementById("audit-records");

    console.log("BURHAN dashboard initialized.");

    // Audit verification is not connected yet.
    verifyButton.disabled = true;

    verificationResult.textContent =
        "Dashboard preview only. Audit verification is not connected.";

    // Reset summary values until authenticated data is available.
    document.getElementById("total-records").textContent = "—";
    document.getElementById("valid-records").textContent = "—";
    document.getElementById("invalid-records").textContent = "—";
    document.getElementById("unsigned-records").textContent = "—";

    // Display the current audit history status.
    function setAuditHistoryStatus(status) {
        const messages = {
            disconnected: "Audit history is not connected yet.",
            loading: "Loading audit records...",
            loaded: "Audit records loaded successfully.",
            unauthorized: "Authentication failed.",
            unavailable: "Audit history is temporarily unavailable.",
        };

        auditHistoryStatus.textContent =
            messages[status] || "Audit history status unknown.";

        auditHistoryStatus.dataset.status = status;
    }

    // Keep the table empty until we have authenticated records.
    auditRecords.replaceChildren();

    const emptyRow = document.createElement("tr");
    const emptyCell = document.createElement("td");

    emptyCell.colSpan = 5;
    emptyCell.textContent = "No audit records loaded.";

    emptyRow.appendChild(emptyCell);
    auditRecords.appendChild(emptyRow);

    // Initial state: no audit connection has been established.
    setAuditHistoryStatus("disconnected");
});
