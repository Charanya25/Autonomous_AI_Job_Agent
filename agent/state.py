
from typing import TypedDict, List, Dict, Any


class JobAgentState(TypedDict, total=False):
    # Workflow settings
    dry_run: bool
    run_id: str

    # Job collection
    jobs_before: int
    jobs_scraped: int
    new_jobs: int

    # Filtering
    eligible_jobs: int
    filtered_jobs: int

    # Scoring
    jobs_scored: int
    scoring_skipped: bool

    # Application review
    selected_jobs: int
    applications_submitted: int
    manual_review_jobs: int

    # Email processing
    drafts_created: int
    emails_sent: int

    # HR follow-up
    followups_queued: int

    # Database and reporting
    database_summary: Dict[str, Any]
    errors: List[str]
    messages: List[str]
    final_report: str
