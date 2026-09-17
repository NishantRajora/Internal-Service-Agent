from database import initialize_database, DATABASE_NAME
import json
import sqlite3

def seed_data():
    print("Initializing database...")
    initialize_database()

    try:
        with open("tickets.json", "r", encoding="utf-8") as file:
            existing_tickets = json.load(file)
    except FileNotFoundError:
        print("Error: tickets.json not found. Please create the file first.")
        return
    except json.JSONDecodeError:
        print("Error: tickets.json contains invalid JSON.")
        return

    print(f"Loading {len(existing_tickets)} historical tickets...")

    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        for t in existing_tickets:
            cursor.execute(
                "INSERT OR REPLACE INTO tickets (ticket_id, employee, email, issue, category, action, policy_id, status, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (t["id"], t["employee"], t["email"], t["issue"], t["category"], t["action"], t["policy"], t["status"], "2026-01-01T00:00:00")
            )
        conn.commit()

    print(f"✅ Successfully seeded {len(existing_tickets)} historical tickets into the database.")

if __name__ == "__main__":
    seed_data()
