
import sqlite3
import hashlib
from pathlib import Path
from datetime import datetime, date


# ==================================================
# DATABASE CONFIGURATION
# ==================================================

DB_PATH = Path(__file__).resolve().parent / "job_agent.db"


# ==================================================
# DATABASE CONNECTION
# ==================================================

def get_connection():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


# ==================================================
# INITIALIZE DATABASE
# ==================================================

def init_db():

    with get_connection() as conn:

        cursor = conn.cursor()

        # 1. Applications table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS applications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_hash TEXT UNIQUE NOT NULL,
                job_url TEXT,
                job_title TEXT,
                company TEXT,
                location TEXT,
                portal TEXT,
                job_description TEXT,
                status TEXT DEFAULT 'new',
                applied_date TEXT,
                hr_email TEXT,
                email_sent INTEGER DEFAULT 0,
                relevance_score REAL DEFAULT 0,
                notes TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Add scoring_status safely to existing databases
        cursor.execute("PRAGMA table_info(applications)")

        columns = [
            column["name"]
            for column in cursor.fetchall()
        ]

        if "scoring_status" not in columns:

            cursor.execute("""
                ALTER TABLE applications
                ADD COLUMN scoring_status TEXT DEFAULT 'pending'
            """)

        # Mark previously scored positive scores as completed
        cursor.execute("""
            UPDATE applications
            SET scoring_status = 'completed'
            WHERE relevance_score > 0
        """)

        # 2. HR Contacts table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS hr_contacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company TEXT,
                company_domain TEXT,
                hr_name TEXT,
                hr_email TEXT,
                source TEXT,
                verified INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(company_domain, hr_email)
            )
        """)

        # 3. Daily Statistics table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS daily_stats (
                date TEXT PRIMARY KEY,
                total_scraped INTEGER DEFAULT 0,
                total_new INTEGER DEFAULT 0,
                total_applied INTEGER DEFAULT 0,
                total_emailed INTEGER DEFAULT 0,
                total_failed INTEGER DEFAULT 0,
                run_time_seconds REAL DEFAULT 0
            )
        """)

        # 4. Drip Outreach table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS drip_outreach (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                name TEXT,
                company TEXT,
                designation TEXT,
                sent_date TEXT,
                status TEXT DEFAULT 'pending'
            )
        """)

        conn.commit()

    print("Database initialized successfully!")


# ==================================================
# GENERATE JOB HASH
# ==================================================

def generate_job_hash(job_url):

    return hashlib.sha256(
        job_url.encode("utf-8")
    ).hexdigest()[:16]


# ==================================================
# ADD NEW JOB
# ==================================================

def add_job(job):

    job_hash = generate_job_hash(job["job_url"])

    with get_connection() as conn:

        cursor = conn.cursor()

        cursor.execute("""
            INSERT OR IGNORE INTO applications (
                job_hash,
                job_url,
                job_title,
                company,
                location,
                portal,
                job_description
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            job_hash,
            job["job_url"],
            job.get("job_title"),
            job.get("company"),
            job.get("location"),
            job.get("portal"),
            job.get("job_description")
        ))

        return cursor.rowcount == 1


# ==================================================
# GET ALL JOBS
# ==================================================

def get_all_jobs():

    with get_connection() as conn:

        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM applications
            ORDER BY created_at DESC
        """)

        return [dict(row) for row in cursor.fetchall()]


# ==================================================
# GET JOBS BY STATUS
# ==================================================

def get_jobs_by_status(status):

    with get_connection() as conn:

        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM applications
            WHERE status = ?
        """, (status,))

        return [dict(row) for row in cursor.fetchall()]


# ==================================================
# UPDATE JOB STATUS
# ==================================================

def update_job_status(job_hash, status):

    allowed_statuses = {
        "new",
        "applied",
        "email_sent",
        "failed",
        "manual_required"
    }

    if status not in allowed_statuses:
        raise ValueError("Invalid application status")

    with get_connection() as conn:

        cursor = conn.cursor()

        cursor.execute("""
            UPDATE applications
            SET status = ?,
                applied_date = CASE
                    WHEN ? = 'applied' THEN ?
                    ELSE applied_date
                END
            WHERE job_hash = ?
        """, (
            status,
            status,
            datetime.now().isoformat(timespec="seconds"),
            job_hash
        ))

        return cursor.rowcount > 0


# ==================================================
# UPDATE JOB RELEVANCE SCORE
# ==================================================

