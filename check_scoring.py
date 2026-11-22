import sqlite3
from database.db_manager import DB_PATH

connection = sqlite3.connect(DB_PATH)

eligible = connection.execute(
    "SELECT COUNT(*) FROM applications WHERE status = 'eligible'"
).fetchone()[0]

scored = connection.execute(
    """
    SELECT COUNT(*) FROM applications
    WHERE status = 'eligible'
    AND relevance_score > 0
    """
).fetchone()[0]

unscored = eligible - scored

print("Eligible jobs:", eligible)
print("Scored jobs:", scored)
print("Unscored jobs:", unscored)

connection.close()