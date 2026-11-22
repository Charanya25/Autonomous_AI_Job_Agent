
import argparse
import time

from agent.graph import build_graph
from config.logging_config import logger


def run_workflow(dry_run=True):

    start_time = time.time()

    logger.info("=" * 55)
    logger.info("AUTONOMOUS AI JOB APPLICATION AGENT")
    logger.info("=" * 55)

    logger.info("Dry-run mode: %s", dry_run)

    try:

        app = build_graph()

        initial_state = {
            "dry_run": True,
            "messages": [],
            "errors": []
        }

        logger.info("Executing LangGraph workflow...")

        result = app.invoke(initial_state)

        logger.info("LangGraph workflow completed successfully.")

        logger.info("=" * 55)
        logger.info("WORKFLOW COMPLETED")
        logger.info("=" * 55)

        logger.info("FINAL REPORT:")
        logger.info(result.get("final_report", "Report unavailable."))

        logger.info("MESSAGES:")

        for message in result.get("messages", []):
            logger.info(message)

        logger.info("ERRORS:")

        for error in result.get("errors", []):
            logger.error(error)

        elapsed_time = round(time.time() - start_time, 2)

        logger.info("Total execution time: %s seconds", elapsed_time)

        return result

    except Exception:

        logger.exception("Workflow failed due to an unexpected error.")

        raise


def start_scheduler():

    from apscheduler.schedulers.blocking import BlockingScheduler

    scheduler = BlockingScheduler()

    logger.info("Starting APScheduler.")

    scheduler.add_job(
        run_workflow,
        trigger="interval",
        hours=24,
        kwargs={"dry_run": True},
        id="daily_job_agent",
        replace_existing=True,
        max_instances=1
    )

    logger.info("Daily workflow scheduled every 24 hours.")
    logger.info("Automatic applications: DISABLED.")
    logger.info("Automatic email sending: DISABLED.")

    try:
        scheduler.start()

    except (KeyboardInterrupt, SystemExit):

        logger.info("Scheduler stopped by user.")

        scheduler.shutdown()


def main():

    parser = argparse.ArgumentParser(
        description="Autonomous AI Job Application Agent"
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run workflow safely without submitting applications or sending emails."
    )

    parser.add_argument(
        "--run-now",
        action="store_true",
        help="Execute the workflow immediately."
    )

    parser.add_argument(
        "--schedule",
        action="store_true",
        help="Start the daily automated scheduler."
    )

    args = parser.parse_args()

    if args.schedule:

        start_scheduler()

    elif args.run_now:

        run_workflow(dry_run=True)

    else:

        # Safe default: dry-run mode
        run_workflow(dry_run=True)


if __name__ == "__main__":

    main()
