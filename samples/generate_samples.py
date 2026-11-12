"""Generate realistic sample job descriptions and PDF/TXT resumes for testing and demo."""

from __future__ import annotations

import os
from pathlib import Path

from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

BASE_DIR = Path(__file__).resolve().parent
JD_DIR = BASE_DIR / "job_descriptions"
RESUME_DIR = BASE_DIR / "resumes"

SAMPLE_JDS = {
    "senior_python_ai_engineer.txt": """Senior Python & AI Engineer

We are looking for a Senior Python & AI Engineer with 4+ years of experience building scalable NLP and machine learning systems.

Required Skills:
- Strong proficiency in Python, SQL, and REST APIs (Flask or FastAPI)
- Hands-on experience with NLP, Scikit-learn, NLTK or spaCy, and HuggingFace Transformers
- Experience with PyTorch or TensorFlow, RAG, and LLMs
- Solid understanding of Docker, Kubernetes, AWS, CI/CD, and PostgreSQL
- Familiarity with Git, Unit Testing (pytest), and Agile/Scrum workflows

Responsibilities:
- Design and deploy production ML/NLP pipelines and document parsing services
- Optimize TF-IDF, embedding search, and ranking algorithms
- Collaborate with cross-functional teams to deliver reliable AI features
""",
    "fullstack_web_developer.txt": """Full-Stack Web Developer

Seeking a Full-Stack Web Developer with 3+ years of experience building responsive web applications.

Required Skills:
- Frontend: JavaScript, TypeScript, React, Next.js, HTML5, CSS3
- Backend: Node.js, Express.js, or Python (Django / Flask), REST API, GraphQL
- Databases: PostgreSQL, MongoDB, Redis
- DevOps: Docker, Git, CI/CD, AWS
- Agile/Scrum and Unit Testing (Jest or pytest)
""",
    "data_analyst.txt": """Data Analyst

Looking for a detail-oriented Data Analyst with 2+ years of experience turning raw data into actionable business insights.

Required Skills:
- SQL, Python (Pandas, NumPy, SciPy), and Statistics (A/B Testing, Hypothesis Testing)
- Data Visualization with Tableau, Power BI, Matplotlib, or Seaborn
- ETL pipelines, BigQuery or Snowflake, and PostgreSQL
- Strong Communication and Problem Solving skills
""",
}

