import sqlite3
import json
from datetime import datetime

DB_FILE = "veridian_it.db"

def init_db():
    """Initialize the SQLite database for tickets and audit logs."""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()

        # Tickets table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tickets (
                ticket_id TEXT PRIMARY KEY,
                employee TEXT,
                email TEXT,
                issue TEXT,
                category TEXT,
                action TEXT,
                policy_id TEXT,
                status TEXT,
                created_at TEXT
            )
        """)

        # Audit logs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                action TEXT,
                details TEXT
            )
        """)

        # Settings table for admin password
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        """)
        conn.commit()

def create_ticket(employee, email, issue, category, action, policy_id, status):
    """Create a new IT support ticket."""
    ticket_id = f"AUTO-{datetime.now().strftime('%S%f')[:4]}" # Simple unique ID
    created_at = datetime.now().isoformat()

    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO tickets VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (ticket_id, employee, email, issue, category, action, policy_id, status, created_at)
        )
        conn.commit()

    return {
        "ticket_id": ticket_id,
        "employee": employee,
        "category": category,
        "status": status,
        "action": action,
        "policy_id": policy_id
    }

def get_all_tickets():
    """Retrieve all tickets from the database."""
    with sqlite3.connect(DB_FILE) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tickets ORDER BY created_at DESC")
        return [dict(row) for row in cursor.fetchall()]

def add_audit_log(action, details):
    """Add an entry to the audit trail."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    details_json = json.dumps(details)

    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO audit_logs (timestamp, action, details) VALUES (?, ?, ?)",
            (timestamp, action, details_json)
        )
        conn.commit()

def get_audit_logs():
    """Retrieve all audit logs from the database."""
    with sqlite3.connect(DB_FILE) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM audit_logs ORDER BY id DESC")
        logs = []
        for row in cursor.fetchall():
            log = dict(row)
            log["details"] = json.loads(log["details"])
            logs.append(log)
        return logs

# ============================================================
# ADMIN SETTINGS
# ============================================================

def set_setting(key, value):
    """Set a configuration value in the settings table."""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
            (key, value)
        )
        conn.commit()

def get_setting(key):
    """Get a configuration value from the settings table."""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
        row = cursor.fetchone()
        return row[0] if row else None

# Initialize the database when the module is imported
init_db()
