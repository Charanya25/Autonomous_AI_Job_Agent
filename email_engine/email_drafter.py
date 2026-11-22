
import os
import re
import time
import sqlite3
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types

from database.db_manager import DB_PATH


# ==================================================
# CONFIGURATION
# ==================================================

load_dotenv()

MODEL_NAME = "gemini-3.8-flash"

MAX_RETRIES = 2
REQUEST_TIMEOUT_MS = 30000

MINIMUM_SCORE = 6.0
MAX_JOBS_PER_RUN = 10

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DRAFT_FOLDER = PROJECT_ROOT / "reports" / "email_drafts"


# ==================================================
# DATABASE
# ==================================================

def get_selected_jobs():

    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            job_hash,
            job_title,
            company,
            location,
            portal,
            job_url,
            job_description,
            relevance_score
        FROM applications
        WHERE status = 'manual_required'
          AND relevance_score >= ?
          AND LOWER(company) != 'abc technologies'
        ORDER BY relevance_score DESC
        LIMIT ?
    """, (MINIMUM_SCORE, MAX_JOBS_PER_RUN))

    jobs = [dict(row) for row in cursor.fetchall()]

    connection.close()

    return jobs


# ==================================================
# GEMINI PROMPT
# ==================================================

def build_prompt(job):

    return f"""
Write a professional job application email.

CANDIDATE:
Name: Sai Charanya Koneti
Degree: B.Tech CSE (Data Science)
College: Vignana Bharathi Institute of Technology
CGPA: 8.1

INTERNSHIP:
Data Engineering Intern at L&T Construction.

Technologies:
Python, APIs, Pandas, PySpark, Flask APIs,
Azure AI Foundry.

Skills:
Python, SQL, Pandas, PySpark, Flask and Java basics.

Career level: Fresher.

JOB:
Company: {job['company']}
Position: {job['job_title']}
Location: {job['location']}

Description:
{(job['job_description'] or 'Not provided')[:3000]}

Write:
- A suitable subject line.
- A polite greeting to the hiring team.
- A short candidate introduction.
- Relevant skills and internship experience.
- Interest in the specific position.
- A professional closing.

Keep the email between 120 and 180 words.

Do not invent experience, recruiter names or email addresses.
Do not claim a resume is attached.

Return only the subject and email body.
"""


# ==================================================
# GEMINI GENERATION WITH TIMEOUT
# ==================================================

def generate_gemini_email(client, job):

    prompt = build_prompt(job)

    for attempt in range(1, MAX_RETRIES + 1):

        try:

            print(
                f"Gemini attempt {attempt}/{MAX_RETRIES}"
            )

            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt,
                config=types.GenerateContentConfig(
                    http_options=types.HttpOptions(
                        timeout=REQUEST_TIMEOUT_MS
                    )
                )
            )

            if not response.text:
                raise ValueError(
                    "Gemini returned an empty response."
                )

            return response.text.strip()

        except Exception as error:

            message = str(error).upper()

            print("Gemini error:", error)

            # Do not retry exhausted daily quotas.
            if (
                "429" in message
                or "RESOURCE_EXHAUSTED" in message
            ):
                print("Quota/rate limit detected.")
                raise

            temporary_error = any(
                term in message
                for term in [
                    "503",
                    "UNAVAILABLE",
                    "500",
                    "INTERNAL",
                    "TIMEOUT",
                    "10060",
                    "CONNECTION",
                    "DEADLINE"
                ]
            )

            if temporary_error and attempt < MAX_RETRIES:

                print("Temporary error. Retrying once in 5 seconds.")

                time.sleep(5)

            else:
                raise

    raise RuntimeError("Gemini generation failed.")


# ==================================================
# LOCAL FALLBACK GENERATOR
# ==================================================

def generate_fallback_email(job):

    company = job["company"]
    title = job["job_title"]

    description = (
        job["job_description"] or ""
    ).lower()

    skill_keywords = [
        ("python", "Python"),
        ("sql", "SQL"),
        ("pyspark", "PySpark"),
        ("pandas", "Pandas"),
        ("machine learning", "Machine Learning"),
        ("data analysis", "Data Analysis"),
        ("flask", "Flask")
    ]

    relevant_skills = [
        skill
        for keyword, skill in skill_keywords
        if keyword in description
    ]

    if not relevant_skills:
        relevant_skills = ["Python", "SQL", "Pandas"]

    skills = ", ".join(relevant_skills)

    return f"""
Subject: Application for {title} - Fresher Candidate

Dear Hiring Team,

I am writing to express my interest in the {title}
position at {company}.

