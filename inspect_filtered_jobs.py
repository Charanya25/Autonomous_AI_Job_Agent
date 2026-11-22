
import sqlite3
from database.db_manager import DB_PATH

connection = sqlite3.connect(DB_PATH)

query = """
SELECT id, job_title, company, location, notes
FROM applications
WHERE status = ?
AND (
    lower(location) LIKE ?
    OR lower(location) LIKE ?
    OR lower(location) LIKE ?
    OR lower(location) LIKE ?
)
ORDER BY id DESC
LIMIT 30
"""

rows = connection.execute(
    query,
    ("filtered_out", "%india%", "%hyderabad%", "%bangalore%", "%remote%")
).fetchall()

for row in rows:
    print("\nID:", row[0])
    print("Title:", row[1])
    print("Company:", row[2])
    print("Location:", row[3])
    print("Reason:", row[4])
    print("-" * 50)

print("\nMatching records:", len(rows))

connection.close()
