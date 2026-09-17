from database import init_db
import json

def seed_data():
    init_db()

    import sqlite3
    from database import DB_FILE

    try:
        with open("tickets.json", "r", encoding="utf-8") as file:
            existing_tickets = json.load(file)
    except FileNotFoundError:
        print("Error: tickets.json not found. Please create the file first.")
        return

    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        for t in existing_tickets:
            cursor.execute(
                "INSERT OR REPLACE INTO tickets (ticket_id, employee, email, issue, category, action, policy_id, status, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (t["id"], t["employee"], t["email"], t["issue"], t["category"], t["action"], t["policy"], t["status"], "2026-01-01T00:00:00")
            )
        conn.commit()
    print(f"✅ Successfully seeded {len(existing_tickets)} historical tickets from tickets.json into the database.")

if __name__ == "__main__":
    seed_data()
