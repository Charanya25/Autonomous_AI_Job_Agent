
from database.db_manager import save_daily_stats
from config.logging_config import logger


def save_memory(state):

    logger.info("Save Memory Node started.")

    print("\n[LANGGRAPH NODE: SAVE MEMORY]")

    errors = list(state.get("errors", []))

    total_scraped = state.get("jobs_scraped", 0)
    total_new = state.get("new_jobs", 0)
    total_applied = state.get("applications_submitted", 0)
    total_emailed = state.get("emails_sent", 0)
    total_failed = len(errors)

    try:

        logger.info("Saving daily statistics to SQLite.")

        save_daily_stats(
            total_scraped=total_scraped,
            total_new=total_new,
            total_applied=total_applied,
            total_emailed=total_emailed,
            total_failed=total_failed,
            run_time_seconds=0
        )

        logger.info("Daily statistics saved successfully.")
        logger.info("New jobs: %s", total_new)
        logger.info("Applications submitted: %s", total_applied)
        logger.info("Emails sent: %s", total_emailed)
        logger.info("Errors: %s", total_failed)

        print("Daily statistics saved successfully.")
        print("New jobs:", total_new)
        print("Applications submitted:", total_applied)
        print("Emails sent:", total_emailed)
        print("Errors:", total_failed)

        messages = list(state.get("messages", []))
        messages.append("Daily statistics saved to SQLite.")

        return {
            "messages": messages
        }

    except Exception as error:

        logger.exception("Save Memory Node failed.")

        errors.append(f"Save memory failed: {error}")

        return {
            "errors": errors
        }


if __name__ == "__main__":

    result = save_memory({
        "jobs_scraped": 0,
        "new_jobs": 0,
        "applications_submitted": 0,
        "emails_sent": 0,
        "errors": [],
        "messages": []
    })

    print("\nTest result:", result)