def update_job_score(job_hash, score):

    if not 0 <= score <= 10:
        raise ValueError("Score must be between 0 and 10")

    with get_connection() as conn:

        cursor = conn.cursor()

        cursor.execute("""
            UPDATE applications
            SET relevance_score = ?,
                scoring_status = 'completed'
            WHERE job_hash = ?
        """, (score, job_hash))

        return cursor.rowcount > 0


# ==================================================
# ADD HR CONTACT
# ==================================================

def add_hr_contact(
    company,
    company_domain,
    hr_name,
    hr_email,
    source="pattern",
    verified=False
):

    with get_connection() as conn:

        cursor = conn.cursor()

        cursor.execute("""
            INSERT OR IGNORE INTO hr_contacts (
                company,
                company_domain,
                hr_name,
                hr_email,
                source,
                verified
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            company,
            company_domain,
            hr_name,
            hr_email,
            source,
            int(verified)
        ))

        return cursor.rowcount == 1


# ==================================================
# GET ALL HR CONTACTS
# ==================================================

def get_all_hr_contacts():

    with get_connection() as conn:

        cursor = conn.cursor()

        cursor.execute("SELECT * FROM hr_contacts")

        return [dict(row) for row in cursor.fetchall()]


# ==================================================
# SAVE DAILY STATISTICS
# ==================================================

def save_daily_stats(
    total_scraped,
    total_new,
    total_applied,
    total_emailed,
    total_failed,
    run_time_seconds
):

    today = date.today().isoformat()

    with get_connection() as conn:

        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO daily_stats (
                date,
                total_scraped,
                total_new,
                total_applied,
                total_emailed,
                total_failed,
                run_time_seconds
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)

            ON CONFLICT(date) DO UPDATE SET
                total_scraped = excluded.total_scraped,
                total_new = excluded.total_new,
                total_applied = excluded.total_applied,
                total_emailed = excluded.total_emailed,
                total_failed = excluded.total_failed,
                run_time_seconds = excluded.run_time_seconds
        """, (
            today,
            total_scraped,
            total_new,
            total_applied,
            total_emailed,
            total_failed,
            run_time_seconds
        ))


# ==================================================
# GET DAILY STATISTICS
# ==================================================

def get_daily_stats():

    with get_connection() as conn:

        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM daily_stats
            ORDER BY date DESC
        """)

        return [dict(row) for row in cursor.fetchall()]


# ==================================================
# ADD HR DRIP CONTACT
# ==================================================

def add_drip_contact(
    email,
    name=None,
    company=None,
    designation=None
):

    with get_connection() as conn:

        cursor = conn.cursor()

        cursor.execute("""
            INSERT OR IGNORE INTO drip_outreach (
                email,
                name,
                company,
                designation
            )
            VALUES (?, ?, ?, ?)
        """, (email, name, company, designation))

        return cursor.rowcount == 1


# ==================================================
# GET PENDING DRIP CONTACTS
# ==================================================

def get_pending_drip_contacts():

    with get_connection() as conn:

        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM drip_outreach
            WHERE status = 'pending'
        """)

        return [dict(row) for row in cursor.fetchall()]


# ==================================================
# MARK DRIP EMAIL AS SENT
# ==================================================

def mark_drip_email_sent(email):

    with get_connection() as conn:

        cursor = conn.cursor()

        cursor.execute("""
            UPDATE drip_outreach
            SET status = 'sent',
                sent_date = ?
            WHERE email = ?
              AND status = 'pending'
        """, (
            datetime.now().isoformat(timespec="seconds"),
            email
        ))

        return cursor.rowcount > 0


# ==================================================
# GET DATABASE SUMMARY
# ==================================================

def get_database_summary():

    with get_connection() as conn:

        cursor = conn.cursor()

        cursor.execute("""
            SELECT COUNT(*) AS total_jobs
            FROM applications
        """)

        total_jobs = cursor.fetchone()["total_jobs"]

        cursor.execute("""
            SELECT COUNT(*) AS total_contacts
            FROM hr_contacts
        """)

        total_contacts = cursor.fetchone()["total_contacts"]

        cursor.execute("""
            SELECT COUNT(*) AS total_drips
            FROM drip_outreach
        """)

        total_drips = cursor.fetchone()["total_drips"]

        return {
            "total_jobs": total_jobs,
            "total_hr_contacts": total_contacts,
            "total_drip_contacts": total_drips
        }


# ==================================================
# MAIN
# ==================================================

if __name__ == "__main__":
    init_db()
