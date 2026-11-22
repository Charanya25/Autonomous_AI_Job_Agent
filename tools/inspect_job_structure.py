
import sys
import os
import sqlite3

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)
sys.path.insert(0, PROJECT_ROOT)

from playwright.sync_api import sync_playwright
from database.db_manager import DB_PATH


def get_benzinga_job():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    cursor.execute("""
        SELECT job_title, company, job_url
        FROM applications
        WHERE company = 'Benzinga'
        ORDER BY relevance_score DESC
        LIMIT 1
    """)

    result = cursor.fetchone()
    connection.close()

    return dict(result) if result else None


def inspect_page(page, job):
    print("\nJOB:", job["job_title"])
    print("COMPANY:", job["company"])

    page.goto(
        job["job_url"],
        wait_until="domcontentloaded",
        timeout=30000
    )

    page.wait_for_timeout(2000)

    print("\nPAGE TITLE:", page.title())
    print("PAGE URL:", page.url)

    print("\n--- JOB-RELATED HTML ELEMENTS ---")

    elements = page.locator(
        "[id*='job'], [class*='job'], "
        "[id*='description'], [class*='description'], "
        "[id*='apply'], [class*='apply']"
    ).evaluate_all("""
        elements => elements.slice(0, 30).map(el => ({
            tag: el.tagName,
            id: el.id,
            className: typeof el.className === 'string'
                ? el.className.substring(0, 200)
                : '',
            text: (el.innerText || '').substring(0, 250)
        }))
    """)

    for element in elements:
        print(element)
        print("-" * 40)

    print("\n--- APPLY LINKS ---")

    apply_links = page.locator("a").evaluate_all("""
        elements => elements
            .filter(a => {
                const text = (
                    (a.innerText || '') + ' ' +
                    (a.getAttribute('aria-label') || '')
                ).toLowerCase();

                return text.includes('apply');
            })
            .map(a => ({
                text: (a.innerText || '').trim(),
                href: a.href,
                parentClass: a.parentElement
                    ? a.parentElement.className
                    : ''
            }))
    """)

    for link in apply_links[:15]:
        print(link)

    print("\n--- MAIN PAGE TEXT SAMPLE ---")

    main_text = page.locator("body").inner_text()
    print(main_text[:2500])


def main():
    job = get_benzinga_job()

    if not job:
        print("Benzinga job not found in database.")
        return

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page()

        inspect_page(page, job)

        browser.close()

    print("\nSTRUCTURE INSPECTION COMPLETED.")
    print("No links clicked.")
    print("No applications submitted.")


if __name__ == "__main__":
    main()
