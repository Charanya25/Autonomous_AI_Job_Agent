
import sqlite3
from database.db_manager import DB_PATH

connection = sqlite3.connect(DB_PATH)

# Check database integrity
result = connection.execute("PRAGMA integrity_check").fetchone()[0]

print("Database integrity:", result)

# List all database tables
print("\nDatabase tables:")

tables = connection.execute("""
    SELECT name
    FROM sqlite_master
    WHERE type = 'table'
    ORDER BY name
""").fetchall()

for table in tables:
    print("-", table[0])

connection.close()
