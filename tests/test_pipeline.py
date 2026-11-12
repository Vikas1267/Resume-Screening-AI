"""Unit and integration tests for Resume Screening AI."""

from __future__ import annotations

import io
from pathlib import Path

from app import app
from src.exporter import candidates_to_csv_string
from src.nlp_processor import preprocess_text
from src.parser import parse_resume_bytes
from src.scorer import rank_resumes
from src.skills import extract_skills

SAMPLES_DIR = Path(__file__).resolve().parent.parent / "samples"


def test_nlp_preprocessing_lemmatizes_and_removes_stopwords():
    raw = "Developing scalable machine learning models and running tests with Python!"
    processed = preprocess_text(raw)
    assert "python" in processed
    assert "machine" in processed
    assert "and" not in processed.split()
    assert "with" not in processed.split()


def test_skill_extraction_handles_aliases_and_boundaries():
    text = "Proficient in Python, sklearn, k8s, PostgreSQL, C++, and React.js. Not Java."
    # Note: 'Java' is explicitly in text above, so test JavaScript vs Java separately
    js_only = "Experienced in JavaScript, TypeScript, and Node.js."
    js_skills = extract_skills(js_only)["skills"]
    assert "JavaScript" in js_skills
    assert "Java" not in js_skills

    alias_text = "Built APIs with Flask, sklearn, postgres, k8s, and C++."
    alias_skills = extract_skills(alias_text)["skills"]
    for expected in ("Flask", "Scikit-learn", "PostgreSQL", "Kubernetes", "C++"):
        assert expected in alias_skills


def test_parse_sample_pdf_and_txt_resumes():
    pdf_path = SAMPLES_DIR / "resumes" / "aarav_sharma_ml_engineer.pdf"
    txt_path = SAMPLES_DIR / "resumes" / "marcus_chen_fullstack.txt"

    pdf_parsed = parse_resume_bytes(pdf_path.read_bytes(), pdf_path.name)
    assert pdf_parsed.candidate_name == "Aarav Sharma"
    assert pdf_parsed.email == "aarav.sharma@email.com"
    assert "Python" in pdf_parsed.skills
    assert "NLP" in pdf_parsed.skills
    assert len(pdf_parsed.education_lines) >= 1
    assert len(pdf_parsed.experience_lines) >= 1

    txt_parsed = parse_resume_bytes(txt_path.read_bytes(), txt_path.name)
    assert txt_parsed.candidate_name == "Marcus Chen"
    assert "React" in txt_parsed.skills
    assert "TypeScript" in txt_parsed.skills


def test_ranking_orders_most_relevant_candidate_first():
    jd = (SAMPLES_DIR / "job_descriptions" / "senior_python_ai_engineer.txt").read_text(encoding="utf-8")
    resumes = [
        parse_resume_bytes(p.read_bytes(), p.name)
        for p in sorted((SAMPLES_DIR / "resumes").iterdir())
        if p.suffix.lower() in {".pdf", ".txt"}
    ]

    results = rank_resumes(jd, resumes)
    candidates = results["candidates"]
    assert len(candidates) == 5
    assert candidates[0]["rank"] == 1
    assert candidates[0]["candidate_name"] == "Aarav Sharma"
    assert candidates[0]["overall_score"] > candidates[-1]["overall_score"]

    csv_output = candidates_to_csv_string(candidates)
    assert "Rank,Candidate Name,Filename" in csv_output
    assert "Aarav Sharma" in csv_output


def test_flask_api_screen_and_export():
    client = app.test_client()

    health_res = client.get("/api/health")
    assert health_res.status_code == 200

    samples_res = client.get("/api/samples")
    assert samples_res.status_code == 200
    assert len(samples_res.get_json()["job_descriptions"]) >= 3

    jd = (SAMPLES_DIR / "job_descriptions" / "fullstack_web_developer.txt").read_text(encoding="utf-8")
    sample_txt = (SAMPLES_DIR / "resumes" / "marcus_chen_fullstack.txt").read_bytes()

    screen_res = client.post(
        "/api/screen",
        data={
            "job_description": jd,
            "use_samples": "false",
            "resumes": (io.BytesIO(sample_txt), "marcus_chen_fullstack.txt"),
        },
        content_type="multipart/form-data",
    )
    assert screen_res.status_code == 200
    payload = screen_res.get_json()
    assert payload["total_candidates"] == 1
    assert payload["candidates"][0]["candidate_name"] == "Marcus Chen"

    export_res = client.post("/api/export-csv", json={"candidates": payload["candidates"]})
    assert export_res.status_code == 200
    assert b"Marcus Chen" in export_res.data

