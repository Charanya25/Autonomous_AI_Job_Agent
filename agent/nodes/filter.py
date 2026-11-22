
import sqlite3

from database.db_manager import DB_PATH
from filter_jobs import run_filter
from config.logging_config import logger


def filter_node(state):

    logger.info("Filter Node started.")

    print("\n[FILTER NODE]")
    print("=" * 45)

    connection = None

    try:
        # Run the existing keyword-based filtering system
        run_filter()

        # Read the updated job counts
        connection = sqlite3.connect(DB_PATH)
        cursor = connection.cursor()

        cursor.execute("""
            SELECT status, COUNT(*)
            FROM applications
            GROUP BY status
        """)

        summary = dict(cursor.fetchall())

        eligible = summary.get("eligible", 0)
        filtered = summary.get("filtered_out", 0)

        print("\nFiltering completed.")
        print("Eligible jobs:", eligible)
        print("Filtered-out jobs:", filtered)

        # Record results in the log file
        logger.info("Filtering completed successfully.")
        logger.info("Eligible jobs: %s", eligible)
        logger.info("Filtered-out jobs: %s", filtered)
        logger.info("Database status summary: %s", summary)

        messages = list(state.get("messages", []))
        messages.append("Job filtering completed.")

        return {
            "eligible_jobs": eligible,
            "filtered_jobs": filtered,
            "database_summary": summary,
            "messages": messages
        }

    except Exception as error:

        error_message = f"Filtering failed: {str(error)}"

        logger.exception("Filter Node failed.")

        print(error_message)

        errors = list(state.get("errors", []))
        errors.append(error_message)

        return {
            "errors": errors,
            "messages": list(state.get("messages", []))
        }

    finally:
        if connection:
            connection.close()


if __name__ == "__main__":
    result = filter_node({})
    print("\nFilter node test completed.")
