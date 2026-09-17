# database.py

import sqlite3
from datetime import datetime
import json

# ============================================================
# DATABASE CONFIGURATION
# ============================================================

DATABASE_NAME = "veridian_it.db"

# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_connection():
    """
    Create and return a connection to the SQLite database.
    """
    connection = sqlite3.connect(
        DATABASE_NAME,
        check_same_thread=False
    )
    connection.row_factory = sqlite3.Row
    return connection

# ============================================================
# INITIALIZE DATABASE
# ============================================================

def initialize_database():
    """
    Create the required database tables if they don't exist.
    """
    connection = get_connection()
    cursor = connection.cursor()

    # Tickets table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS tickets (
            ticket_id TEXT PRIMARY KEY,
            employee TEXT NOT NULL,
            email TEXT NOT NULL,
            issue TEXT NOT NULL,
            category TEXT,
            action TEXT,
            policy_id TEXT,
            status TEXT,
            created_at TEXT
        )
        """
    )

    # Audit logs table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            action TEXT,
            details TEXT
        )
        """
    )

    # Settings table for admin password
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)
    connection.commit()
    connection.close()

# ============================================================
# GENERATE TICKET ID
# ============================================================

def generate_ticket_id():
    """
    Generate a new ticket ID.
    """
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT COUNT(*) AS total FROM tickets")
    result = cursor.fetchone()
    total_tickets = result["total"]
    connection.close()
    next_number = total_tickets + 1
    return f"AUTO-{next_number:03d}"

# ============================================================
# CREATE TICKET
# ============================================================

def create_ticket(employee, email, issue, category, action, policy_id, status):
    """
    Create a structured IT support ticket.
    """
    initialize_database()
    ticket_id = generate_ticket_id()
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(
        """
        INSERT INTO tickets (ticket_id, employee, email, issue, category, action, policy_id, status, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (ticket_id, employee, email, issue, category, action, policy_id, status, created_at)
    )
    connection.commit()
    connection.close()

    return {
        "ticket_id": ticket_id,
        "employee": employee,
        "email": email,
        "issue": issue,
        "category": category,
        "action": action,
        "policy_id": policy_id,
        "status": status,
        "created_at": created_at
    }

# ============================================================
# GET ALL TICKETS
# ============================================================

def get_all_tickets():
    """
    Return all tickets.
    """
    initialize_database()
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM tickets ORDER BY created_at DESC")
    rows = cursor.fetchall()
    connection.close()
    return [dict(row) for row in rows]

# ============================================================
# GET TICKET BY ID
# ============================================================

def get_ticket(ticket_id):
    """
    Retrieve a single ticket by ticket ID.
    """
    initialize_database()
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM tickets WHERE ticket_id = ?", (ticket_id,))
    row = cursor.fetchone()
    connection.close()
    return dict(row) if row else None

# ============================================================
# UPDATE TICKET STATUS
# ============================================================

def update_ticket_status(ticket_id, new_status):
    """
    Update the status of an existing ticket.
    """
    initialize_database()
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("UPDATE tickets SET status = ? WHERE ticket_id = ?", (new_status, ticket_id))
    connection.commit()
    updated = cursor.rowcount > 0
    connection.close()
    return updated

# ============================================================
# ADD AUDIT LOG
# ============================================================

def add_audit_log(action, details):
    """
    Record an agent action in the audit trail.
    """
    initialize_database()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if isinstance(details, dict):
        details = json.dumps(details, indent=2, default=str)

    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(
        "INSERT INTO audit_logs (timestamp, action, details) VALUES (?, ?, ?)",
        (timestamp, action, details)
    )
    connection.commit()
    connection.close()

# ============================================================
# GET AUDIT LOGS
# ============================================================

def get_audit_logs():
    """
    Retrieve all audit logs from the database.
    """
    initialize_database()
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM audit_logs ORDER BY id DESC")
    rows = cursor.fetchall()
    connection.close()

    logs = []
    for row in rows:
        log = dict(row)
        try:
            log["details"] = json.loads(log["details"])
        except (json.JSONDecodeError, TypeError):
            pass
        logs.append(log)
    return logs

# ============================================================
# ADMIN SETTINGS
# ============================================================

def set_setting(key, value):
    initialize_database()
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, value))
    connection.commit()
    connection.close()

def get_setting(key):
    initialize_database()
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
    row = cursor.fetchone()
    connection.close()
    return row[0] if row else None
