
from agent.application_engine import run_application_engine
from config.logging_config import logger


def apply_node(state):

    logger.info("Apply Node started.")

    print("\n[APPLY NODE - DRY RUN]")
    print("=" * 45)

    messages = list(state.get("messages", []))
    errors = list(state.get("errors", []))

    # Safety protection
    if not state.get("dry_run", True):

        message = "Live applications are disabled in this workflow."

        print(message)
        logger.warning(message)

        errors.append(message)

        return {
            "applications_submitted": 0,
            "manual_review_jobs": 0,
            "errors": errors,
            "messages": messages
        }

    try:
        print("Dry-run mode enabled.")
        print("No applications will be submitted.")

        logger.info("Dry-run mode enabled.")
        logger.info("Live application submission is disabled.")

        run_application_engine()

        messages.append(
            "Application review completed in dry-run mode."
        )

        logger.info("Application review completed successfully.")
        logger.info("Applications submitted: 0")

        return {
            "applications_submitted": 0,
            "manual_review_jobs": state.get("jobs_scored", 0),
            "messages": messages,
            "errors": errors
        }

    except Exception as error:

        logger.exception("Apply Node failed.")

        errors.append(f"Application review failed: {error}")

        return {
            "applications_submitted": 0,
            "manual_review_jobs": 0,
            "messages": messages,
            "errors": errors
        }


if __name__ == "__main__":

    result = apply_node({"dry_run": True})

    print("\nTest result:", result)