SAMPLE_RESUMES = [
    {
        "filename": "aarav_sharma_ml_engineer.pdf",
        "format": "pdf",
        "text": """Aarav Sharma
aarav.sharma@email.com | +1 (555) 234-8910 | San Francisco, CA

SUMMARY
Senior Machine Learning & NLP Engineer with 5+ years of experience designing production AI pipelines, document intelligence systems, and scalable Python microservices.

SKILLS
Programming: Python, SQL, Bash
AI & NLP: Machine Learning, NLP, Scikit-learn, NLTK, spaCy, HuggingFace, PyTorch, LLMs, RAG, Pandas, NumPy
Backend & Cloud: Flask, FastAPI, REST API, PostgreSQL, Docker, Kubernetes, AWS, CI/CD, Git, pytest

EXPERIENCE
Senior AI Engineer — NovaTech AI (2022 - Present)
- Built an automated resume and document screening engine using Python, NLTK, Scikit-learn, and HuggingFace Transformers.
- Deployed Flask and FastAPI microservices in Docker containers on AWS EKS (Kubernetes) with CI/CD via GitHub Actions.
- Designed RAG pipelines with LLMs and PostgreSQL vector search, reducing manual review time by 65%.

Machine Learning Engineer — DataPulse Labs (2020 - 2022)
- Developed NLP text classification and named-entity extraction models using spaCy and PyTorch.
- Automated unit testing with pytest and collaborated in Agile/Scrum sprints.

EDUCATION
M.S. in Computer Science — Stanford University (2018 - 2020)
B.Tech in Computer Science — IIT Delhi (2014 - 2018)
""",
    },
    {
        "filename": "priya_nair_data_scientist.pdf",
        "format": "pdf",
        "text": """Priya Nair
priya.nair@email.com | (555) 876-5432 | Austin, TX

SUMMARY
Data Scientist with 4 years of experience in predictive modeling, statistical analysis, and NLP analytics.

SKILLS
Languages: Python, R, SQL
ML & Data: Scikit-learn, TensorFlow, Pandas, NumPy, SciPy, NLTK, Feature Engineering, Statistics, Data Visualization, Tableau
Tools: Flask, PostgreSQL, Docker, Git, AWS, ETL, Snowflake

EXPERIENCE
Data Scientist — InsightSphere (2022 - Present)
- Built customer churn and lead-scoring models in Python using Scikit-learn and XGBoost.
- Performed NLP topic modeling on customer feedback using NLTK and TF-IDF.
- Created interactive Tableau dashboards and automated ETL workflows into Snowflake.

Junior Data Analyst — FinMetrics Corp (2020 - 2022)
- Wrote complex SQL queries on PostgreSQL and conducted A/B testing for product experiments.

EDUCATION
M.S. in Data Science — University of Texas at Austin (2018 - 2020)
B.S. in Mathematics — University of Michigan (2014 - 2018)
""",
    },
    {
        "filename": "marcus_chen_fullstack.txt",
        "format": "txt",
        "text": """Marcus Chen
marcus.chen@email.com | 555-345-6789 | Seattle, WA

PROFESSIONAL SUMMARY
Full-Stack Software Engineer with 4+ years of experience building modern React and Node.js applications with Python backend integrations.

TECHNICAL SKILLS
Frontend: JavaScript, TypeScript, React, Next.js, HTML5, CSS3
Backend: Node.js, Express.js, Python, Flask, REST API, GraphQL
Databases & Cloud: PostgreSQL, MongoDB, Redis, Docker, AWS, CI/CD, Git, Jest, Agile

WORK EXPERIENCE
Senior Full-Stack Developer — CloudScale Systems (2021 - Present)
- Architected responsive React + TypeScript dashboards and GraphQL/REST APIs in Node.js and Flask.
- Managed PostgreSQL and Redis caching layers inside Docker containers on AWS.

Software Engineer — WebCraft Studio (2019 - 2021)
- Built Next.js e-commerce storefronts and automated CI/CD pipelines with GitHub Actions.

EDUCATION
B.S. in Software Engineering — University of Washington (2015 - 2019)
""",
    },
    {
        "filename": "elena_rodriguez_data_analyst.pdf",
        "format": "pdf",
        "text": """Elena Rodriguez
elena.rodriguez@email.com | 555-901-2233 | Chicago, IL

SUMMARY
Data Analyst with 3 years of experience transforming large datasets into executive dashboards and business recommendations.

SKILLS
Analytics: SQL, Python, Pandas, NumPy, Statistics, Data Analysis, Data Visualization
BI & Warehousing: Tableau, Power BI, BigQuery, Snowflake, PostgreSQL, ETL
Soft Skills: Communication, Problem Solving, Stakeholder Management

EXPERIENCE
Data Analyst — RetailPulse Inc (2023 - Present)
- Built automated BigQuery ETL pipelines and Power BI / Tableau KPI dashboards for 120+ stakeholders.
- Conducted hypothesis testing and A/B experiments to optimize marketing spend by 18%.

Business Analyst — MetroLogistics (2021 - 2023)
- Analyzed supply chain metrics using SQL, Python (Pandas), and Matplotlib.

EDUCATION
B.S. in Economics & Statistics — Northwestern University (2017 - 2021)
""",
    },
    {
        "filename": "david_kim_junior_dev.txt",
        "format": "txt",
        "text": """David Kim
david.kim@email.com | 555-654-3210 | Boston, MA

OBJECTIVE
Recent Computer Science graduate seeking an entry-level Software Engineering or Backend role.

SKILLS
Languages: Python, Java, C++, SQL, HTML5, CSS3
Tools: Git, Linux, MySQL, Flask, Unit Testing

EXPERIENCE
Software Engineering Intern — TechStart (Summer 2025)
- Assisted in building internal REST API endpoints using Python and Flask.
- Wrote unit tests and fixed bugs in MySQL queries.

PROJECTS
- Campus Event Finder: Built a web app using Flask, HTML5, CSS3, and SQLite.

EDUCATION
B.S. in Computer Science — Boston University (2022 - 2026)
""",
    },
]


def _write_pdf(path: Path, text: str) -> None:
    doc = SimpleDocTemplate(
        str(path),
        pagesize=LETTER,
        leftMargin=0.75 * inch,
        rightMargin=0.75 * inch,
        topMargin=0.7 * inch,
        bottomMargin=0.7 * inch,
    )
    styles = getSampleStyleSheet()
    body_style = ParagraphStyle(
        "ResumeBody",
        parent=styles["Normal"],
        fontSize=10,
        leading=14,
    )
    header_style = ParagraphStyle(
        "ResumeHeader",
        parent=styles["Heading2"],
        fontSize=11,
        leading=15,
        spaceBefore=8,
        spaceAfter=2,
    )

    story = []
    for idx, line in enumerate(text.strip().splitlines()):
        stripped = line.strip()
        if not stripped:
            story.append(Spacer(1, 6))
            continue
        escaped = stripped.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        if idx == 0 or stripped.isupper():
            story.append(Paragraph(f"<b>{escaped}</b>", header_style))
        else:
            story.append(Paragraph(escaped, body_style))

    doc.build(story)


def generate_all() -> None:
    JD_DIR.mkdir(parents=True, exist_ok=True)
    RESUME_DIR.mkdir(parents=True, exist_ok=True)

    for filename, content in SAMPLE_JDS.items():
        (JD_DIR / filename).write_text(content.strip() + "\n", encoding="utf-8")

    for item in SAMPLE_RESUMES:
        target = RESUME_DIR / item["filename"]
        if item["format"] == "pdf":
            _write_pdf(target, item["text"])
        else:
            target.write_text(item["text"].strip() + "\n", encoding="utf-8")

    print(f"Generated {len(SAMPLE_JDS)} sample JDs in {JD_DIR}")
    print(f"Generated {len(SAMPLE_RESUMES)} sample resumes in {RESUME_DIR}")


if __name__ == "__main__":
    generate_all()

