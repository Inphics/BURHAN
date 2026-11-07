
import sqlite3
from pathlib import Path


class AuditDatabase:
    def __init__(self, db_path="burhan_audit.db"):
        self.db_path = Path(db_path)
        self.create_tables()

    def create_tables(self):
        with sqlite3.connect(self.db_path) as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS audit_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    agent TEXT NOT NULL,
                    action TEXT NOT NULL,
                    allowed INTEGER NOT NULL,
                    reason TEXT NOT NULL
                )
                """
            )
    
    def save_event(self, timestamp, agent, action, allowed, reason):
        with sqlite3.connect(self.db_path) as connection:
            connection.execute(
                """
                INSERT INTO audit_events (
                    timestamp,
                    agent,
                    action,
                    allowed,
                    reason
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (timestamp, agent, action, int(allowed), reason),
            )
    
    def get_events(self):
        with sqlite3.connect(self.db_path) as connection:
            connection.row_factory = sqlite3.Row

            cursor = connection.execute(
                """
                SELECT
                    id,
                    timestamp,
                    agent,
                    action,
                    allowed,
                    reason
                FROM audit_events
                ORDER BY id DESC
                """
            )

            return [
                {
                    "id": row["id"],
                    "timestamp": row["timestamp"],
                    "agent": row["agent"],
                    "action": row["action"],
                    "allowed": bool(row["allowed"]),
                    "reason": row["reason"],
                }
                for row in cursor.fetchall()
            ]
