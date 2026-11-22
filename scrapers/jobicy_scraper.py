
import requests
from bs4 import BeautifulSoup

from database import db_manager as db


API_URL = "https://jobicy.com/api/jobs"

HEADERS = {
    "User-Agent": "AutonomousAIJobAgent/1.0",
    "Accept": "application/json"
}


def clean_description(description):

    if not description:
        return ""

    soup = BeautifulSoup(description, "html.parser")

    return soup.get_text(separator=" ", strip=True)


def fetch_jobicy_jobs():

    print("\nConnecting to Jobicy API...")

    try:

        response = requests.get(
            API_URL,
            params={"count": 100},
            headers=HEADERS,
            timeout=30
        )

        response.raise_for_status()

        data = response.json()

        if not isinstance(data, dict):
            raise ValueError("Unexpected API response")

        if data.get("success") is False:
            raise ValueError(data.get("error", "API request failed"))

        jobs_data = data.get("jobs", [])

        jobs = []

        for item in jobs_data:

            if not isinstance(item, dict):
                continue

            title = item.get("jobTitle")
            company = item.get("companyName")
            job_url = item.get("url")

            if not title or not company or not job_url:
                continue

            job = {
                "job_title": title.strip(),
                "company": company.strip(),
                "location": item.get("jobGeo") or "Remote",
                "job_url": job_url,
                "portal": "Jobicy",
                "job_description": clean_description(
                    item.get("jobDescription", "")
                )
            }

            jobs.append(job)

        print("Jobicy connection successful!")
        print("Jobs collected:", len(jobs))

        return jobs

    except requests.exceptions.RequestException as error:

        print("Network/API error:", error)

    except Exception as error:

        print("Scraper error:", error)

    return []


def save_jobs_to_database(jobs):

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


def run_jobicy_scraper():

    print("\n==============================")
    print("AUTONOMOUS AI JOB AGENT")
    print("JOBICY SCRAPER")
    print("==============================")

    db.init_db()

    jobs = fetch_jobicy_jobs()

    if not jobs:

        print("No jobs collected.")
        return

    save_jobs_to_database(jobs)

    print("\nFIRST 5 JOBS")

    for job in jobs[:5]:

        print("\nTitle:", job["job_title"])
        print("Company:", job["company"])
        print("Location:", job["location"])
        print("Portal:", job["portal"])
        print("Source: Jobicy")
        print("URL:", job["job_url"])

    print("\nJobicy scraping completed!")


if __name__ == "__main__":

    run_jobicy_scraper()
