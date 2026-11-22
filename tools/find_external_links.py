
import os
import sqlite3
from urllib.parse import urljoin, urlparse

from playwright.sync_api import sync_playwright


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DB_PATH = os.path.join(
    PROJECT_ROOT,
    "database",
    "job_agent.db"
)

MINIMUM_SCORE = 6.0
MAX_JOBS = 4


def get_jobs():

    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            job_hash,
            job_url,
            job_title,
            company,
            portal,
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


def inspect_remoteok(page, job):

    print("\nREMOTEOK INSPECTION")

    print("Company:", job["company"])
    print("Job:", job["job_title"])

    print("\nApply link:")

    apply_links = page.locator(
        "a[class*='action-apply']"
    )

    found = False

    for index in range(apply_links.count()):

        link = apply_links.nth(index)

        text = link.inner_text().strip()
        href = link.get_attribute("href")

        if href:

            print("Text:", text)
            print("URL:", urljoin(page.url, href))
            found = True

    if not found:
        print("No Apply link found.")

    print("\nNo links clicked.")


def inspect_jobicy(page, job):

    print("\nJOBICY INSPECTION")

    print("Company:", job["company"])
    print("Job:", job["job_title"])

    application_section = page.locator(
        "#job-application"
    )

    print(
        "\nApplication sections:",
        application_section.count()
    )

    if application_section.count() == 0:

        print("Application section not found.")
        return

    print("\nAPPLICATION SECTION TEXT:")
    print(application_section.inner_text())

    # Extract all links from the application section.
    links = application_section.locator("a")

    print("\nAPPLICATION LINKS:")
    print("Number of links:", links.count())

    for index in range(links.count()):

        link = links.nth(index)

        text = link.inner_text().strip()

        href = link.get_attribute("href")

        if href:

            print(f"\nLink {index + 1}")
            print("Text:", text)
            print("Original href:", href)
            print("Resolved URL:", urljoin(page.url, href))

            print(
                "External:",
                urlparse(urljoin(page.url, href)).netloc.lower()
                != urlparse(page.url).netloc.lower()
            )

    # Inspect buttons without clicking.
    buttons = application_section.locator("button")

    print("\nAPPLICATION BUTTONS:")
    print("Number of buttons:", buttons.count())

    for index in range(buttons.count()):

        button = buttons.nth(index)

        print(f"\nButton {index + 1}")
        print("Text:", button.inner_text())

        print(
            "HTML:",
            button.evaluate(
                "element => element.outerHTML"
            )[:1500]
        )

    # Inspect forms.
    forms = application_section.locator("form")

    print("\nAPPLICATION FORMS:")
    print("Number of forms:", forms.count())

    for index in range(forms.count()):

        form = forms.nth(index)

        print(
            form.evaluate(
                """element => ({
                    action: element.action,
                    method: element.method
                })"""
            )
        )

    # Inspect iframe elements.
    frames = application_section.locator("iframe")

    print("\nIFRAMES:")
    print("Number of iframes:", frames.count())

    for index in range(frames.count()):

        frame = frames.nth(index)

        print(
            frame.evaluate(
                "element => element.outerHTML"
            )[:1500]
        )

    print("\nNo buttons clicked.")
    print("No application submitted.")


def main():

    print("\nAPPLICATION DESTINATION INSPECTOR")
    print("=" * 60)

    jobs = get_jobs()

    print("Jobs selected:", len(jobs))

    if not jobs:
        print("No eligible jobs found.")
        return

    with sync_playwright() as playwright:

        browser = playwright.chromium.launch(
            headless=True
        )

        page = browser.new_page()

        for index, job in enumerate(jobs, 1):

            print("\n" + "#" * 60)
            print(f"JOB {index}: {job['company']}")
            print("#" * 60)

            try:

                response = page.goto(
                    job["job_url"],
                    wait_until="domcontentloaded",
                    timeout=45000
                )

                if response:
                    print("HTTP status:", response.status)

                page.wait_for_timeout(2500)

                portal = job["portal"].lower()

                if "remoteok" in portal:

                    inspect_remoteok(page, job)

                elif "jobicy" in portal:

                    inspect_jobicy(page, job)

                else:

                    print("Portal not configured.")

            except Exception as error:

                print("Inspection error:", error)

        browser.close()

    print("\n" + "=" * 60)
    print("INSPECTION FINISHED")
    print("No applications submitted.")
    print("No emails sent.")
    print("=" * 60)


if __name__ == "__main__":
    main()
