
import sqlite3

from database.db_manager import DB_PATH
from config.logging_config import logger


def hr_drip_node(state):

    logger.info("HR Drip Node started.")

    print("\n[HR DRIP NODE]")
    print("=" * 50)

    messages = list(state.get("messages", []))
    errors = list(state.get("errors", []))

    connection = None

    try:
        connection = sqlite3.connect(DB_PATH)
        cursor = connection.cursor()

        cursor.execute("""
            SELECT COUNT(*)
            FROM drip_outreach
            WHERE status = 'pending'
        """)

        pending_followups = cursor.fetchone()[0]

        logger.info(
            "Pending follow-ups found: %s",
            pending_followups
        )

        print("Pending follow-ups:", pending_followups)
        print("Email sending: Disabled")

        messages.append(
            "HR follow-up queue checked successfully."
        )

        logger.info("No follow-up emails were sent.")
        logger.info("HR Drip Node completed successfully.")

        return {
            "followups_queued": pending_followups,
            "emails_sent": 0,
            "messages": messages,
            "errors": errors
        }

    except Exception as error:

        logger.exception("HR Drip Node failed.")

        errors.append(
            f"HR Drip node failed: {error}"
        )

        return {
            "followups_queued": 0,
            "emails_sent": 0,
            "messages": messages,
            "errors": errors
        }

    finally:
        if connection:
            connection.close()


if __name__ == "__main__":
    result = hr_drip_node({})

    print("\nTest result:", result)
