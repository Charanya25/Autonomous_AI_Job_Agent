
from database import db_manager as db

jobs = db.get_all_jobs()

print("\nTOTAL JOBS IN DATABASE:", len(jobs))

for job in jobs[:10]:

    print("\n-------------------------")
    print("Title:", job["job_title"])
    print("Company:", job["company"])
    print("Location:", job["location"])
    print("Portal:", job["portal"])
    print("Status:", job["status"])
    print("URL:", job["job_url"])

print("\nDATABASE SUMMARY")
print(db.get_database_summary())
