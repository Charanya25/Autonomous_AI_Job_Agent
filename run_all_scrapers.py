
import sqlite3

from database.db_manager import DB_PATH

from scrapers.remoteok_scraper import run_remoteok_scraper
from scrapers.jobicy_scraper import run_jobicy_scraper
from scrapers.arbeitnow_scraper import run_arbeitnow_scraper


def get_job_count():
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    cursor.execute("SELECT COUNT(*) FROM applications")
    count = cursor.fetchone()[0]

    connection.close()
    return count


def run_all_scrapers():

    print("\n================================")
    print("AUTONOMOUS AI JOB AGENT")
    print("MULTI-PORTAL SCRAPER")
    print("================================")

    jobs_before = get_job_count()
    successful_portals = 0
    failed_portals = []

    scrapers = [
        ("RemoteOK", run_remoteok_scraper),
        ("Jobicy", run_jobicy_scraper),
        ("Arbeitnow", run_arbeitnow_scraper)
    ]

    for portal_name, scraper_function in scrapers:

        print(f"\nStarting {portal_name} scraper...")

        try:
            scraper_function()
            successful_portals += 1

        except Exception as error:
            print(f"{portal_name} scraper failed:", error)
            failed_portals.append(portal_name)

    jobs_after = get_job_count()
    new_jobs = jobs_after - jobs_before

    print("\n================================")
    print("FINAL JOB DATABASE SUMMARY")
    print("================================")

    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    cursor.execute("""
        SELECT portal, COUNT(*)
        FROM applications
        GROUP BY portal
    """)

    for portal, count in cursor.fetchall():
        print(f"{portal}: {count} jobs")

    print("\nTOTAL JOBS:", jobs_after)
    print("NEW JOBS:", new_jobs)
    print("SUCCESSFUL PORTALS:", successful_portals)
    print("FAILED PORTALS:", failed_portals)

    connection.close()

    print("\nAll scraper processes finished!")

    return {
        "jobs_before": jobs_before,
        "jobs_after": jobs_after,
        "jobs_scraped": jobs_after - jobs_before,
        "new_jobs": new_jobs,
        "successful_portals": successful_portals,
        "failed_portals": failed_portals
    }


if __name__ == "__main__":
    result = run_all_scrapers()
    print("\nScraper result:", result)
