
import sqlite3
from database.db_manager import DB_PATH

# Safety settings
DRY_RUN = True
MINIMUM_SCORE = 6.0
MAX_JOBS_PER_RUN = 10

SENIOR_KEYWORDS = [
    "senior", "staff", "principal", "lead",
    "director", "manager", "head of"
]


def get_selected_jobs():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            job_hash,
            job_title,
            company,
            location,
            portal,
            job_url,
            relevance_score,
            notes
        FROM applications
        WHERE status = 'eligible'
          AND relevance_score >= ?
        ORDER BY relevance_score DESC
        LIMIT ?
    """, (MINIMUM_SCORE, MAX_JOBS_PER_RUN))

    jobs = [dict(row) for row in cursor.fetchall()]
    connection.close()

    return jobs


def check_job(job):
    title = (job["job_title"] or "").lower()

    # Flag possible senior-level jobs
    for keyword in SENIOR_KEYWORDS:
        if keyword in title:
            return "manual_required", "Possible senior-level position"

    # Job eligibility needs human confirmation
    return "manual_required", "Needs eligibility and application review"


def run_application_engine():
    print("\nAUTONOMOUS AI JOB APPLICATION ENGINE")
    print("=" * 55)

    jobs = get_selected_jobs()

    if not jobs:
        print("No eligible jobs found above the score threshold.")
        return

    print("Selected jobs:", len(jobs))
    print("Minimum relevance score:", MINIMUM_SCORE)
    print("Dry-run mode:", DRY_RUN)

    print("\nAPPLICATION REVIEW")
    print("-" * 55)

    for number, job in enumerate(jobs, start=1):
        proposed_status, reason = check_job(job)

        print(f"\nJob {number}")
        print("Title:", job["job_title"])
        print("Company:", job["company"])
        print("Location:", job["location"])
        print("Portal:", job["portal"])
        print("Score:", job["relevance_score"])
        print("Proposed status:", proposed_status)
        print("Reason:", reason)
        print("Application URL:", job["job_url"])

        if DRY_RUN:
            print("Action: No application submitted.")

    print("\n" + "=" * 55)
    print("DRY RUN COMPLETED")
    print("No applications were submitted.")
    print("No database statuses were changed.")


if __name__ == "__main__":
    run_application_engine()
