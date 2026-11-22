
import sqlite3

from database.db_manager import DB_PATH
from filter_jobs import check_location_eligibility


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


def main():

    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row

    try:
        jobs = connection.execute("""
            SELECT id, location, job_description,
                   relevance_score, scoring_status, notes
            FROM applications
            WHERE status = 'eligible'
            ORDER BY id
        """).fetchall()

        if len(jobs) != 113:
            raise RuntimeError(
                f"Expected 113 eligible jobs, found {len(jobs)}. "
                "No changes applied."
            )

        decisions = {}

        for job in jobs:

            job_id = job["id"]

            if job_id in KEEP_ELIGIBLE:
                status = "eligible"
                reason = KEEP_ELIGIBLE[job_id]

            elif job_id in MANUAL_REVIEW:
                status = "manual_required"
                reason = MANUAL_REVIEW[job_id]

            elif job_id in REJECT:
                status = "filtered_out"
                reason = REJECT[job_id]

            else:
                is_eligible, location_reason = check_location_eligibility({
                    "location": job["location"] or "",
                    "job_description": job["job_description"] or ""
                })

                if is_eligible:
                    status = "manual_required"
                    reason = location_reason
                else:
                    status = "filtered_out"
                    reason = location_reason

            decisions[job_id] = {
                "status": status,
                "reason": reason,
                "old_notes": job["notes"] or "",
                "score": job["relevance_score"],
                "scoring_status": job["scoring_status"]
            }

        counts = {
            "eligible": 0,
            "manual_required": 0,
            "filtered_out": 0
        }

        for item in decisions.values():
            counts[item["status"]] += 1

        expected = {
            "eligible": 1,
            "manual_required": 4,
            "filtered_out": 108
        }

        if counts != expected:
            raise RuntimeError(
                f"Preview mismatch. Expected {expected}, got {counts}. "
                "No changes applied."
            )

        print("\nREADY TO UPDATE DATABASE")
        print("=" * 45)
        print("Eligible:", counts["eligible"])
        print("Manual review:", counts["manual_required"])
        print("Filtered out:", counts["filtered_out"])
        print("\nGemini scores and scoring statuses will be preserved.")

        confirmation = input(
            "\nType APPLY to confirm these changes: "
        ).strip()

        if confirmation != "APPLY":
            print("\nCancelled. No changes applied.")
            return

        connection.execute("BEGIN")

        for job_id, item in decisions.items():

            new_note = (
                item["old_notes"]
                + ("\n" if item["old_notes"] else "")
                + "Reclassification: "
                + item["reason"]
            )

            connection.execute("""
                UPDATE applications
                SET status = ?, notes = ?
                WHERE id = ? AND status = 'eligible'
            """, (
                item["status"],
                new_note,
                job_id
            ))

        # Verify every updated record and its original scoring data.
        for job in jobs:

            current = connection.execute("""
                SELECT status, relevance_score, scoring_status
                FROM applications
                WHERE id = ?
            """, (job["id"],)).fetchone()

            original = decisions[job["id"]]

            if (
                current["status"] != original["status"]
                or current["relevance_score"] != original["score"]
                or current["scoring_status"] != original["scoring_status"]
            ):
                raise RuntimeError(
                    f"Verification failed for job ID {job['id']}"
                )

        connection.commit()

        print("\nRECLASSIFICATION SUCCESSFUL")
        print("=" * 45)
        print("Eligible:", counts["eligible"])
        print("Manual review:", counts["manual_required"])
        print("Filtered out:", counts["filtered_out"])
        print("Gemini scores: Preserved")
        print("Scoring statuses: Preserved")
        print("Database transaction: Committed")

    except Exception as error:
        connection.rollback()
        print("\nERROR:", error)
        print("Database changes rolled back.")

    finally:
        connection.close()


if __name__ == "__main__":
    main()
