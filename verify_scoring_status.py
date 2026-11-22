
import sqlite3

connection = sqlite3.connect("database/job_agent.db")

print("\nSCORING STATUS SUMMARY")
print("=" * 40)

results = connection.execute("""
    SELECT scoring_status, COUNT(*)
    FROM applications
    GROUP BY scoring_status
""").fetchall()

for status, count in results:
    print(f"{status}: {count}")

pending = connection.execute("""
    SELECT COUNT(*)
    FROM applications
    WHERE status = 'eligible'
    AND scoring_status = 'pending'
""").fetchone()[0]

completed = connection.execute("""
    SELECT COUNT(*)
    FROM applications
    WHERE status = 'eligible'
    AND scoring_status = 'completed'
""").fetchone()[0]

print("\nELIGIBLE JOBS")
print("=" * 40)
print("Eligible pending:", pending)
print("Eligible completed:", completed)

connection.close()
