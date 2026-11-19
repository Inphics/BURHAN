
from backend.app.evaluation.audit_integrity import AuditIntegrity


def test_same_audit_data_produces_same_hash():
    event = {
        "agent": "research_agent",
        "action": "read",
        "allowed": True,
        "execution_status": "simulated",
    }

    first_hash = AuditIntegrity.calculate_hash(event)
    second_hash = AuditIntegrity.calculate_hash(event)

    assert first_hash == second_hash
    assert len(first_hash) == 64


def test_modified_audit_data_produces_different_hash():
    original_event = {
        "agent": "research_agent",
        "action": "read",
        "allowed": True,
        "execution_status": "simulated",
    }

    modified_event = {
        "agent": "research_agent",
        "action": "delete",
        "allowed": True,
        "execution_status": "simulated",
    }

    original_hash = AuditIntegrity.calculate_hash(original_event)
    modified_hash = AuditIntegrity.calculate_hash(modified_event)

    assert original_hash != modified_hash


def test_dictionary_key_order_does_not_change_hash():
    first_event = {
        "agent": "research_agent",
        "action": "read",
    }

    second_event = {
        "action": "read",
        "agent": "research_agent",
    }

    assert (
        AuditIntegrity.calculate_hash(first_event)
        == AuditIntegrity.calculate_hash(second_event)
    )


def test_same_data_and_secret_produce_same_hmac():
    event = {
        "agent": "research_agent",
        "action": "read",
        "allowed": True,
    }

    secret = "test-secret-key"

    first_hmac = AuditIntegrity.calculate_hmac(event, secret)
    second_hmac = AuditIntegrity.calculate_hmac(event, secret)

    assert first_hmac == second_hmac
    assert len(first_hmac) == 64


def test_modified_data_produces_different_hmac():
    original_event = {
        "agent": "research_agent",
        "action": "read",
    }

    modified_event = {
        "agent": "research_agent",
        "action": "delete",
    }

    secret = "test-secret-key"

    original_hmac = AuditIntegrity.calculate_hmac(
        original_event, secret
    )
    modified_hmac = AuditIntegrity.calculate_hmac(
        modified_event, secret
    )

    assert original_hmac != modified_hmac


def test_different_secret_produces_different_hmac():
    event = {
        "agent": "research_agent",
        "action": "read",
    }

    first_hmac = AuditIntegrity.calculate_hmac(
        event, "first-test-secret"
    )
    second_hmac = AuditIntegrity.calculate_hmac(
        event, "second-test-secret"
    )

    assert first_hmac != second_hmac


def test_verify_hmac_accepts_valid_signature():
    event = {
        "agent": "research_agent",
        "action": "read",
        "allowed": True,
    }

    secret = "test-secret-key"

    signature = AuditIntegrity.calculate_hmac(event, secret)

    assert AuditIntegrity.verify_hmac(
        event, secret, signature
    ) is True


def test_verify_hmac_rejects_tampered_event():
    event = {
        "agent": "research_agent",
        "action": "read",
        "allowed": True,
    }

    secret = "test-secret-key"

    signature = AuditIntegrity.calculate_hmac(event, secret)

    # Simulate someone changing the audit event.
    event["action"] = "delete"

    assert AuditIntegrity.verify_hmac(
        event, secret, signature
    ) is False


def test_verify_hmac_rejects_wrong_secret():
    event = {
        "agent": "research_agent",
        "action": "read",
        "allowed": True,
    }

    signature = AuditIntegrity.calculate_hmac(
        event, "correct-test-secret"
    )

    assert AuditIntegrity.verify_hmac(
        event, "wrong-test-secret", signature
    ) is False


