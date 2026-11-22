
import sqlite3

from database.db_manager import DB_PATH
from config.logging_config import logger


def score_node(state):

    logger.info("Score Node started.")

    print("\n[SCORE NODE]")
    print("=" * 45)

    connection = None

    try:
        connection = sqlite3.connect(DB_PATH)
        cursor = connection.cursor()

        cursor.execute("""
            SELECT COUNT(*)
            FROM applications
            WHERE status = 'eligible'
              AND relevance_score >= 6
        """)

        selected = cursor.fetchone()[0]

        messages = list(state.get("messages", []))
        messages.append("Existing relevance scores checked.")

        print("Jobs with score >= 6:", selected)
        print("Gemini API call skipped; cached scores reused.")

        logger.info("Jobs with score >= 6: %s", selected)
        logger.info("Gemini API call skipped; cached scores reused.")
        logger.info("Score Node completed successfully.")

        return {
            "jobs_scored": selected,
            "scoring_skipped": True,
            "messages": messages
        }

    except Exception:
        logger.exception("Score Node failed.")
        raise

    finally:
        if connection:
            connection.close()


if __name__ == "__main__":
    print(score_node({}))
