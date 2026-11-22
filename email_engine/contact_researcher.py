
import re
import sqlite3
import requests

from bs4 import BeautifulSoup
from urllib.parse import urlparse

from database.db_manager import DB_PATH


# Browser-like headers for public webpage requests
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 Chrome/120.0 Safari/537.36"
}


# Email extraction pattern
EMAIL_PATTERN = re.compile(
    r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"
)


# Emails related to non-recruitment purposes
BLOCKED_KEYWORDS = [
    "security",
    "privacy",
    "abuse",
    "support",
    "help",
    "billing",
    "legal",
    "press",
    "media",
    "noreply",
    "no-reply"
]


def get_company_sources():
    """Get company careers pages from SQLite."""

    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row

    rows = connection.execute("""
        SELECT company, company_domain, careers_url
        FROM company_sources
    """).fetchall()

    connection.close()

    return [dict(row) for row in rows]


def get_research_urls(careers_url):
    """Generate a small list of public pages to inspect."""

    parsed = urlparse(careers_url)

    base_url = f"{parsed.scheme}://{parsed.netloc}"

    return [
        careers_url,
        base_url + "/contact",
        base_url + "/about"
    ]


def extract_public_emails(url):
    """Extract email addresses visible on a public webpage."""

    try:
        response = requests.get(
            url,
            headers=HEADERS,
            timeout=15
        )

        if response.status_code != 200:
            print("HTTP status:", response.status_code)
            return []

        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )

        emails = set(
            EMAIL_PATTERN.findall(response.text)
        )

        # Also inspect mailto links
        for link in soup.select('a[href^="mailto:"]'):

            email = (
                link.get("href", "")
                .replace("mailto:", "")
                .split("?")[0]
                .strip()
            )

            if EMAIL_PATTERN.fullmatch(email):
                emails.add(email)

        return sorted(emails)

    except requests.RequestException as error:

        print("Page request failed:", error)

        return []


def save_public_contact(company, email, source_url):
    """Save a public contact as unverified."""

    connection = sqlite3.connect(DB_PATH)

    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO hr_contacts (
            company,
            company_domain,
            hr_name,
            hr_email,
            source,
            verified
        )
        VALUES (?, ?, NULL, ?, ?, 0)
        ON CONFLICT DO NOTHING
    """, (
        company,
        email.split("@")[-1].lower(),
        email,
        source_url
    ))

    connection.commit()
    connection.close()


def is_recruitment_contact(email):
    """Exclude obvious non-recruitment email addresses."""

    email_lower = email.lower()

    for keyword in BLOCKED_KEYWORDS:

        if keyword in email_lower:
            return False

    return True


def run_research():

    print("\nPUBLIC CONTACT RESEARCH")
    print("=" * 55)

    companies = get_company_sources()

    total_found = 0

    print("Companies to research:", len(companies))

    for company_data in companies:

        company = company_data["company"]

        company_domain = company_data["company_domain"]

        print("\nCompany:", company)

        found_for_company = set()

        research_urls = get_research_urls(
            company_data["careers_url"]
        )

        for url in research_urls:

            print("Checking:", url)

            emails = extract_public_emails(url)

            for email in emails:

                domain = email.split("@")[-1].lower()

                # Accept only the company's configured domain
                if domain != company_domain:
                    continue

                # Exclude security/support and other unrelated contacts
                if not is_recruitment_contact(email):

                    print(
                        "Excluded non-recruitment contact:",
                        email
                    )

                    continue

                found_for_company.add((email, url))

        if not found_for_company:

            print("No matching public company email found.")

            continue

        for email, source_url in sorted(found_for_company):

            save_public_contact(
                company,
                email,
                source_url
            )

            print("Public email found:", email)

            print("Source:", source_url)

            print("Verification: NOT VERIFIED")

            total_found += 1

    print("\n" + "=" * 55)

    print(
        "Public email addresses recorded:",
        total_found
    )

    print("Addresses automatically verified: 0")

    print("Emails sent: 0")


if __name__ == "__main__":

    run_research()