def test_verify_record_accepts_valid_signed_record():
    secret = "test-only-secret"

    record = {
        "timestamp": "2026-11-15T12:00:00+00:00",
        "agent": "research_agent",
        "action": "read",
        "allowed": True,
        "reason": "Action permitted.",
        "execution_status": "simulated",
        "request_id": "test-request-123",
    }

    record["event_hmac"] = AuditIntegrity.calculate_hmac(
        record,
        secret,
    )

    assert AuditIntegrity.verify_record(record, secret) is True


def test_verify_record_rejects_tampered_record():
    secret = "test-only-secret"

    record = {
        "timestamp": "2026-11-15T12:00:00+00:00",
        "agent": "research_agent",
        "action": "read",
        "allowed": True,
        "reason": "Action permitted.",
        "execution_status": "simulated",
        "request_id": "test-request-123",
    }

    record["event_hmac"] = AuditIntegrity.calculate_hmac(
        record,
        secret,
    )

    # Change the action after the signature was created.
    record["action"] = "delete"

    assert AuditIntegrity.verify_record(record, secret) is False


def test_verify_record_rejects_unsigned_record():
    record = {
        "timestamp": "2026-11-15T12:00:00+00:00",
        "agent": "research_agent",
        "action": "read",
        "allowed": True,
        "reason": "Action permitted.",
        "execution_status": "simulated",
        "request_id": "test-request-123",
        "event_hmac": None,
    }

    assert AuditIntegrity.verify_record(
        record,
        "test-only-secret",
    ) is False


def test_verify_record_rejects_malformed_hmac():
    from backend.app.evaluation.audit_integrity import AuditIntegrity

    record = {
        "timestamp": "2026-11-19T12:00:00+00:00",
        "agent": "research_agent",
        "action": "read",
        "allowed": True,
        "reason": "Action permitted.",
        "execution_status": "simulated",
        "request_id": "malformed-hmac-test",
        "event_hmac": "this-is-not-a-valid-hmac",
    }

    result = AuditIntegrity.verify_record(
        record,
        "test-only-hmac-secret",
    )

    assert result is False


def test_verify_record_rejects_signature_from_wrong_secret():
    from backend.app.evaluation.audit_integrity import AuditIntegrity

    record = {
        "timestamp": "2026-11-19T12:00:00+00:00",
        "agent": "research_agent",
        "action": "read",
        "allowed": True,
        "reason": "Action permitted.",
        "execution_status": "simulated",
        "request_id": "wrong-secret-test",
    }

    # Sign the record with a different secret key.
    record["event_hmac"] = AuditIntegrity.calculate_hmac(
        record,
        "incorrect-test-secret",
    )

    # Attempt verification using the correct secret.
    result = AuditIntegrity.verify_record(
        record,
        "correct-test-secret",
    )

    assert result is False


def test_verify_record_rejects_non_string_hmac():
    from backend.app.evaluation.audit_integrity import AuditIntegrity

    record = {
        "timestamp": "2026-11-19T12:00:00+00:00",
        "agent": "research_agent",
        "action": "read",
        "allowed": True,
        "reason": "Action permitted.",
        "execution_status": "simulated",
        "request_id": "invalid-type-test",
        "event_hmac": 12345,
    }

    result = AuditIntegrity.verify_record(
        record,
        "test-only-hmac-secret",
    )

    assert result is False


def test_verify_records_classifies_malformed_hmac_as_invalid():
    from backend.app.evaluation.audit_integrity import AuditIntegrity

    record = {
        "id": 1,
        "timestamp": "2026-11-19T12:00:00+00:00",
        "agent": "research_agent",
        "action": "read",
        "allowed": True,
        "reason": "Action permitted.",
        "execution_status": "simulated",
        "request_id": "malformed-batch-test",
        "event_hmac": 12345,
    }

    result = AuditIntegrity.verify_records(
        [record],
        "test-only-hmac-secret",
    )

    assert result["total"] == 1
    assert result["valid"] == 0
    assert result["invalid"] == 1
    assert result["unsigned"] == 0

    assert result["results"][0]["status"] == "invalid"
