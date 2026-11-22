import sqlite3
from database.db_manager import DB_PATH

connection = sqlite3.connect(DB_PATH)
cursor = connection.cursor()

cursor.execute("""
    SELECT COUNT(*)
    FROM applications
    WHERE status = 'eligible'
    AND relevance_score IS NOT NULL
""")

scored = cursor.fetchone()[0]

cursor.execute("""
    SELECT COUNT(*)
    FROM applications
    WHERE status = 'eligible'
""")

total = cursor.fetchone()[0]

print("\nSCORING STATUS")
print("-" * 30)
print("Eligible jobs:", total)
print("Jobs scored:", scored)
print("Jobs remaining:", total - scored)

connection.close()