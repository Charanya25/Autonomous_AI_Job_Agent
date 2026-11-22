\# Autonomous AI Job Application Agent



An AI-powered job discovery and application-support platform built with Python, LangGraph, Gemini, SQLite, and Flask.



The project automates several stages of a job-search workflow: collecting job listings, removing duplicates, filtering opportunities, scoring eligible jobs, preparing recruiter email drafts, tracking application-related information, and generating reports.



\## Project Objectives



\- Collect job listings from multiple job sources.

\- Remove duplicate job records.

\- Filter opportunities based on job titles, skills, seniority, and location.

\- Use Gemini to evaluate relevant job opportunities.

\- Store job and workflow information in SQLite.

\- Prepare personalized recruiter email drafts.

\- Provide a Flask dashboard for monitoring the workflow.

\- Support scheduled workflow execution.

\- Generate HTML reports and maintain application-related records.



\## Technology Stack



| Technology | Purpose |

|---|---|

| Python | Main programming language |

| LangGraph | Multi-step workflow orchestration |

| Google Gemini | AI-based job relevance scoring |

| SQLite | Persistent data storage |

| Flask | Web dashboard |

| Requests | API requests |

| BeautifulSoup | HTML parsing |

| Playwright | Browser automation foundation |

| APScheduler | Scheduled workflow execution |

| Pandas | Data processing |

| Python-dotenv | Environment configuration |

| SMTP / DNS validation | Email infrastructure |



\## Architecture



The LangGraph workflow contains nine nodes:



1\. \*\*Load Memory\*\* – Loads existing database information.

2\. \*\*Scrape\*\* – Collects job listings.

3\. \*\*Filter\*\* – Checks job eligibility, location, seniority, and keywords.

4\. \*\*Score\*\* – Evaluates eligible jobs using Gemini.

5\. \*\*Apply\*\* – Reviews application opportunities and routes unsupported cases for manual review.

6\. \*\*Email\*\* – Generates recruiter outreach drafts.

7\. \*\*HR Drip\*\* – Tracks follow-up outreach.

8\. \*\*Save Memory\*\* – Stores workflow statistics.

9\. \*\*Report\*\* – Generates the final HTML report.



Conditional routing after filtering allows the workflow to skip scoring and continue to saving and reporting when there are no eligible jobs or an error occurs.



\## Job Sources



The project integrates three job sources:



\- RemoteOK

\- Jobicy

\- Arbeitnow



Job listings are stored in SQLite, with URL-based SHA-256 hashes used for duplicate detection.



Original job links should be used when reviewing opportunities. Always follow the source platforms' terms and conditions.



\## Main Features



\### 1. Job Collection

\- Collect listings from multiple sources.

\- Handle scraper errors independently.

\- Identify new and duplicate records.



\### 2. Job Filtering

\- Keyword whitelist and blacklist.

\- Senior and management role exclusion.

\- Location and remote-work eligibility checks.

\- Manual review for ambiguous location requirements.



\### 3. AI Job Scoring

\- Gemini-based relevance evaluation.

\- Scores on a 0–10 scale.

\- Batch processing and retry handling.

\- Persistent scoring status in SQLite.



\### 4. Application Review

\- Identifies opportunities requiring manual review.

\- Tracks application statuses.

\- Avoids unsupported or unverified automated application routes.



\### 5. Recruiter Email Drafting

\- Records company career-page information.

\- Checks publicly available recruiter contact information.

\- Prepares personalized email drafts.

\- Supports email validation and sending safeguards.



\### 6. Database

SQLite stores:

\- Job applications and listings.

\- Recruiter contact records.

\- Daily workflow statistics.

\- Follow-up outreach information.

\- Company source information.



\### 7. Flask Dashboard



The dashboard includes:



\- Overview

\- Jobs

\- Emails

\- Logs

\- Reports



\### 8. Scheduling and Reporting

\- APScheduler-based daily scheduling.

\- Structured rotating logs.

\- HTML workflow reports.

\- Daily statistics.



\## Project Structure



```text

Autonomous\_AI\_Job\_Agent/

│

├── agent/

│   ├── graph.py

│   ├── state.py

│   └── nodes/

│

├── config/

├── dashboard/

├── database/

├── data/

├── email\_engine/

├── logs/

├── reports/

├── scrapers/

├── tools/

│

├── filter\_jobs.py

├── score\_jobs.py

├── run\_all\_scrapers.py

├── run\_agent.py

├── requirements.txt

├── .env.example

├── .gitignore

└── README.md

```



\## Installation



\### Prerequisites



\- Python 3.13 (the development environment used for this project)

\- Git

\- A Google Gemini API key for AI scoring

\- Gmail credentials only if email functionality is configured



\### 1. Clone the repository



```powershell

git clone YOUR\_GITHUB\_REPOSITORY\_URL

cd Autonomous\_AI\_Job\_Agent

```



\### 2. Create a virtual environment



```powershell

python -m venv venv

```



\### 3. Activate the environment



```powershell

.\\venv\\Scripts\\Activate.ps1

```



\### 4. Install dependencies



```powershell

python -m pip install --upgrade pip

python -m pip install -r requirements.txt

```



\### 5. Install the Playwright browser



```powershell

playwright install chromium

```



\### 6. Configure environment variables



Create a `.env` file in the project root using `.env.example` as a template.



Add your own credentials:



```dotenv

GEMINI\_API\_KEY=your\_gemini\_api\_key

GMAIL\_ADDRESS=your\_gmail\_address

GMAIL\_APP\_PASSWORD=your\_gmail\_app\_password

```



Never publish your real `.env` file or credentials.



\## Running the Project



\### Run the workflow safely



```powershell

python run\_agent.py --dry-run

```



\### Execute the workflow immediately



```powershell

python run\_agent.py --run-now

```



\### Start the daily scheduler



```powershell

python run\_agent.py --schedule

```



The current workflow keeps application submission and email sending disabled. The dry-run mode can still collect listings, update the database, filter jobs, generate local drafts, and save statistics.



\### Start the Flask dashboard



```powershell

python dashboard/app.py

```



Open the following address in your browser:



http://127.0.0.1:5000



\## Safety and Limitations



\- Live job applications are currently disabled.

\- Email sending is currently disabled in the workflow.

\- Recruiter email addresses must be verified before any future sending is enabled.

\- Some job opportunities require manual location and eligibility verification.

\- Gemini API quota limits may affect scoring availability.

\- Scraping and automation must respect each platform's terms and conditions.

\- The system must not bypass authentication, CAPTCHA, or anti-bot protections.

\- Review job descriptions and generated email drafts before taking action.



\## Future Improvements



\- Add more permitted job-source integrations.

\- Improve location and eligibility classification.

\- Expand automated test coverage.

\- Improve recruiter contact discovery and verification.

\- Add configurable application workflows for supported portals.

\- Improve dashboard analytics and reporting.

\- Add comprehensive end-to-end testing.



\## Author



\*\*Sai Charanya Koneti\*\*



B.Tech – Computer Science and Engineering (Data Science)



GitHub: https://github.com/Charanya25



\## Disclaimer



This project is developed for educational and job-search assistance purposes. It does not guarantee job eligibility, application acceptance, or employment. Users are responsible for reviewing opportunities and complying with the terms of the relevant platforms.
