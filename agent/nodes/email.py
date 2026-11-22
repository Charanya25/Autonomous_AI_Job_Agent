
from email_engine.email_drafter import (
    get_selected_jobs,
    generate_fallback_email,
    save_draft
)

from config.logging_config import logger


def email_node(state):

    logger.info("Email Node started.")

    print("\n[EMAIL NODE - LOCAL FALLBACK]")
    print("=" * 50)

    messages = list(state.get("messages", []))
    errors = list(state.get("errors", []))

    try:
        jobs = get_selected_jobs()

        print("Jobs selected:", len(jobs))
        print("Gemini API: Disabled")
        print("Email sending: Disabled")

        logger.info("Jobs selected for email drafts: %s", len(jobs))
        logger.info("Gemini API disabled in Email Node.")
        logger.info("Actual email sending disabled.")

        drafts_created = 0

        for job in jobs:
            try:
                draft = generate_fallback_email(job)

                save_draft(
                    job,
                    draft,
                    "Local Python Template"
                )

                drafts_created += 1

                print(
                    "Draft created:",
                    job["company"],
                    "-",
                    job["job_title"]
                )

                logger.info(
                    "Email draft created: %s - %s",
                    job["company"],
                    job["job_title"]
                )

            except Exception as error:

                message = (
                    f"Draft failed for {job['company']}: {error}"
                )

                print(message)
                logger.exception(
                    "Email draft creation failed for %s",
                    job.get("company", "Unknown company")
                )

                errors.append(message)

        messages.append("Local email drafting completed.")

        print("\nDrafts created:", drafts_created)
        print("Emails sent: 0")

        logger.info("Total email drafts created: %s", drafts_created)
        logger.info("Emails sent: 0")
        logger.info("Email Node completed successfully.")

        return {
            "drafts_created": drafts_created,
            "emails_sent": 0,
            "messages": messages,
            "errors": errors
        }

    except Exception as error:

        logger.exception("Email Node failed.")

        errors.append(f"Email node failed: {error}")

        return {
            "drafts_created": 0,
            "emails_sent": 0,
            "messages": messages,
            "errors": errors
        }


if __name__ == "__main__":
    result = email_node({})
    print("\nTest result:", result)
