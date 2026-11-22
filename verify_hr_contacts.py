
import sqlite3
from database.db_manager import DB_PATH

connection = sqlite3.connect(DB_PATH)

print("HR CONTACT VERIFICATION")
print("=" * 40)

rows = connection.execute("""
    SELECT verified, COUNT(*)
    FROM hr_contacts
    GROUP BY verified
""").fetchall()

verified_total = 0
unverified_total = 0

for verified, count in rows:
    if verified == 1:
        verified_total = count
    else:
        unverified_total += count

print("Verified contacts:", verified_total)
print("Unverified contacts:", unverified_total)
print("Total contacts:", verified_total + unverified_total)

connection.close()
