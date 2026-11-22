
import sqlite3
from email_validator import validate_email, EmailNotValidError

from database.db_manager import DB_PATH


def check_email_address(email):
    """Check email syntax and domain mail deliverability."""

    try:
        result = validate_email(
            email,
            check_deliverability=True
        )

        return True, result.normalized, "Valid syntax and mail domain"

    except EmailNotValidError as error:
        return False, None, str(error)

    except Exception as error:
        return False, None, f"Could not complete DNS check: {error}"


def get_recruiter_contacts():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()

    cursor.execute("""
        SELECT id, company, hr_name, hr_email,
               company_domain, source
        FROM hr_contacts
        WHERE hr_email IS NOT NULL
          AND TRIM(hr_email) != ''
          AND LOWER(hr_email) NOT LIKE '%.example'
    """)

    contacts = [dict(row) for row in cursor.fetchall()]
    connection.close()

    return contacts


def run_email_validation():
    print("\nRECRUITER EMAIL VALIDATION")
    print("=" * 55)

    contacts = get_recruiter_contacts()

    if not contacts:
        print("No real recruiter email addresses available.")
        print("Placeholder addresses are excluded.")
        print("Add a publicly listed contact before validation.")
        return

    for number, contact in enumerate(contacts, start=1):
        print(f"\nContact {number}")
        print("Company:", contact["company"])
        print("Recruiter:", contact["hr_name"] or "Not specified")
        print("Email:", contact["hr_email"])

        valid, normalized, reason = check_email_address(
            contact["hr_email"]
        )

        print("Validation:", "Passed" if valid else "Not passed")
        print("Result:", reason)

        if valid:
            print("Normalized email:", normalized)
            print("Human confirmation: Still required")
        else:
            print("Action: Review the email address.")

    print("\nVALIDATION COMPLETED")
    print("No emails were sent.")
    print("No recruiter was marked as personally verified.")


if __name__ == "__main__":
    run_email_validation()
