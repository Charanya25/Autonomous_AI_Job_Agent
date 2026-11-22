
import sqlite3
from database.db_manager import DB_PATH

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
        SELECT job_hash, job_title, company, location,
               portal, job_url, relevance_score
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
    portal = (job["portal"] or "").lower()

    for keyword in SENIOR_KEYWORDS:
        if keyword in title:
            return (
                "manual_required",
                "Possible senior-level position. Manual review required."
            )

    if "remoteok" in portal:
        return (
            "manual_required",
            "RemoteOK application destination is not verified. "
            "Review the employer application process manually."
        )

    if "jobicy" in portal:
        return (
            "manual_required",
            "Jobicy application requires further review. "
            "No verified employer application URL was found."
        )

    return (
        "manual_required",
        "Application route and eligibility are not verified. "
        "Manual review required."
    )


def save_job_status(job_hash, status, reason):
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE applications
        SET status = ?, notes = ?
        WHERE job_hash = ?
    """, (status, reason, job_hash))

    connection.commit()
    connection.close()


def run_application_engine():
    print("\nAUTONOMOUS AI JOB APPLICATION ENGINE")
    print("=" * 55)

    jobs = get_selected_jobs()

    if not jobs:
        print("No eligible jobs found above the score threshold.")
        return

    print("Selected jobs:", len(jobs))
    print("Minimum relevance score:", MINIMUM_SCORE)

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
        print("Job URL:", job["job_url"])

        save_job_status(
            job["job_hash"],
            proposed_status,
            reason
        )

        print("Database: Status saved successfully.")
        print("Action: No application submitted.")

    print("\nAPPLICATION ENGINE COMPLETED")
    print("Job statuses saved to the database.")
    print("No applications were submitted.")
    print("No emails were sent.")


if __name__ == "__main__":
    run_application_engine()