I am a B.Tech graduate in Computer Science and
Engineering (Data Science) from Vignana Bharathi
Institute of Technology, with a CGPA of 8.1.

I completed a Data Engineering internship at
L&T Construction, where I gained practical exposure
to Python, APIs, Pandas, PySpark, Flask APIs and
Azure AI Foundry.

My technical skills include {skills}. I am eager
to apply my knowledge, learn from experienced
professionals and contribute to your team.

As a fresher, I would appreciate an opportunity
to discuss how my skills and internship experience
could be relevant to this position.

Thank you for your time and consideration.

Best regards,
Sai Charanya Koneti
B.Tech CSE (Data Science)
""".strip()


# ==================================================
# FILE NAME
# ==================================================

def create_filename(company, job_title):

    filename = f"{company}_{job_title}"

    filename = re.sub(
        r"[^a-zA-Z0-9_-]",
        "_",
        filename
    )

    return filename[:120] + ".txt"


# ==================================================
# SAVE DRAFT
# ==================================================

def save_draft(job, draft, method):

    DRAFT_FOLDER.mkdir(
        parents=True,
        exist_ok=True
    )

    filename = create_filename(
        job["company"],
        job["job_title"]
    )

    filepath = DRAFT_FOLDER / filename

    with open(
        filepath,
        "w",
        encoding="utf-8"
    ) as file:

        file.write("AI JOB APPLICATION EMAIL DRAFT\n")
        file.write("=" * 55 + "\n\n")

        file.write(f"Company: {job['company']}\n")
        file.write(f"Position: {job['job_title']}\n")
        file.write(f"Location: {job['location']}\n")
        file.write(f"Score: {job['relevance_score']}\n")
        file.write(f"Job URL: {job['job_url']}\n")
        file.write(f"Generated using: {method}\n")

        file.write("\n" + "=" * 55 + "\n\n")

        file.write(draft)

        file.write("\n\nSTATUS: DRAFT ONLY\n")
        file.write("EMAIL SENT: NO\n")
        file.write("REVIEW REQUIRED: YES\n")

    return filepath


# ==================================================
# MAIN
# ==================================================

def run_email_drafter():

    print("\nAI PERSONALIZED EMAIL DRAFTER")
    print("=" * 55)

    api_key = os.getenv("GEMINI_API_KEY")

    client = None

    if api_key:

        try:

            client = genai.Client(
                api_key=api_key
            )

            print("Gemini client initialized.")

        except Exception as error:

            print("Gemini initialization failed:", error)

    else:

        print("Gemini API key not found.")
        print("Local fallback will be used.")

    jobs = get_selected_jobs()

    if not jobs:

        print("No suitable jobs found.")
        return

    print("Jobs selected:", len(jobs))
    print("Request timeout:", REQUEST_TIMEOUT_MS, "ms")
    print("Maximum Gemini attempts:", MAX_RETRIES)
    print("Fallback: Enabled")
    print("Emails will NOT be sent.")

    gemini_count = 0
    fallback_count = 0
    failed_count = 0

    for number, job in enumerate(jobs, start=1):

        print("\n" + "=" * 55)

        print(
            f"Processing job {number}/{len(jobs)}"
        )

        print("Company:", job["company"])
        print("Position:", job["job_title"])

        draft = None
        method = None

        if client is not None:

            try:

                draft = generate_gemini_email(
                    client,
                    job
                )

                method = "Gemini AI"

            except Exception as error:

                print("Gemini unavailable:", error)

        if draft is None:

            print("Switching to local fallback.")

            try:

                draft = generate_fallback_email(job)

                method = "Local Python Template"

            except Exception as error:

                print("Fallback failed:", error)
                failed_count += 1
                continue

        try:

            filepath = save_draft(
                job,
                draft,
                method
            )

            print("Draft saved successfully.")
            print("Method:", method)
            print("File:", filepath)

            if method == "Gemini AI":
                gemini_count += 1
            else:
                fallback_count += 1

        except Exception as error:

            print("File saving failed:", error)
            failed_count += 1

    # ==================================================
    # SUMMARY
    # ==================================================

    print("\n" + "=" * 55)

    print("EMAIL DRAFTING COMPLETED")

    print("Total jobs:", len(jobs))
    print("Gemini drafts:", gemini_count)
    print("Fallback drafts:", fallback_count)
    print("Failed:", failed_count)

    print("\nDraft location:")
    print(DRAFT_FOLDER)

    print("\nEmails sent: 0")
    print("Manual review required for every draft.")


if __name__ == "__main__":
    run_email_drafter()
