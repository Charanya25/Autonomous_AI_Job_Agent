
import sqlite3
from pathlib import Path

from flask import Flask, render_template_string, request, send_file

from database.db_manager import DB_PATH
from config.logging_config import LOG_FILE


app = Flask(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent

DRAFT_DIR = BASE_DIR / "reports" / "email_drafts"
REPORT_PATH = BASE_DIR / "reports" / "latest_report.html"


# --------------------------------------------------
# DATABASE CONNECTION
# --------------------------------------------------

def get_db_connection():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


# --------------------------------------------------
# DASHBOARD STATISTICS
# --------------------------------------------------

def get_statistics():
    connection = get_db_connection()

    try:
        total = connection.execute(
            "SELECT COUNT(*) FROM applications"
        ).fetchone()[0]

        statuses = connection.execute(
            """
            SELECT status, COUNT(*) AS count
            FROM applications
            GROUP BY status
            """
        ).fetchall()

        scored = connection.execute(
            """
            SELECT COUNT(*) FROM applications
            WHERE relevance_score >= 6
            """
        ).fetchone()[0]

        drafts = (
            len(list(DRAFT_DIR.glob("*.txt")))
            if DRAFT_DIR.exists()
            else 0
        )

        return {
            "total": total,
            "statuses": statuses,
            "scored": scored,
            "drafts": drafts
        }

    finally:
        connection.close()


# --------------------------------------------------
# RECENT JOBS
# --------------------------------------------------

def get_recent_jobs(limit=100):
    connection = get_db_connection()

    try:
        return connection.execute(
            """
            SELECT job_title, company, location, portal,
                   status, relevance_score, job_url, created_at
            FROM applications
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,)
        ).fetchall()

    finally:
        connection.close()


# --------------------------------------------------
# EMAIL DRAFTS
# --------------------------------------------------

def get_email_drafts():

    if not DRAFT_DIR.exists():
        return []

    drafts = []

    for file in sorted(DRAFT_DIR.glob("*.txt"), reverse=True):

        try:
            content = file.read_text(encoding="utf-8")

        except Exception:
            content = "Unable to read this draft."

        drafts.append({
            "name": file.name,
            "content": content
        })

    return drafts


# --------------------------------------------------
# RECENT LOGS
# --------------------------------------------------

def get_recent_logs():

    if not Path(LOG_FILE).exists():
        return ["Log file not found."]

    try:
        lines = Path(LOG_FILE).read_text(
            encoding="utf-8",
            errors="replace"
        ).splitlines()

        return lines[-100:]

    except Exception as error:
        return [f"Unable to read logs: {error}"]


# --------------------------------------------------
# DASHBOARD HTML TEMPLATE
# --------------------------------------------------

TEMPLATE = """
<!DOCTYPE html>
<html lang="en">

<head>

    <meta charset="UTF-8">

    <meta name="viewport"
          content="width=device-width, initial-scale=1">

    <title>Autonomous AI Job Agent</title>

    <style>

        * {
            box-sizing: border-box;
        }

        body {
            margin: 0;
            font-family: Arial, sans-serif;
            background: #f3f5f9;
            color: #202938;
        }

        header {
            background: #172554;
            color: white;
            padding: 22px 30px;
        }

        header h1 {
            margin: 0 0 8px;
        }

        nav {
            background: white;
            padding: 16px 30px;
            border-bottom: 1px solid #ddd;
        }

        nav a {
            color: #1d4ed8;
            text-decoration: none;
            margin-right: 22px;
            font-weight: bold;
        }

        nav a:hover {
            text-decoration: underline;
        }

        main {
            padding: 25px;
            max-width: 1250px;
            margin: auto;
        }

        .cards {
            display: grid;
            grid-template-columns:
                repeat(auto-fit, minmax(180px, 1fr));
            gap: 16px;
            margin-bottom: 25px;
        }

        .card,
        .panel {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 8px #0000000d;
        }

        .card h3 {
            color: #64748b;
            margin-top: 0;
        }

        .number {
            font-size: 30px;
            font-weight: bold;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            background: white;
        }

        th,
        td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #e5e7eb;
        }

        th {
            background: #eaf0fa;
        }

        .table-wrap {
            overflow-x: auto;
        }

        .panel {
            margin-bottom: 20px;
        }

        .draft,
        .log {
            background: #f8fafc;
            padding: 14px;
            margin: 12px 0;
            border-radius: 7px;
            overflow-wrap: anywhere;
        }

        pre {
            white-space: pre-wrap;
            overflow-wrap: anywhere;
            font-size: 12px;
        }

        .muted {
            color: #64748b;
        }

        input,
        button {
            padding: 10px;
            margin: 5px 0;
        }

        button {
            background: #1d4ed8;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }

        footer {
            text-align: center;
            padding: 25px;
            color: #64748b;
        }

        @media (max-width: 600px) {

            nav a {
                display: inline-block;
                margin-bottom: 12px;
            }

            main {
                padding: 14px;
            }

        }

    </style>

</head>

<body>

<header>

    <h1>Autonomous AI Job Application Agent</h1>

    <div>
        Job monitoring and application management dashboard
    </div>

</header>


<!-- NAVIGATION -->

<nav>

    <a href="/">Overview</a>

    <a href="/jobs">Jobs</a>

    <a href="/emails">Emails</a>

    <a href="/logs">Logs</a>

    <a href="/reports">Reports</a>

</nav>


<main>


{% if page == "overview" %}

    <h2>Dashboard Overview</h2>

    <div class="cards">

        <div class="card">
            <h3>Total Jobs</h3>
            <div class="number">{{ stats.total }}</div>
        </div>

        <div class="card">
            <h3>Scored 6 or Above</h3>
            <div class="number">{{ stats.scored }}</div>
        </div>

        <div class="card">
            <h3>Email Drafts</h3>
            <div class="number">{{ stats.drafts }}</div>
        </div>

    </div>


    <div class="panel">

        <h2>Job Status Summary</h2>

        <div class="table-wrap">

            <table>

                <tr>
                    <th>Status</th>
                    <th>Count</th>
                </tr>

                {% for item in stats.statuses %}

                <tr>
                    <td>{{ item.status }}</td>
                    <td>{{ item.count }}</td>
                </tr>

                {% else %}

                <tr>
                    <td colspan="2">No job records found.</td>
                </tr>

                {% endfor %}

            </table>

        </div>

    </div>


    <div class="panel">

        <h2>Recent Jobs</h2>

        <div class="table-wrap">

            <table>

                <tr>
                    <th>Job</th>
                    <th>Company</th>
                    <th>Status</th>
                    <th>Score</th>
                </tr>

                {% for job in jobs[:10] %}

                <tr>
                    <td>{{ job.job_title }}</td>
                    <td>{{ job.company }}</td>
                    <td>{{ job.status }}</td>
                    <td>{{ job.relevance_score }}</td>
                </tr>

                {% endfor %}

            </table>

        </div>

    </div>


{% elif page == "jobs" %}

    <h2>Saved Jobs</h2>

    <form method="get">

        <input
            name="search"
            placeholder="Search title or company"
            value="{{ search }}"
        >

        <button type="submit">Search</button>

    </form>

    <p class="muted">
        Showing up to 100 recent matching jobs.
    </p>

    <div class="panel table-wrap">

        <table>

            <tr>
                <th>Title</th>
                <th>Company</th>
                <th>Location</th>
                <th>Portal</th>
                <th>Status</th>
                <th>Score</th>
                <th>Link</th>
            </tr>

            {% for job in jobs %}

            <tr>

                <td>{{ job.job_title }}</td>

                <td>{{ job.company }}</td>

                <td>{{ job.location }}</td>

                <td>{{ job.portal }}</td>

                <td>{{ job.status }}</td>

                <td>{{ job.relevance_score }}</td>

                <td>

                    {% if job.job_url %}

                    <a
                        href="{{ job.job_url }}"
                        target="_blank"
                        rel="noopener noreferrer"
                    >
                        Open
                    </a>

                    {% endif %}

                </td>

            </tr>

            {% else %}

            <tr>
                <td colspan="7">No matching jobs found.</td>
            </tr>

            {% endfor %}

        </table>

    </div>


{% elif page == "emails" %}

    <h2>Saved Email Drafts</h2>

    <p class="muted">
        These are local drafts only.
        No emails are sent from this dashboard.
    </p>

    {% for draft in drafts %}

    <div class="panel">

        <h3>{{ draft.name }}</h3>

        <pre>{{ draft.content }}</pre>

    </div>

    {% else %}

    <div class="panel">
        No email drafts found.
    </div>

    {% endfor %}


{% elif page == "logs" %}

    <h2>Agent Activity Logs</h2>

    <p class="muted">
        Showing the latest 100 log entries.
    </p>

    <div class="panel">

        {% for line in logs %}

        <div class="log">
            {{ line }}
        </div>

        {% else %}

        <div>No log entries found.</div>

        {% endfor %}

    </div>


{% endif %}


</main>


<footer>
    Autonomous AI Job Agent | Flask Dashboard
</footer>


</body>

</html>
"""


# --------------------------------------------------
# OVERVIEW ROUTE
# --------------------------------------------------

@app.route("/")
def overview():

    return render_template_string(
        TEMPLATE,
        page="overview",
        stats=get_statistics(),
        jobs=get_recent_jobs()
    )


# --------------------------------------------------
# JOBS ROUTE
# --------------------------------------------------

@app.route("/jobs")
def jobs_page():

    search = request.args.get("search", "").strip()

    jobs = get_recent_jobs()

    if search:

        search_lower = search.lower()

        jobs = [
            job for job in jobs
            if search_lower in (job["job_title"] or "").lower()
            or search_lower in (job["company"] or "").lower()
        ]

    return render_template_string(
        TEMPLATE,
        page="jobs",
        jobs=jobs,
        search=search
    )


# --------------------------------------------------
# EMAILS ROUTE
# --------------------------------------------------

@app.route("/emails")
def emails_page():

    return render_template_string(
        TEMPLATE,
        page="emails",
        drafts=get_email_drafts()
    )


# --------------------------------------------------
# LOGS ROUTE
# --------------------------------------------------

@app.route("/logs")
def logs_page():

    return render_template_string(
        TEMPLATE,
        page="logs",
        logs=get_recent_logs()
    )


# --------------------------------------------------
# REPORTS ROUTE
# --------------------------------------------------

@app.route("/reports")
def reports_page():

    if not REPORT_PATH.exists():

        return (
            "HTML report not found. Run the workflow first.",
            404
        )

    return send_file(REPORT_PATH)


# --------------------------------------------------
# RUN DASHBOARD
# --------------------------------------------------

if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False
    )
