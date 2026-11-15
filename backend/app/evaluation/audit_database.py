
import sqlite3
import os
from pathlib import Path


class AuditDatabase:
    def __init__(self, db_path=None):
        if db_path is None:
            db_path = os.getenv(
                "BURHAN_AUDIT_DB_PATH",
                "burhan_audit.db",
            )

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

            # Add execution outcome tracking to existing databases.
            columns = connection.execute(
                "PRAGMA table_info(audit_events)"
            ).fetchall()

            column_names = {column[1] for column in columns}

            if "execution_status" not in column_names:
                connection.execute(
                    """
                    ALTER TABLE audit_events
                    ADD COLUMN execution_status TEXT
                    NOT NULL DEFAULT 'not_attempted'
                    """
                )

    
    
    def save_event(
        self,
        timestamp,
        agent,
        action,
        allowed,
        reason,
        execution_status="not_attempted",
    ):
        with sqlite3.connect(self.db_path) as connection:
            connection.execute(
                """
                INSERT INTO audit_events (
                    timestamp,
                    agent,
                    action,
                    allowed,
                    reason,
                    execution_status
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    timestamp,
                    agent,
                    action,
                    int(allowed),
                    reason,
                    execution_status,
                ),
            )

     
    
    def get_events(self, limit=100):
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
                    reason,
                    execution_status
                FROM audit_events
                ORDER BY id DESC
                LIMIT ?
                """,
                (limit,),
            )

            return [
                {
                    "id": row["id"],
                    "timestamp": row["timestamp"],
                    "agent": row["agent"],
                    "action": row["action"],
                    "allowed": bool(row["allowed"]),
                    "reason": row["reason"],
                    "execution_status": row["execution_status"],
                }
                for row in cursor.fetchall()
            ]

