# 📄 Resume Screening AI

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-Web%20App-000000?logo=flask&logoColor=white)
![NLP](https://img.shields.io/badge/NLP-NLTK%20%2B%20Scikit--learn-green)
![Tests](https://img.shields.io/badge/Tests-5%20Passing-brightgreen)

An AI-powered **Resume Screening & Candidate Ranking** tool that parses **PDF** and **TXT** resumes, extracts skills, education, and experience, compares them against a **Job Description**, and ranks candidates with clear match scores and summary reports.

---

## ✨ Key Features

- **Multi-Format Resume Parsing**: Supports `.pdf` (`pdfplumber` with `PyPDF2` fallback) and `.txt` / `.md` resumes.
- **Smart Section & Contact Extraction**: Extracts candidate name, email, phone, estimated years of experience, **Skills**, **Education**, and **Experience** sections.
- **NLP + Skill Matching**: Uses **NLTK** (tokenization, stopword removal, POS-aware lemmatization) + **Scikit-learn TF-IDF Cosine Similarity** + a 90+ skill taxonomy with alias normalization (e.g., `sklearn` → `Scikit-learn`, `k8s` → `Kubernetes`).
- **Modern Web Dashboard**: Drag-and-drop upload, **1-click Quick Demo**, dark/light theme, live search & tier filter, candidate profile modal, and **CSV Report Export**.
- **CLI Support**: Screen an entire folder of resumes directly from the terminal.

---

## 🚀 How to Run (Step-by-Step)

### 1. Open Terminal & Go to the Project Folder
```bash
cd "Resume Screening AI"
```

### 2. Create & Activate a Virtual Environment

**Windows (PowerShell):**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**macOS / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Web App
```bash
python app.py
```
Now open your browser and go to:
👉 **http://127.0.0.1:5000**

> 💡 **Tip:** Click **Quick Demo** in the top-right corner of the web app to test immediately using the built-in sample job description and 5 sample resumes!

---

## 💻 Optional: Run via Command Line (CLI)

You can also screen a folder of resumes from your terminal and save a CSV report:

```bash
python cli.py --jd samples/job_descriptions/senior_python_ai_engineer.txt --resumes samples/resumes --out samples/sample_ranking_report.csv
```

---

## 🧠 How the Scoring Algorithm Works

Each candidate receives an **Overall Match Score (0–100%)** using a transparent hybrid formula:

$$\text{Overall Score} = 0.55 \times \text{Skill Match} + 0.35 \times \text{TF-IDF Similarity} + 0.10 \times \text{Experience Alignment}$$

| Component | Weight | What It Measures |
| :--- | :---: | :--- |
| **Skill Match** | **55%** | Percentage of Job Description skills found in the resume (with matched & missing skill breakdown). |
| **TF-IDF Similarity** | **35%** | Cosine similarity between the lemmatized JD and resume text (unigrams + bigrams). |
| **Experience & Profile** | **10%** | Presence of Education/Experience sections and alignment with JD years of experience. |

*(If a job description has no predefined skill keywords, weights automatically adjust to **85% TF-IDF + 15% Experience**.)*

**Match Tiers:**
- 🟢 **Strong Match**: `75% – 100%`
- 🔵 **Good Match**: `55% – 74.9%`
- 🟡 **Moderate Match**: `35% – 54.9%`
- 🔴 **Low Match**: `< 35%`

---

## 📁 Project Structure

```text
Resume Screening AI/
├── app.py                  # Flask web server & REST API
├── cli.py                  # Command-line batch screening tool
├── requirements.txt        # Python dependencies
├── src/
│   ├── parser.py           # PDF/TXT text & section extraction
│   ├── nlp_processor.py    # NLTK tokenization, stopwords & lemmatization
│   ├── skills.py           # Categorized skill taxonomy & matching
│   ├── scorer.py           # TF-IDF cosine similarity & hybrid ranking
│   └── exporter.py         # CSV report generator
├── templates/index.html    # Web UI layout
├── static/                 # CSS & JavaScript frontend
├── samples/                # Sample job descriptions, resumes & CSV report
└── tests/                  # Automated pytest suite
```

---

## 🧪 Run Tests

```bash
python -m pytest -v
```
