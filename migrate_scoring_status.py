
import json
import sqlite3

from database.db_manager import DB_PATH, init_db


def migrate_scoring_results():

    report_path = "reports/job_scores.json"

    # Ensure database schema is initialized
    init_db()

    # Load previous Gemini scoring results
    with open(report_path, "r", encoding="utf-8") as file:
        results = json.load(file)

    if not isinstance(results, list):
        raise ValueError("Invalid scoring report format")

    connection = sqlite3.connect(DB_PATH)

    updated = 0
    missing = 0

    try:

        for item in results:

            job_hash = item.get("job_hash")
            score = item.get("score")

            if not job_hash or score is None:
                continue

            if not isinstance(score, (int, float)) or not 0 <= score <= 10:
                raise ValueError(
                    f"Invalid score for job {job_hash}: {score}"
                )

            cursor = connection.execute("""
                UPDATE applications
                SET relevance_score = ?,
                    scoring_status = 'completed'
                WHERE job_hash = ?
            """, (score, job_hash))

            if cursor.rowcount > 0:
                updated += 1
            else:
                missing += 1

        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()

    print("\nSCORING MIGRATION SUMMARY")
    print("=" * 40)
    print("Results in JSON report:", len(results))
    print("Existing jobs migrated:", updated)
    print("Jobs not found:", missing)
    print("Migration completed successfully!")


if __name__ == "__main__":
    migrate_scoring_results()
