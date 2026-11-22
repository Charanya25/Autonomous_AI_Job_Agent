
import json
import os
import time
import sqlite3
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types

from database.db_manager import DB_PATH, update_job_score


# ==========================================
# 1. CONFIGURATION
# ==========================================

BASE_DIR = Path(__file__).resolve().parent

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

MODEL = "gemini-3.5-flash-lite"

BATCH_SIZE = 5
MAX_RETRIES = 2
MINIMUM_SCORE = 6.0

REPORT_PATH = BASE_DIR / "reports" / "job_scores.json"

if not API_KEY:
    raise ValueError("Gemini API key not found in .env")

client = genai.Client(api_key=API_KEY)


# ==========================================
# 2. CUSTOM ERRORS
# ==========================================

class QuotaExceededError(Exception):
    pass


class ServiceUnavailableError(Exception):
    pass


# ==========================================
# 3. GET PENDING ELIGIBLE JOBS
# ==========================================

def get_eligible_jobs():

    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row

    try:

        cursor = connection.cursor()

        cursor.execute("""
            SELECT job_hash, job_title, company,
                   location, portal, job_description
            FROM applications
            WHERE status = 'eligible'
            AND scoring_status = 'pending'
            ORDER BY id DESC
        """)

        return [dict(row) for row in cursor.fetchall()]

    finally:
        connection.close()


# ==========================================
# 4. LOAD EXISTING SCORING RESULTS
# ==========================================

def load_existing_results():

    if not REPORT_PATH.exists():
        return []

    try:

        with open(REPORT_PATH, "r", encoding="utf-8") as file:
            results = json.load(file)

        if not isinstance(results, list):
            print("Existing report format invalid. Starting fresh.")
            return []

        return results

    except (json.JSONDecodeError, OSError) as error:

        print("Could not load previous report:", error)
        return []


# ==========================================
# 5. GEMINI BATCH SCORING
# ==========================================

def score_batch(jobs):

    job_details = []

    for job in jobs:

        job_details.append({
            "job_hash": job["job_hash"],
            "title": job["job_title"],
            "company": job["company"],
            "location": job["location"],
            "description": (job["job_description"] or "")[:2500]
        })

    prompt = f"""
You are an AI job evaluator.

Candidate:
B.Tech Computer Science and Engineering,
Data Science specialization.
Experience: Fresher / entry-level.

Skills:
Python, SQL, Pandas, PySpark, Machine Learning,
Data Science, Flask, FastAPI, HTML, CSS and basic Java.

Career interests:
Python Developer, Data Analyst, Data Scientist,
Data Engineer, AI Engineer, ML Engineer and
entry-level Software Developer.

Evaluate each job based only on the supplied information.

Scoring:
- Score from 0 to 10.
- Consider technical skill match.
- Consider fresher suitability.
- Prefer junior and entry-level roles.
- Give low scores to senior or unrelated roles.
- Do not invent job requirements.

Return valid JSON:

{{
  "results": [
    {{
      "job_hash": "provided job hash",
      "score": 8,
      "reason": "Short explanation"
    }}
  ]
}}

Jobs:
{json.dumps(job_details)}
"""

    for attempt in range(MAX_RETRIES):

        try:

            response = client.models.generate_content(
                model=MODEL,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )

            if not response.text:
                raise ValueError("Empty Gemini response")

            result = json.loads(response.text)

            if not isinstance(result.get("results"), list):
                raise ValueError("Invalid JSON response structure")

            return result

        except Exception as error:

            error_text = str(error).lower()

            print(
                f"Gemini attempt {attempt + 1} failed: {error}"
            )

            if (
                "429" in error_text
                or "resource_exhausted" in error_text
                or "quota" in error_text
            ):
                raise QuotaExceededError(str(error))

            if "503" in error_text or "unavailable" in error_text:

                if attempt == MAX_RETRIES - 1:
                    raise ServiceUnavailableError(str(error))

            elif attempt == MAX_RETRIES - 1:
                raise

            wait_time = 10 * (attempt + 1)

            print(f"Retrying in {wait_time} seconds...")
            time.sleep(wait_time)


# ==========================================
# 6. PROCESS SCORING RESULTS
# ==========================================

