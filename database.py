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

    # --------------------------------------------------------
    # Tickets table
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Audit logs table
    # --------------------------------------------------------

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

    connection.commit()

    connection.close()


# ============================================================
# GENERATE TICKET ID
# ============================================================

def generate_ticket_id():
    """
    Generate a new ticket ID.

    Example:
    AUTO-001
    AUTO-002
    AUTO-003
    """

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT COUNT(*) AS total
        FROM tickets
        """
    )

    result = cursor.fetchone()

    total_tickets = result["total"]

    connection.close()

    next_number = total_tickets + 1

    return f"AUTO-{next_number:03d}"


# ============================================================
# CREATE TICKET
# ============================================================

def create_ticket(
    employee,
    email,
    issue,
    category,
    action,
    policy_id,
    status
):
    """
    Create a structured IT support ticket.

    Returns the created ticket as a dictionary.
    """

    initialize_database()

    ticket_id = generate_ticket_id()

    created_at = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO tickets (
            ticket_id,
            employee,
            email,
            issue,
            category,
            action,
            policy_id,
            status,
            created_at
        )

        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            ticket_id,
            employee,
            email,
            issue,
            category,
            action,
            policy_id,
            status,
            created_at
        )
    )

    connection.commit()

    connection.close()

    ticket = {
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

    return ticket


# ============================================================
# GET ALL TICKETS
# ============================================================

def get_all_tickets():
    """
    Return all automatically generated tickets.
    """

    initialize_database()

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT *
        FROM tickets
        ORDER BY created_at DESC
        """
    )

    rows = cursor.fetchall()

    connection.close()

    tickets = []

    for row in rows:

        tickets.append(
            dict(row)
        )

    return tickets


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

    cursor.execute(
        """
        SELECT *
        FROM tickets
        WHERE ticket_id = ?
        """,
        (ticket_id,)
    )

    row = cursor.fetchone()

    connection.close()

    if row:

        return dict(row)

    return None


# ============================================================
# UPDATE TICKET STATUS
# ============================================================

def update_ticket_status(
    ticket_id,
    new_status
):
    """
    Update the status of an existing ticket.
    """

    initialize_database()

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE tickets

        SET status = ?

        WHERE ticket_id = ?
        """,
        (
            new_status,
            ticket_id
        )
    )

    connection.commit()

    updated = cursor.rowcount > 0

    connection.close()

    return updated


# ============================================================
# ADD AUDIT LOG
# ============================================================

def add_audit_log(
    action,
    details
):
    """
    Record an agent action in the audit trail.

    Details can be provided as a dictionary.
    """

    initialize_database()

    timestamp = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    # Convert dictionary to JSON
    if isinstance(details, dict):

        details = json.dumps(
            details,
            indent=2,
            default=str
        )

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO audit_logs (
            timestamp,
            action,
            details
        )

        VALUES (?, ?, ?)
        """,
        (
            timestamp,
            action,
            details
        )
    )

    connection.commit()

    connection.close()


# ============================================================
# GET AUDIT LOGS
# ============================================================

def get_audit_logs():
    """
    Return all audit trail records.
    """

    initialize_database()

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT *
        FROM audit_logs
        ORDER BY timestamp DESC
        """
    )

    rows = cursor.fetchall()

    connection.close()

    logs = []

    for row in rows:

        log = dict(row)

        # Try converting JSON details back to dictionary
        try:

            log["details"] = json.loads(
                log["details"]
            )

        except Exception:

            pass

        logs.append(log)

    return logs


# ============================================================
# GET TICKET STATISTICS
# ============================================================

def get_ticket_statistics():
    """
    Return basic ticket statistics.

    Useful for a future dashboard/analytics section.
    """

    initialize_database()

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT status, COUNT(*) AS count
        FROM tickets
        GROUP BY status
        """
    )

    rows = cursor.fetchall()

    connection.close()

    statistics = {}

    for row in rows:

        statistics[
            row["status"]
        ] = row["count"]

    return statistics


# ============================================================
# CLEAR DATABASE
# ============================================================

def clear_database():
    """
    Delete generated tickets and audit logs.

    Useful during testing/demo preparation.
    """

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        "DELETE FROM tickets"
    )

    cursor.execute(
        "DELETE FROM audit_logs"
    )

    connection.commit()

    connection.close()


# ============================================================
# TEST DATABASE
# ============================================================

if __name__ == "__main__":

    print(
        "\n================================"
    )

    print(
        "VERIDIAN DATABASE TEST"
    )

    print(
        "================================\n"
    )

    # Initialize
    initialize_database()

    print(
        "✓ Database initialized"
    )

    # Create test ticket
    test_ticket = create_ticket(
        employee="Test Employee",
        email="test@veridian-corp.example",
        issue="My account is locked.",
        category="Account Access",
        action="Manual account unlock",
        policy_id="KB-01",
        status="Escalated"
    )

    print(
        "\n✓ Ticket created:"
    )

    print(
        json.dumps(
            test_ticket,
            indent=2
        )
    )

    # Add audit event
    add_audit_log(
        action="Manual account unlock",
        details={
            "employee": "Test Employee",
            "ticket_id": test_ticket["ticket_id"],
            "policy": "KB-01",
            "status": "Escalated"
        }
    )

    print(
        "\n✓ Audit log added"
    )

    # Display tickets
    print(
        "\nAll tickets:"
    )

    print(
        json.dumps(
            get_all_tickets(),
            indent=2
        )
    )

    # Display audit logs
    print(
        "\nAudit logs:"
    )

    print(
        json.dumps(
            get_audit_logs(),
            indent=2
        )
    )

    print(
        "\n✓ Database test completed"
    )