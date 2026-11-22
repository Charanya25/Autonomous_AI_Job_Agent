
import sqlite3
from database.db_manager import DB_PATH

connection = sqlite3.connect(DB_PATH)

print("DATABASE RECORD SUMMARY")
print("=" * 40)

tables = [
    "applications",
    "hr_contacts",
    "daily_stats",
    "drip_outreach",
    "company_sources"
]

for table in tables:
    count = connection.execute(
        f"SELECT COUNT(*) FROM {table}"
    ).fetchone()[0]

    print(f"{table}: {count}")

print("\nJOB STATUS SUMMARY")
print("=" * 40)

statuses = connection.execute("""
    SELECT status, COUNT(*)
    FROM applications
    GROUP BY status
    ORDER BY status
""").fetchall()

for status, count in statuses:
    print(f"{status}: {count}")

connection.close()