def save_batch_results(result, batch):

    batch_hashes = {
        job["job_hash"] for job in batch
    }

    saved_results = []
    returned_hashes = set()

    for item in result["results"]:

        job_hash = item.get("job_hash")

        if job_hash not in batch_hashes:
            continue

        if job_hash in returned_hashes:
            continue

        try:

            score = float(item["score"])

            if not 0 <= score <= 10:
                print("Invalid score skipped:", score)
                continue

            reason = str(
                item.get("reason", "No explanation")
            )

            updated = update_job_score(job_hash, score)

            if not updated:
                print("Job not found in database:", job_hash)
                continue

            returned_hashes.add(job_hash)

            saved_results.append({
                "job_hash": job_hash,
                "score": score,
                "reason": reason
            })

            print(f"Saved score: {score} | {reason}")

        except (ValueError, TypeError, KeyError) as error:

            print("Invalid scoring result:", error)

    missing = batch_hashes - returned_hashes

    if missing:
        print("Jobs not successfully scored:", len(missing))

    return saved_results


# ==========================================
# 7. SAVE JSON REPORT
# ==========================================

def save_report(all_results):

    REPORT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    # Keep the latest result for each job hash
    unique_results = {}

    for item in all_results:
        unique_results[item["job_hash"]] = item

    with open(
        REPORT_PATH,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            list(unique_results.values()),
            file,
            indent=4,
            ensure_ascii=False
        )


# ==========================================
# 8. MAIN SCORING WORKFLOW
# ==========================================

def run_scoring():

    print("\n================================")
    print("AUTONOMOUS AI JOB AGENT")
    print("GEMINI AI JOB SCORING")
    print("================================")

    print("Model:", MODEL)

    jobs = get_eligible_jobs()

    print("Pending eligible jobs:", len(jobs))

    if not jobs:
        print("All eligible jobs have been scored.")
        return

    total_batches = (
        len(jobs) + BATCH_SIZE - 1
    ) // BATCH_SIZE

    # Preserve previous successful scoring results
    all_results = load_existing_results()

    existing_hashes = {
        item["job_hash"]
        for item in all_results
        if "job_hash" in item
    }

    print("Previous report entries:", len(all_results))

    failed_batches = 0
    stopped_early = False

    # Correct counter: counts only newly added results
    newly_scored_count = 0

    for start in range(0, len(jobs), BATCH_SIZE):

        batch = jobs[start:start + BATCH_SIZE]

        batch_number = start // BATCH_SIZE + 1

        print(
            f"\nBatch {batch_number}/{total_batches}"
            f" | Jobs: {len(batch)}"
        )

        try:

            result = score_batch(batch)

            saved = save_batch_results(result, batch)

            for item in saved:

                if item["job_hash"] not in existing_hashes:

                    all_results.append(item)

                    existing_hashes.add(item["job_hash"])

                    # Count only newly scored jobs
                    newly_scored_count += 1

                else:

                    # Update an existing report entry
                    for index, old_item in enumerate(all_results):

                        if old_item.get("job_hash") == item["job_hash"]:
                            all_results[index] = item
                            break

            # Save after every successful batch
            save_report(all_results)

        except QuotaExceededError as error:

            print("\nAPI QUOTA LIMIT REACHED.")
            print("Stopping scoring to protect your API quota.")
            print(error)

            stopped_early = True
            break

        except ServiceUnavailableError as error:

            print("\nGemini service remains unavailable.")
            print("Stopping remaining batches for now.")
            print(error)

            stopped_early = True
            break

        except Exception as error:

            failed_batches += 1

            print("Batch failed:", error)
            print("Continuing to next batch.")

        if start + BATCH_SIZE < len(jobs):
            time.sleep(3)

    # Save final report
    save_report(all_results)

    # ======================================
    # 9. FINAL SUMMARY
    # ======================================

    print("\n================================")
    print("SCORING SUMMARY")
    print("================================")

    print("Eligible jobs initially pending:", len(jobs))
    print("Newly scored in this run:", newly_scored_count)
    print("Pending jobs remaining:", len(get_eligible_jobs()))
    print("Failed batches:", failed_batches)
    print("Stopped early:", stopped_early)
    print("Report:", REPORT_PATH)

    print("\nTOP 10 SCORING JOBS")

    top_results = sorted(
        all_results,
        key=lambda item: item["score"],
        reverse=True
    )[:10]

    for item in top_results:

        print("\nJob hash:", item["job_hash"])
        print("Score:", item["score"])
        print("Reason:", item["reason"])


# ==========================================
# 10. HELPER FUNCTION
# ==========================================

def get_completed_hashes(results):

    return {
        item["job_hash"]
        for item in results
        if "job_hash" in item
    }


# ==========================================
# 11. MAIN
# ==========================================

if __name__ == "__main__":
    run_scoring()
