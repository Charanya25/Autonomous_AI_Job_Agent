
from config.logging_config import logger

from pathlib import Path
from datetime import datetime
from html import escape


BASE_DIR = Path(__file__).resolve().parent.parent.parent
REPORT_DIR = BASE_DIR / "reports"
HTML_REPORT_PATH = REPORT_DIR / "latest_report.html"


def generate_html_report(state, report):

    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    errors = state.get("errors", [])

    metrics = {
        "Jobs before scraping": state.get("jobs_before", 0),
        "New jobs collected": state.get("new_jobs", 0),
        "Eligible jobs": state.get("eligible_jobs", 0),
        "Filtered jobs": state.get("filtered_jobs", 0),
        "Jobs with score >= 6": state.get("jobs_scored", 0),
        "Application submissions": 0,
        "Manual review jobs": state.get("manual_review_jobs", 0),
        "Email drafts created": state.get("drafts_created", 0),
        "Emails sent": 0,
        "Pending follow-ups": state.get("followups_queued", 0),
        "Workflow errors": len(errors)
    }

    metric_cards = ""

    for label, value in metrics.items():

        metric_cards += f"""
        <div class="card">
            <h3>{escape(str(label))}</h3>
            <div class="number">{escape(str(value))}</div>
        </div>
        """

    error_html = ""

    if errors:
        for error in errors:
            error_html += f"<li>{escape(str(error))}</li>"
    else:
        error_html = "<li>No workflow errors recorded.</li>"

    timestamp = datetime.now().strftime("%d %B %Y, %I:%M:%S %p")

    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">

<title>Autonomous AI Job Agent - Run Report</title>

<style>

body {{
    font-family: Arial, sans-serif;
    background: #f1f5f9;
    margin: 0;
    color: #1e293b;
}}

header {{
    background: #172554;
    color: white;
    padding: 25px;
}}

main {{
    max-width: 1100px;
    margin: auto;
    padding: 25px;
}}

.cards {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(190px, 1fr));
    gap: 15px;
}}

.card {{
    background: white;
    padding: 20px;
    border-radius: 10px;
    box-shadow: 0 2px 8px #00000010;
}}

.card h3 {{
    font-size: 14px;
    color: #64748b;
}}

.number {{
    font-size: 28px;
    font-weight: bold;
    color: #1d4ed8;
}}

.panel {{
    background: white;
    padding: 22px;
    margin-top: 22px;
    border-radius: 10px;
}}

pre {{
    white-space: pre-wrap;
    line-height: 1.6;
}}

li {{
    margin-bottom: 10px;
}}

footer {{
    text-align: center;
    padding: 25px;
    color: #64748b;
}}

</style>
</head>

<body>

<header>
    <h1>Autonomous AI Job Application Agent</h1>
    <p>Workflow Execution Report</p>
    <p>Generated: {escape(timestamp)}</p>
</header>

<main>

    <h2>Workflow Metrics</h2>

    <div class="cards">
        {metric_cards}
    </div>

    <div class="panel">
        <h2>Detailed Workflow Report</h2>
        <pre>{escape(report.strip())}</pre>
    </div>

    <div class="panel">
        <h2>Workflow Errors</h2>
        <ul>
            {error_html}
        </ul>
    </div>

    <div class="panel">
        <h2>Safety Information</h2>
        <p>Applications and emails require human approval.</p>
        <p>Automatic application submissions and email sending are disabled.</p>
    </div>

</main>

<footer>
    Autonomous AI Job Agent | Generated automatically
</footer>

</body>
</html>
"""

    HTML_REPORT_PATH.write_text(
        html_content,
        encoding="utf-8"
    )

    logger.info("HTML report saved: %s", HTML_REPORT_PATH)

    return str(HTML_REPORT_PATH)


def report_node(state):

    logger.info("Report Node started.")

    print("\n[REPORT NODE]")
    print("=" * 50)

    errors = state.get("errors", [])

    report = f"""
AUTONOMOUS AI JOB AGENT - RUN REPORT
====================================

Jobs before scraping: {state.get('jobs_before', 0)}
New jobs collected: {state.get('new_jobs', 0)}
Eligible jobs: {state.get('eligible_jobs', 0)}
Filtered jobs: {state.get('filtered_jobs', 0)}
Jobs with score >= 6: {state.get('jobs_scored', 0)}

Application submissions: 0
Manual review jobs: {state.get('manual_review_jobs', 0)}
Email drafts created: {state.get('drafts_created', 0)}
Emails sent: 0
Pending follow-ups: {state.get('followups_queued', 0)}

Errors: {len(errors)}

All applications and emails require human approval.
"""

    print(report)

    logger.info("Final workflow report generated.")
    logger.info("New jobs collected: %s", state.get("new_jobs", 0))
    logger.info("Eligible jobs: %s", state.get("eligible_jobs", 0))
    logger.info("Filtered jobs: %s", state.get("filtered_jobs", 0))
    logger.info("Email drafts created: %s", state.get("drafts_created", 0))
    logger.info("Total errors: %s", len(errors))

    if errors:
        for error in errors:
            logger.error("Workflow error: %s", error)

    html_path = generate_html_report(state, report)

    logger.info("Report Node completed successfully.")

    return {
        "final_report": report,
        "final_report_html": html_path,
        "messages": list(state.get("messages", []))
    }


if __name__ == "__main__":

    result = report_node({})

    print("HTML report:", result["final_report_html"])
