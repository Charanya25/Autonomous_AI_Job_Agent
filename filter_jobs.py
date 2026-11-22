
import sqlite3
import re

from database.db_manager import DB_PATH


# ==========================================
# 1. PREFERRED JOB TITLES
# ==========================================

WHITELIST = [
    "python developer",
    "python engineer",
    "data analyst",
    "data scientist",
    "data engineer",
    "machine learning",
    "ml engineer",
    "ai engineer",
    "artificial intelligence",
    "software engineer",
    "software developer",
    "backend developer",
    "backend engineer",
    "sql developer",
    "business intelligence",
    "bi analyst",
    "data science",
    "analytics engineer",
    "pyspark",
    "nlp engineer",
    "computer vision"
]


# ==========================================
# 2. UNWANTED JOB CATEGORIES
# ==========================================

BLACKLIST = [
    "sales",
    "account executive",
    "business development",
    "recruiter",
    "recruitment",
    "talent acquisition",
    "marketing",
    "customer support",
    "travel booking",
    "call center",
    "bpo"
]


# ==========================================
# 3. SENIOR-LEVEL KEYWORDS
# ==========================================

SENIOR_KEYWORDS = [
    "senior",
    "sr.",
    "staff",
    "principal",
    "lead",
    "director",
    "manager",
    "head of",
    "vice president",
    "vp ",
    "architect"
]


# ==========================================
# 4. INDIA LOCATIONS
# ==========================================

INDIA_KEYWORDS = [
    "india",
    "hyderabad",
    "bangalore",
    "bengaluru",
    "chennai",
    "mumbai",
    "pune",
    "delhi",
    "new delhi",
    "gurgaon",
    "gurugram",
    "noida",
    "kolkata",
    "kochi",
    "cochin",
    "ahmedabad",
    "jaipur",
    "lucknow",
    "indore",
    "chandigarh",
    "visakhapatnam",
    "vizag",
    "coimbatore",
    "thiruvananthapuram",
    "telangana",
    "karnataka",
    "tamil nadu",
    "maharashtra",
    "uttar pradesh",
    "west bengal",
    "kerala"
]


# ==========================================
# 5. FOREIGN COUNTRIES AND CITIES
# ==========================================

FOREIGN_LOCATION_KEYWORDS = [
    "united states",
    "usa",
    "canada",
    "united kingdom",
    "uk",
    "germany",
    "france",
    "netherlands",
    "nederland",
    "ireland",
    "switzerland",
    "sweden",
    "norway",
    "denmark",
    "finland",
    "australia",
    "new zealand",
    "singapore",
    "japan",
    "south korea",
    "israel",
    "uae",
    "dubai",
    "brazil",
    "portugal",
    "bulgaria",
    "italy",
    "spain",
    "hungary",
    "poland",
    "mexico",
    "belfast",
    "london",
    "paris",
    "berlin",
    "munich",
    "amsterdam",
    "zurich",
    "zürich",
    "bordeaux",
    "hamburg",
    "helsinki",
    "cambridge",
    "toronto",
    "palo alto",
    "newcastle",
    "edinburgh",
    "glasgow",
    "leeds",
    "manchester",
    "birmingham",
    "bristol",
    "lausanne",
    "heidelberg",
    "dortmund",
    "aachen",
    "koblenz",
    "schiphol",
    "saint-denis",
    "woerden"
]


# ==========================================
# 6. LOCATION RESTRICTION PATTERNS
# ==========================================

RESTRICTION_PATTERNS = [
    r"\b(us|usa|united states)\s+only\b",
    r"\bcanada\s+only\b",
    r"\b(uk|united kingdom)\s+only\b",
    r"\b(europe|eu)\s+only\b",
    r"\bonly candidates based in\b",
    r"\bonly applicants based in\b",
    r"\bcandidates to be based in .{0,80} only\b",
    r"\bmust be based in\b",
    r"\bmust reside in\b",
    r"\bremote within (the )?(us|usa|united states|canada|uk|europe)\b",
    r"\bwork authorization required in (the )?(us|usa|united states|canada|uk)\b",
    r"\bno remote working available from any other country\b",
    r"\bremote candidates must be located in\b",
    r"\btimezone overlap required\b",
    r"\bwithin .{0,30} time ?zones?\b"
]


