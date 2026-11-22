
import sqlite3

from database.db_manager import DB_PATH
from config.logging_config import logger


def load_memory(state):

    logger.info("Load Memory Node started.")

    print("\n[LOAD MEMORY NODE]")
    print("=" * 45)

    connection = None

    try:
        connection = sqlite3.connect(DB_PATH)
        cursor = connection.cursor()

        # Get total saved jobs
        cursor.execute("""
            SELECT COUNT(*)
            FROM applications
        """)
        total_jobs = cursor.fetchone()[0]

        # Get job status summary
        cursor.execute("""
            SELECT status, COUNT(*)
            FROM applications
            GROUP BY status
        """)
        status_summary = dict(cursor.fetchall())

        # Get recent application records
        cursor.execute("""
            SELECT job_title, company, status, relevance_score
            FROM applications
            ORDER BY created_at DESC
            LIMIT 5
        """)
        recent_jobs = cursor.fetchall()

        print("Total saved jobs:", total_jobs)
        print("Job status summary:", status_summary)

        print("\nRecent jobs:")
        for job in recent_jobs:
            print(
                f"{job[0]} | {job[1]} | "
                f"{job[2]} | Score: {job[3]}"
            )

        messages = list(state.get("messages", []))
        messages.append(
            "Existing database memory loaded successfully."
        )

        logger.info("Total saved jobs: %s", total_jobs)
        logger.info("Job status summary: %s", status_summary)
        logger.info("Recent job records loaded: %s", len(recent_jobs))
        logger.info("Load Memory Node completed successfully.")

        return {
            "jobs_before": total_jobs,
            "database_summary": status_summary,
            "messages": messages
        }

    except Exception:
        logger.exception("Load Memory Node failed.")
        raise

    finally:
        if connection:
            connection.close()


if __name__ == "__main__":
    result = load_memory({})
    print("\nNode test completed.")
