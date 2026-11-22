
from database import db_manager as db


# 1. Initialize database
db.init_db()


# 2. Insert sample job
sample_job = {
    "job_url": "https://example.com/jobs/python-developer-101",
    "job_title": "Python Developer - Fresher",
    "company": "ABC Technologies",
    "location": "Hyderabad",
    "portal": "RemoteOK",
    "job_description": "Python, SQL, Flask and REST API development"
}

result = db.add_job(sample_job)

print("\nJob inserted:", result)


# 3. Insert the same job again
duplicate = db.add_job(sample_job)

print("Duplicate job inserted:", duplicate)


# 4. Get all jobs
jobs = db.get_all_jobs()

print("\nALL JOBS:")

for job in jobs:
    print(job["job_title"], "-", job["company"])


# 5. Update job score
job_hash = db.generate_job_hash(sample_job["job_url"])

db.update_job_score(job_hash, 9.0)

print("\nJob score updated to 9.0")


# 6. Update job status
db.update_job_status(job_hash, "manual_required")

print("Job status updated")


# 7. Add HR contact
hr_result = db.add_hr_contact(
    company="ABC Technologies",
    company_domain="abc.example",
    hr_name="HR Team",
    hr_email="hr@abc.example",
    source="pattern"
)

print("\nHR contact inserted:", hr_result)


# 8. Add drip contact
drip_result = db.add_drip_contact(
    email="recruiter@abc.example",
    name="Recruiter",
    company="ABC Technologies",
    designation="HR"
)

print("Drip contact inserted:", drip_result)


# 9. Save daily statistics
db.save_daily_stats(
    total_scraped=10,
    total_new=5,
    total_applied=0,
    total_emailed=0,
    total_failed=0,
    run_time_seconds=12.5
)

print("\nDaily statistics saved")


# 10. Display database summary
print("\nDATABASE SUMMARY:")

print(db.get_database_summary())


# 11. Display daily statistics
print("\nDAILY STATISTICS:")

print(db.get_daily_stats())

print("\nDATABASE TEST COMPLETED!")
