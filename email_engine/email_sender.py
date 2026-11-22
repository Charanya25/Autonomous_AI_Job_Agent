
import os
import re
import sqlite3
import smtplib

from pathlib import Path
from dotenv import load_dotenv
from email.message import EmailMessage

from database.db_manager import DB_PATH

load_dotenv()

GMAIL_ADDRESS = os.getenv("GMAIL_ADDRESS")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")

BASE_DIR = Path(__file__).resolve().parent.parent
RESUME_PATH = BASE_DIR / "data" / "resume.pdf"
DRAFT_DIR = BASE_DIR / "reports" / "email_drafts"


def get_approved_contacts():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()
    cursor.execute("""
        SELECT
            a.job_hash,
            a.company,
            a.job_title,
            a.hr_email,
            h.source
        FROM applications a
        INNER JOIN hr_contacts h
            ON LOWER(a.hr_email) = LOWER(h.hr_email)
            AND LOWER(a.company) = LOWER(h.company)
        WHERE a.status = 'manual_required'
          AND a.email_sent = 0
          AND a.hr_email IS NOT NULL
          AND TRIM(a.hr_email) != ''
          AND h.verified = 1
          AND LOWER(a.hr_email) NOT LIKE '%.example'
    """)

    contacts = [dict(row) for row in cursor.fetchall()]
    connection.close()

    return contacts


def get_draft(company, job_title):
    safe_name = re.sub(
        r"[^A-Za-z0-9_-]+",
        "_",
        f"{company}_{job_title}"
    ).strip("_")

    draft_path = DRAFT_DIR / f"{safe_name}.txt"

    if not draft_path.exists():
        print("Draft not found:", draft_path.name)
        return None

    content = draft_path.read_text(encoding="utf-8")
    lines = content.splitlines()

    subject = None
    subject_index = None

    for index, line in enumerate(lines):
        if line.startswith("Subject:"):
            subject = line.replace("Subject:", "", 1).strip()
            subject_index = index
            break

    if not subject:
        print("Subject missing in draft.")
        return None

    body_lines = lines[subject_index + 1:]

    while body_lines and not body_lines[0].strip():
        body_lines.pop(0)

    body = []

    for line in body_lines:
        if line.startswith((
            "STATUS:",
            "EMAIL SENT:",
            "REVIEW REQUIRED:"
        )):
            break
        body.append(line)

    return subject, "\n".join(body).strip()


def send_application_email(contact):
    recipient = contact["hr_email"]

    draft = get_draft(
        contact["company"],
        contact["job_title"]
    )

    if not draft:
        return False

    subject, body = draft

    message = EmailMessage()
    message["From"] = GMAIL_ADDRESS
    message["To"] = recipient
    message["Subject"] = subject

    message.set_content(body)

    with open(RESUME_PATH, "rb") as resume:
        message.add_attachment(
            resume.read(),
            maintype="application",
            subtype="pdf",
            filename="Sai_Charanya_Resume.pdf"
        )

    print("\nAPPLICATION EMAIL")
    print("=" * 50)
    print("Company:", contact["company"])
    print("Position:", contact["job_title"])
    print("Recipient:", recipient)
    print("Subject:", subject)
    print("Attachment: Sai_Charanya_Resume.pdf")

    approval = input(
        "\nType SEND to approve this email, or anything else to skip: "
    )

    if approval.strip() != "SEND":
        print("Email skipped. Nothing was sent.")
        return False

    with smtplib.SMTP_SSL(
        "smtp.gmail.com", 465, timeout=30
    ) as server:
        server.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
        server.send_message(message)

    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE applications
        SET email_sent = 1,
            status = 'email_sent',
            notes = COALESCE(notes, '') || ' | Application email sent'
        WHERE job_hash = ?
    """, (contact["job_hash"],))

    connection.commit()
    connection.close()

    print("Email sent successfully!")
    return True


def main():
    print("\nAI JOB APPLICATION EMAIL SENDER")
    print("=" * 50)

    if not GMAIL_ADDRESS or not GMAIL_APP_PASSWORD:
        print("Gmail credentials missing in .env")
        return

    if not RESUME_PATH.exists():
        print("Resume PDF not found:", RESUME_PATH)
        return

    contacts = get_approved_contacts()

    if not contacts:
        print("No verified recruiter email addresses available.")
        print("No emails will be sent.")
        return

    print("Verified contacts available:", len(contacts))

    for contact in contacts:
        try:
            send_application_email(contact)
        except Exception as error:
            print("Email sending failed:", error)


if __name__ == "__main__":
    main()
