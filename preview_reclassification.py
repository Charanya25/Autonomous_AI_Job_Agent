
import sqlite3
from collections import Counter

from database.db_manager import DB_PATH
from filter_jobs import check_location_eligibility


# Jobs manually reviewed in our previous steps.
# These decisions are only proposed classifications.

KEEP_ELIGIBLE = {
    5: "Globally remote opportunity - Supabase"
}

MANUAL_REVIEW = {
    11: "Addepto - confirm India eligibility",
    26: "Toptal - worldwide task-based freelance opportunity",
    1099: "NIKI Digital Engineering - confirm location",
    1782: "Canonical - confirm India eligibility"
}

REJECT = {
    6: "Remote restricted to Singapore or US Pacific",
    24: "Requires 4+ years and technical leadership",
    30: "Application deadline has passed",
    35: "Europe-only remote position",
    50: "Security clearance and experience requirements",
    1130: "Experienced task-based freelance work",
    1132: "Only Italy or Spain",
    1367: "Hybrid role requiring advanced experience",
    1418: "Remote UK position",
    1582: "Netherlands-based on-site role",
    1696: "Fluent Japanese required",
    1776: "EMEA-only position",
    1787: "Europe-based position",
    2050: "Netherlands-based role requiring substantial experience"
}


def preview_reclassification():

    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row

    jobs = connection.execute("""
        SELECT
            id,
            job_title,
            company,
            location,
            relevance_score,
            scoring_status,
            job_description
        FROM applications
        WHERE status = 'eligible'
        ORDER BY id
    """).fetchall()

    proposed = []

    for job in jobs:

        job_id = job["id"]

        if job_id in KEEP_ELIGIBLE:
            new_status = "eligible"
            reason = KEEP_ELIGIBLE[job_id]

        elif job_id in MANUAL_REVIEW:
            new_status = "manual_required"
            reason = MANUAL_REVIEW[job_id]

        elif job_id in REJECT:
            new_status = "filtered_out"
            reason = REJECT[job_id]

        else:
            is_eligible, location_reason = check_location_eligibility({
                "location": job["location"] or "",
                "job_description": job["job_description"] or ""
            })

            if is_eligible:
                new_status = "manual_required"
                reason = location_reason
            else:
                new_status = "filtered_out"
                reason = location_reason

        proposed.append({
            "id": job_id,
            "company": job["company"],
            "title": job["job_title"],
            "location": job["location"],
            "old_status": "eligible",
            "proposed_status": new_status,
            "reason": reason,
            "score": job["relevance_score"],
            "scoring_status": job["scoring_status"]
        })

    connection.close()

    print("\nRECLASSIFICATION PREVIEW")
    print("=" * 65)

    counts = Counter(
        item["proposed_status"] for item in proposed
    )

    print("Total existing eligible jobs:", len(proposed))
    print("Remain eligible:", counts["eligible"])
    print("Require manual review:", counts["manual_required"])
    print("Proposed rejection:", counts["filtered_out"])

    for status in ("eligible", "manual_required", "filtered_out"):

        print("\n" + "=" * 65)
        print("PROPOSED STATUS:", status.upper())
        print("=" * 65)

        for item in proposed:

            if item["proposed_status"] == status:

                print(
                    f'\nID: {item["id"]}'
                    f'\nCompany: {item["company"]}'
                    f'\nTitle: {item["title"]}'
                    f'\nLocation: {item["location"]}'
                    f'\nReason: {item["reason"]}'
                    f'\nGemini score: {item["score"]}'
                    f'\nScoring status: {item["scoring_status"]}'
                )

    print("\nDATABASE CHECK")
    print("=" * 65)
    print("This was a READ-ONLY preview.")
    print("No job statuses or Gemini scores were modified.")


if __name__ == "__main__":
    preview_reclassification()
