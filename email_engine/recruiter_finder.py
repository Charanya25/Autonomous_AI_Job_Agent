
import sqlite3
from datetime import datetime, timezone

from database.db_manager import DB_PATH


COMPANY_INFO = {
    "Benzinga": {
        "domain": "benzinga.com",
        "careers_url": "https://jobs.benzinga.com/",
    },
    "Carrot": {
        "domain": "get-carrot.com",
        "careers_url": (
            "https://www.get-carrot.com/company/careers/open-roles"
        ),
    },
    "Prenosis": {
        "domain": "prenosis.com",
        "careers_url": "https://prenosis.com/careers/",
    },
    "Mirantis": {
        "domain": "mirantis.com",
        "careers_url": "https://jobs.smartrecruiters.com/Mirantis/",
    },
}


def create_company_sources_table(connection):
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS company_sources (
            company TEXT PRIMARY KEY,
            company_domain TEXT,
            careers_url TEXT,
            source_type TEXT,
            verification_status TEXT,
            checked_at TEXT
        )
    """)

    connection.commit()


def get_companies():
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    cursor.execute("""
        SELECT DISTINCT company
        FROM applications
        WHERE status = 'manual_required'
          AND company IS NOT NULL
          AND LOWER(company) != 'abc technologies'
        ORDER BY company
    """)

    companies = [row[0] for row in cursor.fetchall()]
    connection.close()

    return companies


def save_company_source(company, details):
    connection = sqlite3.connect(DB_PATH)
    create_company_sources_table(connection)

    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO company_sources (
            company,
            company_domain,
            careers_url,
            source_type,
            verification_status,
            checked_at
        )
        VALUES (?, ?, ?, ?, ?, ?)

        ON CONFLICT(company) DO UPDATE SET
            company_domain = excluded.company_domain,
            careers_url = excluded.careers_url,
            source_type = excluded.source_type,
            verification_status = excluded.verification_status,
            checked_at = excluded.checked_at
    """, (
        company,
        details["domain"],
        details["careers_url"],
        "official_careers_page",
        "official_page_recorded_email_not_verified",
        datetime.now(timezone.utc).isoformat()
    ))

    connection.commit()
    connection.close()


def run_recruiter_finder():
    print("\nRECRUITER CONTACT AND CAREERS FINDER")
    print("=" * 60)

    companies = get_companies()

    print("Companies to research:", len(companies))

    saved = 0
    not_found = 0

    for number, company in enumerate(companies, start=1):
        print(f"\n{number}. Company: {company}")

        details = COMPANY_INFO.get(company)

        if not details:
            print("No official careers page configured.")
            not_found += 1
            continue

        save_company_source(company, details)

        print("Company domain:", details["domain"])
        print("Official careers page:", details["careers_url"])
        print("Careers page recorded successfully.")
        print("Recruiter email: NOT VERIFIED")

        saved += 1

    print("\n" + "=" * 60)
    print("RESEARCH SUMMARY")
    print("=" * 60)
    print("Careers pages recorded:", saved)
    print("Companies needing further research:", not_found)
    print("Recruiter emails invented: 0")
    print("Emails sent: 0")


if __name__ == "__main__":
    run_recruiter_finder()
