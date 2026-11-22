
import sqlite3

from database.db_manager import DB_PATH

connection = sqlite3.connect(DB_PATH)

cursor = connection.cursor()

cursor.execute("""
    SELECT portal, COUNT(*)
    FROM applications
    GROUP BY portal
""")

results = cursor.fetchall()

print("\nJOB PORTAL SUMMARY")
print("-" * 40)

for portal, count in results:
    print(f"{portal}: {count} jobs")

connection.close()
