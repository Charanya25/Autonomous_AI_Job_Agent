
import sys
import os
import sqlite3
from urllib.parse import urljoin, urlparse

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)
sys.path.insert(0, PROJECT_ROOT)

from playwright.sync_api import sync_playwright, TimeoutError
from database.db_manager import DB_PATH

MINIMUM_SCORE = 6.0
MAX_JOBS = 4

def get_jobs():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    cursor.execute("""
        SELECT job_title, company, job_url, relevance_score, portal
        FROM applications
        WHERE status = 'eligible'
          AND relevance_score >= ?
        ORDER BY relevance_score DESC
        LIMIT ?
    """, (MINIMUM_SCORE, MAX_JOBS))

    jobs = [dict(row) for row in cursor.fetchall()]
    connection.close()
    return jobs


def inspect_job(page, job):
    print("\n" + "=" * 65)
    print("JOB:", job["job_title"])
    print("COMPANY:", job["company"])
    print("PORTAL:", job["portal"])
    print("SCORE:", job["relevance_score"])

    try:
        response = page.goto(
            job["job_url"],
            wait_until="domcontentloaded",
            timeout=30000
        )

        if response:
            print("HTTP STATUS:", response.status)

        page.wait_for_timeout(1500)

        print("PAGE TITLE:", page.title())

        # Find links that appear related to this job
        links = page.locator("a").evaluate_all("""
            elements => elements.map(a => ({
                text: (a.innerText || a.textContent || '').trim(),
                href: a.href,
                className: a.className || '',
                ariaLabel: a.getAttribute('aria-label') || ''
            }))
        """)

        job_id = ""
        if "remoteok.com" in job["job_url"].lower():
            job_id = job["job_url"].rstrip("/").split("-")[-1]

        application_links = []

        for link in links:
            text = link["text"].lower()
            href = link["href"].lower()

            if not any(word in text for word in ["apply", "application"]):
                continue

            # For RemoteOK, prioritize links for this job ID
            if job_id and job_id in href:
                application_links.append(link)

            # For other portals, retain job-specific application links
            elif not job_id:
                if "job-application" in href or href.startswith(job["job_url"].lower()):
                    application_links.append(link)

        print("\nJOB-SPECIFIC APPLICATION LINKS:")

        unique_links = []
        seen = set()

        for link in application_links:
            if link["href"] not in seen:
                seen.add(link["href"])
                unique_links.append(link)

        for link in unique_links[:10]:
            print("Text:", link["text"])
            print("URL:", link["href"])

        if not unique_links:
            print("No job-specific Apply link identified.")

        # Inspect forms without filling or submitting them
        forms = page.locator("form")
        form_count = forms.count()

        print("\nFORMS FOUND:", form_count)

        for index in range(form_count):
            form = forms.nth(index)

            fields = form.locator("input, textarea, select").evaluate_all("""
                elements => elements.map(el => ({
                    type: el.type || el.tagName.toLowerCase(),
                    name: el.name || '',
                    placeholder: el.placeholder || '',
                    required: el.required
                }))
            """)

            print(f"\nFORM {index + 1} FIELDS:")
            for field in fields:
                print(field)

        # Classify the route
        if form_count > 0:
            route_status = "manual_required"
            reason = "Application form found; review before submission."
        elif unique_links:
            route_status = "manual_required"
            reason = "Apply link found; destination needs inspection."
        else:
            route_status = "unsupported"
            reason = "No usable application route identified."

        print("\nROUTE STATUS:", route_status)
        print("REASON:", reason)
        print("APPLICATION SUBMITTED: NO")

    except TimeoutError:
        print("ROUTE STATUS: manual_required")
        print("REASON: Page loading timed out.")

    except Exception as error:
        print("INSPECTION ERROR:", error)


def run_inspector():
    jobs = get_jobs()

    print("\nIMPROVED PLAYWRIGHT JOB INSPECTOR")
    print("=" * 65)
    print("Jobs selected:", len(jobs))

    if not jobs:
        print("No matching jobs found.")
        return

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page()

        for job in jobs:
            inspect_job(page, job)

        browser.close()

    print("\n" + "=" * 65)
    print("INSPECTION COMPLETED")
    print("No applications submitted.")


if __name__ == "__main__":
    run_inspector()
