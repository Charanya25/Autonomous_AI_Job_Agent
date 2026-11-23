\# Technical Report

\## Autonomous AI Job Application Agent



\*\*Author:\*\* Sai Charanya Koneti  

\*\*Degree:\*\* B.Tech – Computer Science and Engineering (Data Science)  

\*\*Programming Language:\*\* Python 3.13



\### 1. Introduction



The Autonomous AI Job Application Agent is an AI-powered job discovery and application-support platform. It helps simplify the job-search process by collecting job listings from multiple sources, removing duplicates, filtering suitable opportunities, evaluating job relevance using Google Gemini, preparing recruiter email drafts, and generating reports.



The project uses a multi-agent workflow implemented with LangGraph and stores information in an SQLite database.



\### 2. Objectives



\- Collect job listings from multiple job platforms.

\- Remove duplicate listings using SHA-256 URL hashing.

\- Filter jobs based on keywords, seniority, and location.

\- Evaluate eligible jobs using Google Gemini.

\- Store job information and workflow history in SQLite.

\- Generate personalized recruiter email drafts.

\- Provide a Flask dashboard to monitor job-search activities.

\- Support scheduled execution and HTML reporting.



\### 3. Technologies Used



| Technology | Purpose |

|---|---|

| Python | Core development |

| LangGraph | Workflow orchestration |

| Google Gemini | AI-based job scoring |

| SQLite | Database management |

| Flask | Web dashboard |

| Requests | API communication |

| BeautifulSoup | HTML parsing |

| Playwright | Browser automation foundation |

| APScheduler | Scheduled execution |

| Pandas | Data processing |

| SMTP and DNS | Email infrastructure |



\### 4. System Architecture



The system contains nine LangGraph workflow nodes:



1\. \*\*Load Memory:\*\* Retrieves previously stored information.

2\. \*\*Scrape:\*\* Collects job listings from RemoteOK, Jobicy, and Arbeitnow.

3\. \*\*Filter:\*\* Evaluates job titles, keywords, seniority, and location.

4\. \*\*Score:\*\* Uses Gemini to score eligible jobs from 0 to 10.

5\. \*\*Apply:\*\* Reviews job opportunities and identifies cases requiring manual application.

6\. \*\*Email:\*\* Generates recruiter outreach drafts.

7\. \*\*HR Drip:\*\* Tracks follow-up outreach information.

8\. \*\*Save Memory:\*\* Stores workflow statistics.

9\. \*\*Report:\*\* Generates an HTML report.



Conditional routing helps the workflow skip unnecessary stages when no eligible jobs are available.



\### 5. Implementation and Features



\*\*Job Collection and Deduplication:\*\*  

The application retrieves listings from three job sources. SHA-256 URL hashing helps identify duplicate records before storing new jobs in SQLite.



\*\*Job Filtering:\*\*  

A filtering module uses keyword inclusion and exclusion rules, seniority checks, and location eligibility rules. Ambiguous opportunities are marked for manual review.



\*\*AI-Based Scoring:\*\*  

Google Gemini evaluates eligible job opportunities based on their relevance. Batch processing, retry handling, and scoring status tracking are implemented.



\*\*Application Support:\*\*  

The application engine identifies suitable opportunities and routes unsupported or unverified application methods for manual review.



\*\*Recruiter Email Drafting:\*\*  

The email module records company contact information, performs email validation checks, and prepares personalized outreach drafts. Email sending remains disabled in the current workflow.



\*\*Dashboard and Reporting:\*\*  

The Flask dashboard provides Overview, Jobs, Emails, Logs, and Reports sections. The system also generates HTML reports and records daily workflow statistics.



\### 6. Database Design



SQLite is used for persistent storage. The main database tables include:



\- `applications` – Job listings, scores, and application statuses.

\- `hr\_contacts` – Recruiter and company contact records.

\- `daily\_stats` – Workflow execution statistics.

\- `drip\_outreach` – Follow-up outreach tracking.

\- `company\_sources` – Company source information.



\### 7. Testing and Validation



The project was validated through Python compilation checks, database integrity checks, scraper execution, scoring status verification, email connection testing, and Flask dashboard route testing.



The database successfully stored job records from the integrated sources, and duplicate detection was verified.



Live job applications and email sending remain disabled. Generated recruiter drafts require manual review before use.



\### 8. Limitations and Future Improvements



Current limitations include Gemini API quota restrictions, incomplete recruiter email discovery, manual application requirements for unsupported portals, and location eligibility cases requiring human verification.



Future improvements include additional permitted job-source integrations, expanded automated testing, improved recruiter contact discovery, enhanced dashboard analytics, and configurable application workflows.



\### 9. Conclusion



The Autonomous AI Job Application Agent demonstrates how Python, LangGraph, Gemini, SQLite, and Flask can be combined to build an AI-assisted job discovery and application-support platform.



The project provides an integrated workflow for collecting, filtering, scoring, tracking, and reporting job opportunities while retaining human review for application submission and recruiter communication.



\*\*GitHub Repository:\*\* https://github.com/Charanya25/Autonomous\_AI\_Job\_Agent

