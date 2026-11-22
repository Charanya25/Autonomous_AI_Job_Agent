
import sys
import os
import sqlite3

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)
sys.path.insert(0, PROJECT_ROOT)

from playwright.sync_api import sync_playwright, TimeoutError
from database.db_manager import DB_PATH

MAX_JOBS = 4
MINIMUM_SCORE = 6.0


def get_jobs():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    cursor.execute("""
        SELECT job_title, company, job_url, portal,
               relevance_score
        FROM applications
        WHERE status = 'eligible'
          AND relevance_score >= ?
        ORDER BY relevance_score DESC
        LIMIT ?
    """, (MINIMUM_SCORE, MAX_JOBS))

    jobs = [dict(row) for row in cursor.fetchall()]
    connection.close()
    return jobs


def inspect_destination(page, job):
    print("\n" + "=" * 65)
    print("COMPANY:", job["company"])
    print("JOB:", job["job_title"])

    try:
        page.goto(
            job["job_url"],
            wait_until="domcontentloaded",
            timeout=30000
        )

        page.wait_for_timeout(1000)

        portal = (job["portal"] or "").lower()
        destination = None

        if "remoteok" in portal:
            job_id = job["job_url"].rstrip("/").split("-")[-1]

            apply_link = page.locator(
                f'a[href*="/l/{job_id}"]'
            ).first

            if apply_link.count() > 0:
                destination = apply_link.get_attribute("href")

        elif "jobicy" in portal:
            destination = (
                job["job_url"].rstrip("/") + "#job-application"
            )

        if not destination:
            print("Application destination not found.")
            return

        if destination.startswith("/"):
            from urllib.parse import urljoin
            destination = urljoin(job["job_url"], destination)

        print("Application link:", destination)

        response = page.goto(
            destination,
            wait_until="domcontentloaded",
            timeout=30000
        )

        page.wait_for_timeout(1500)

        print("Final URL:", page.url)
        print("Page title:", page.title())

        if response:
            print("HTTP status:", response.status)

        # Inspect only visible, interactive form fields.
        fields = page.locator(
            "input:not([type='hidden']), textarea, select"
        ).evaluate_all("""
            elements => elements
                .filter(el => {
                    const style = window.getComputedStyle(el);
                    return style.display !== 'none'
                        && style.visibility !== 'hidden';
                })
                .map(el => ({
                    tag: el.tagName,
                    type: el.type || '',
                    name: el.name || '',
                    placeholder: el.placeholder || '',
                    required: el.required
                }))
        """)

        print("\nVISIBLE FORM FIELDS:", len(fields))

        for field in fields[:20]:
            print(field)

        forms = page.locator("form")
        print("Forms on destination page:", forms.count())

        print("\nACTION: Inspection only")
        print("APPLICATION SUBMITTED: NO")

    except TimeoutError:
        print("Destination inspection timed out.")

    except Exception as error:
        print("Inspection error:", error)


def main():
    jobs = get_jobs()

    print("\nAPPLICATION DESTINATION INSPECTOR")
    print("=" * 65)
    print("Jobs selected:", len(jobs))

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page()

        for job in jobs:
            inspect_destination(page, job)

        browser.close()

    print("\nDESTINATION INSPECTION COMPLETED")
    print("No applications submitted.")


if __name__ == "__main__":
    main()
