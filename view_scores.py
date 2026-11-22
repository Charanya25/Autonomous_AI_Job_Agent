import sqlite3
from database.db_manager import DB_PATH

connection = sqlite3.connect(DB_PATH)
cursor = connection.cursor()

cursor.execute("""
    SELECT job_title, company, relevance_score, status
    FROM applications
    WHERE status = 'eligible'
    ORDER BY relevance_score DESC
    LIMIT 10
""")

print("\nTOP 10 MATCHING JOBS")
print("-" * 70)

for row in cursor.fetchall():
    print(f"\nJob: {row[0]}")
    print(f"Company: {row[1]}")
    print(f"Score: {row[2]}")
    print(f"Status: {row[3]}")

connection.close()