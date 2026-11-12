"""Flask web server and REST API for Resume Screening AI."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, List

from flask import Flask, Response, jsonify, render_template, request

from src.exporter import candidates_to_csv_string
from src.nlp_processor import ensure_nltk_data
from src.parser import ParsedResume, parse_resume_bytes
from src.scorer import rank_resumes

BASE_DIR = Path(__file__).resolve().parent
SAMPLES_JD_DIR = BASE_DIR / "samples" / "job_descriptions"
SAMPLES_RESUME_DIR = BASE_DIR / "samples" / "resumes"
ALLOWED_EXTENSIONS = {".pdf", ".txt", ".md"}

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 25 * 1024 * 1024  # 25 MB max upload


@app.route("/")
def index() -> str:
    return render_template("index.html")


@app.route("/api/health")
def health() -> Response:
    return jsonify({"status": "ok"})


@app.route("/api/samples")
def list_samples() -> Response:
    jds = []
    if SAMPLES_JD_DIR.exists():
        for p in sorted(SAMPLES_JD_DIR.glob("*.txt")):
            jds.append({
                "id": p.name,
                "title": p.stem.replace("_", " ").title(),
                "content": p.read_text(encoding="utf-8"),
            })

    resumes = []
    if SAMPLES_RESUME_DIR.exists():
        for p in sorted(SAMPLES_RESUME_DIR.iterdir()):
            if p.suffix.lower() in ALLOWED_EXTENSIONS:
                resumes.append({
                    "filename": p.name,
                    "size_kb": round(p.stat().st_size / 1024, 1),
                    "format": p.suffix.lstrip(".").upper(),
                })

    return jsonify({"job_descriptions": jds, "resumes": resumes})


@app.route("/api/screen", methods=["POST"])
def screen_resumes() -> tuple[Response, int] | Response:
    job_description = (request.form.get("job_description") or "").strip()
    if not job_description:
        return jsonify({"error": "Please provide a job description."}), 400

    use_samples = request.form.get("use_samples", "false").lower() == "true"
    uploaded_files = request.files.getlist("resumes")

    parsed_resumes: List[ParsedResume] = []
    errors: List[Dict[str, str]] = []

    if use_samples and SAMPLES_RESUME_DIR.exists():
        for p in sorted(SAMPLES_RESUME_DIR.iterdir()):
            if p.suffix.lower() in ALLOWED_EXTENSIONS:
                try:
                    parsed_resumes.append(parse_resume_bytes(p.read_bytes(), p.name))
                except Exception as exc:
                    errors.append({"filename": p.name, "error": str(exc)})

    for file_storage in uploaded_files:
        filename = file_storage.filename or ""
        if not filename:
            continue
        ext = os.path.splitext(filename)[1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            errors.append({
                "filename": filename,
                "error": f"Unsupported format '{ext}'. Only PDF and TXT files are accepted.",
            })
            continue
        try:
            file_bytes = file_storage.read()
            parsed_resumes.append(parse_resume_bytes(file_bytes, filename))
        except Exception as exc:
            errors.append({"filename": filename, "error": str(exc)})

    if not parsed_resumes:
        msg = "No valid resumes could be parsed."
        if errors:
            msg += f" ({errors[0]['filename']}: {errors[0]['error']})"
        return jsonify({"error": msg, "file_errors": errors}), 400

    results: Dict[str, Any] = rank_resumes(job_description, parsed_resumes)
    results["file_errors"] = errors
    return jsonify(results)


@app.route("/api/export-csv", methods=["POST"])
def export_csv() -> tuple[Response, int] | Response:
    payload = request.get_json(silent=True) or {}
    candidates = payload.get("candidates")
    if not isinstance(candidates, list) or not candidates:
        return jsonify({"error": "No candidate results provided for export."}), 400

    csv_data = candidates_to_csv_string(candidates)
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=candidate_ranking_report.csv"},
    )


if __name__ == "__main__":
    ensure_nltk_data()
    app.run(host="127.0.0.1", port=5000, debug=True)

