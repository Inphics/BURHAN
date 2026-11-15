
import hashlib
import json
import hmac


class AuditIntegrity:
    """Calculate deterministic SHA-256 fingerprints for audit data."""

    @staticmethod
    def calculate_hash(event_data: dict) -> str:
        serialized_data = json.dumps(
            event_data,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        )

        return hashlib.sha256(
            serialized_data.encode("utf-8")
        ).hexdigest()


    @staticmethod
    def calculate_hmac(event_data: dict, secret_key: str) -> str:
        """Calculate a keyed HMAC-SHA256 signature for audit data."""
        if not secret_key:
            raise ValueError("An audit integrity secret key is required.")

        serialized_data = json.dumps(
            event_data,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        )

        return hmac.new(
            secret_key.encode("utf-8"),
            serialized_data.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()


    @staticmethod
    def verify_hmac(
        event_data: dict,
        secret_key: str,
        expected_hmac: str,
    ) -> bool:
        """Verify an audit event's HMAC-SHA256 signature."""

        calculated_hmac = AuditIntegrity.calculate_hmac(
            event_data,
            secret_key,
        )

        return hmac.compare_digest(
            calculated_hmac,
            expected_hmac,
        )


    @staticmethod
    def verify_record(record: dict, secret_key: str) -> bool:
        """Verify the HMAC signature of a stored audit record."""

        expected_hmac = record.get("event_hmac")

        if not expected_hmac:
            return False

        event_data = {
            "timestamp": record["timestamp"],
            "agent": record["agent"],
            "action": record["action"],
            "allowed": record["allowed"],
            "reason": record["reason"],
            "execution_status": record["execution_status"],
            "request_id": record["request_id"],
        }

        return AuditIntegrity.verify_hmac(
            event_data,
            secret_key,
            expected_hmac,
        )


    @staticmethod
    def verify_records(records: list[dict], secret_key: str) -> dict:
        """Verify a collection of stored audit records."""

        if not secret_key:
            raise ValueError("An audit integrity secret key is required.")

        results = []

        for record in records:
            if not record.get("event_hmac"):
                status = "unsigned"
            elif AuditIntegrity.verify_record(record, secret_key):
                status = "valid"
            else:
                status = "invalid"

            results.append(
                {
                    "id": record["id"],
                    "request_id": record["request_id"],
                    "status": status,
                }
            )

        return {
            "total": len(results),
            "valid": sum(
                result["status"] == "valid"
                for result in results
            ),
            "invalid": sum(
                result["status"] == "invalid"
                for result in results
            ),
            "unsigned": sum(
                result["status"] == "unsigned"
                for result in results
            ),
            "results": results,
        }
