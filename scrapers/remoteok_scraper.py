
import requests
from bs4 import BeautifulSoup

from database import db_manager as db

API_URL = "https://remoteok.com/api"

HEADERS = {
    "User-Agent": "AutonomousAIJobAgent/1.0",
    "Accept": "application/json"
}


def clean_description(description):
    """Remove HTML tags from job descriptions."""

    if not description:
        return ""

    soup = BeautifulSoup(description, "html.parser")
    return soup.get_text(separator=" ", strip=True)


def fetch_remoteok_jobs():
    """Fetch jobs from the RemoteOK public API."""

    print("\nConnecting to RemoteOK...")

    try:
        response = requests.get(
            API_URL,
            headers=HEADERS,
            timeout=30
        )

        response.raise_for_status()

        data = response.json()

        if not isinstance(data, list):
            raise ValueError("Invalid API response")

        # First item is metadata, not a job
        jobs_data = data[1:]

        jobs = []

        for item in jobs_data:

            if not isinstance(item, dict):
                continue

            title = item.get("position")
            company = item.get("company")
            job_url = item.get("url")

            if not job_url and item.get("slug"):
                job_url = (
                    "https://remoteok.com/remote-jobs/"
                    + item["slug"]
                )

            if not title or not company or not job_url:
                continue

            job = {
                "job_title": title.strip(),
                "company": company.strip(),
                "location": item.get("location") or "Remote",
                "job_url": job_url,
                "portal": "RemoteOK",
                "job_description": clean_description(
                    item.get("description", "")
                )
            }

            jobs.append(job)

        print("Jobs collected:", len(jobs))

        return jobs

    except requests.exceptions.RequestException as error:
        print("Network/API error:", error)

    except Exception as error:
        print("Scraper error:", error)

    return []


def save_jobs_to_database(jobs):
    """Save jobs into our SQLite database."""

    inserted = 0
    duplicates = 0

    for job in jobs:

        try:
            result = db.add_job(job)

            if result:
                inserted += 1
            else:
                duplicates += 1

        except Exception as error:
            print("Database error:", error)

    print("\nDatabase saving completed!")
    print("New jobs:", inserted)
    print("Duplicate jobs skipped:", duplicates)


def run_remoteok_scraper():

    print("\n==============================")
    print("AUTONOMOUS AI JOB AGENT")
    print("REMOTEOK SCRAPER")
    print("==============================")

    db.init_db()

    jobs = fetch_remoteok_jobs()

    if not jobs:
        print("No jobs collected.")
        return

    save_jobs_to_database(jobs)

    print("\nFIRST 5 JOBS")

    for job in jobs[:5]:

        print("\nTitle:", job["job_title"])
        print("Company:", job["company"])
        print("Location:", job["location"])
        print("URL:", job["job_url"])

    print("\nRemoteOK scraping completed!")


if __name__ == "__main__":
    run_remoteok_scraper()