# ==========================================
# 7. WORLDWIDE REMOTE PATTERNS
# ==========================================

WORLDWIDE_REMOTE_PATTERNS = [
    r"\bremote worldwide\b",
    r"\bworldwide remote\b",
    r"\bwork from anywhere in the world\b",
    r"\bwork from anywhere\b",
    r"\bremote from anywhere\b",
    r"\banywhere in the world\b",
    r"\bopen to candidates worldwide\b",
    r"\bopen to applicants worldwide\b",
    r"\bopen to applicants in all countries\b",
    r"\bremote across all countries\b",
    r"\bglobal remote position\b"
]


# ==========================================
# 8. INDIA REMOTE PATTERNS
# ==========================================

INDIA_REMOTE_PATTERNS = [
    r"\bremote from india\b",
    r"\bremote within india\b",
    r"\bindia is an eligible location\b",
    r"\bapplicants based in india\b",
    r"\bcandidates based in india\b",
    r"\bindia-based applicants\b",
    r"\bindia-based candidates\b",
    r"\bhiring in india\b",
    r"\bopen to applicants in india\b",
    r"\bopen to candidates in india\b"
]


# ==========================================
# 9. REMOTE AND AMBIGUOUS LOCATIONS
# ==========================================

REMOTE_KEYWORDS = [
    "remote",
    "work from home",
    "work remotely",
    "distributed team",
    "werken op afstand"
]


AMBIGUOUS_LOCATIONS = [
    "",
    "not specified",
    "unknown",
    "headquarter",
    "anywhere",
    "global",
    "worldwide"
]


# ==========================================
# 10. HELPER FUNCTIONS
# ==========================================

def contains_location_keyword(text, keywords):

    for keyword in keywords:

        pattern = (
            r"(?<!\w)"
            + re.escape(keyword)
            + r"(?!\w)"
        )

        if re.search(pattern, text):
            return True

    return False


def contains_any_pattern(text, patterns):

    return any(
        re.search(pattern, text)
        for pattern in patterns
    )


def contains_title_keyword(title, keywords):

    for keyword in keywords:

        pattern = (
            r"(?<!\w)"
            + re.escape(keyword)
            + r"(?!\w)"
        )

        if re.search(pattern, title):
            return True

    return False


# ==========================================
# 11. LOCATION ELIGIBILITY
# ==========================================

def check_location_eligibility(job):

    location = (
        job["location"] or ""
    ).lower().strip()

    description = (
        job["job_description"] or ""
    ).lower()

    combined_text = location + " " + description

    # Reject explicit foreign-country restrictions.
    if contains_any_pattern(
        combined_text,
        RESTRICTION_PATTERNS
    ):

        return False, "Explicit foreign-country restriction"

    # Accept India-based locations.
    if contains_location_keyword(
        location,
        INDIA_KEYWORDS
    ):

        return True, "India-based opportunity"

    # Accept explicitly India-eligible remote jobs.
    if contains_any_pattern(
        description,
        INDIA_REMOTE_PATTERNS
    ):

        return True, "Explicit India remote eligibility"

    # Check for explicit worldwide remote eligibility.
    has_worldwide_remote = contains_any_pattern(
        description,
        WORLDWIDE_REMOTE_PATTERNS
    )

    remote_like_location = location in [
        "remote",
        "work from home",
        "anywhere in the world",
        "worldwide remote",
        "global remote"
    ]

    if (
        has_worldwide_remote
        and (
            remote_like_location
            or not location
        )
    ):

        return True, "Explicit worldwide remote opportunity"

    # Reject known foreign locations unless India eligibility
    # was explicitly confirmed above.
    if contains_location_keyword(
        location,
        FOREIGN_LOCATION_KEYWORDS
    ):

        return False, "Foreign location - India eligibility not confirmed"

    # APAC needs manual verification.
    if location in ["apac", "asia pacific"]:

        return True, "APAC opportunity - verify India eligibility"

    # Unknown locations need manual verification.
    if location in AMBIGUOUS_LOCATIONS:

        return True, "Location unclear - manual verification required"

    # Remote jobs without clear country eligibility need review.
    is_remote = any(
        keyword in combined_text
        for keyword in REMOTE_KEYWORDS
    )

    if is_remote:

        return True, "Remote opportunity - verify India eligibility"

    # Conservative default.
    return False, "Location outside India or not verified"


