
from run_all_scrapers import run_all_scrapers
from config.logging_config import logger


def scrape(state):

    logger.info("Scrape Node started.")

    print("\n[LANGGRAPH NODE: SCRAPE]")

    try:
        result = run_all_scrapers()

        jobs_scraped = result.get("jobs_scraped", 0)
        new_jobs = result.get("new_jobs", 0)

        logger.info("Multi-portal scraping completed.")
        logger.info("New unique jobs collected: %s", new_jobs)
        logger.info("Jobs scraped metric: %s", jobs_scraped)

        messages = list(state.get("messages", []))
        messages.append("Multi-portal scraping completed.")

        return {
            "jobs_scraped": jobs_scraped,
            "new_jobs": new_jobs,
            "messages": messages
        }

    except Exception as error:

        logger.exception("Scraping Node failed.")

        errors = list(state.get("errors", []))
        errors.append(f"Scraping node failed: {error}")

        return {
            "jobs_scraped": 0,
            "new_jobs": 0,
            "errors": errors
        }