# ==========================================
# 12. JOB FILTERING
# ==========================================

def filter_job(job):

    title = (
        job["job_title"] or ""
    ).lower()

    description = (
        job["job_description"] or ""
    ).lower()

    # Reject senior roles.
    if contains_title_keyword(title, SENIOR_KEYWORDS):

        return False, "Senior-level role"

    # Reject unwanted categories.
    if contains_title_keyword(title, BLACKLIST):

        return False, "Unwanted job category"

    # Check location eligibility.
    location_allowed, location_reason = (
        check_location_eligibility(job)
    )

    if not location_allowed:

        return False, location_reason

    # Match preferred job titles.
    if contains_title_keyword(title, WHITELIST):

        return True, (
            location_reason
            + " | Matching job title"
        )

    # General technical roles.
    general_roles = [
        "developer",
        "engineer",
        "programmer"
    ]

    technical_skills = [
        "python",
        "sql",
        "pyspark",
        "machine learning"
    ]

    has_general_role = contains_title_keyword(
        title,
        general_roles
    )

    has_technical_skill = any(
        skill in description
        for skill in technical_skills
    )

    if has_general_role and has_technical_skill:

        return True, (
            location_reason
            + " | Technical skills match"
        )

    return False, "No matching job keywords"


# ==========================================
# 13. RUN FILTERING
# ==========================================

def run_filter():

    connection = sqlite3.connect(DB_PATH)

    connection.row_factory = sqlite3.Row

    try:

        cursor = connection.cursor()

        cursor.execute("""
            SELECT job_hash, job_title, company,
                   location, portal, job_description, notes
            FROM applications
            WHERE status = 'new'
        """)

        jobs = cursor.fetchall()

        eligible = 0
        manual_review = 0
        rejected = 0

        print("\n================================")
        print("AUTONOMOUS AI JOB AGENT")
        print("JOB FILTERING SYSTEM")
        print("================================")

        print("\nTotal new jobs:", len(jobs))

        for job in jobs:

            is_eligible, reason = filter_job(job)

            # Unclear location or remote eligibility
            # requires manual review.
            if is_eligible and any(
                marker in reason.lower()
                for marker in [
                    "manual verification",
                    "verify india eligibility"
                ]
            ):

                status = "manual_required"
                manual_review += 1

            elif is_eligible:

                status = "eligible"
                eligible += 1

            else:

                status = "filtered_out"
                rejected += 1

            # Preserve existing notes.
            old_notes = job["notes"] or ""

            if old_notes:
                updated_notes = old_notes + "\n" + reason
            else:
                updated_notes = reason

            cursor.execute("""
                UPDATE applications
                SET status = ?, notes = ?
                WHERE job_hash = ? AND status = 'new'
            """, (
                status,
                updated_notes,
                job["job_hash"]
            ))

        connection.commit()

        print("\nFILTERING COMPLETED!")

        print("Eligible jobs:", eligible)
        print("Manual review jobs:", manual_review)
        print("Rejected jobs:", rejected)

        print("\nDATABASE STATUS SUMMARY")

        cursor.execute("""
            SELECT status, COUNT(*)
            FROM applications
            GROUP BY status
        """)

        for status, count in cursor.fetchall():

            print(status, ":", count)

    except Exception:

        connection.rollback()
        raise

    finally:

        connection.close()


# ==========================================
# 14. MAIN
# ==========================================

if __name__ == "__main__":

    run_filter()
