"""TF-IDF cosine similarity, skill-match scoring, candidate ranking, and summary reporting."""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from src.nlp_processor import preprocess_text
from src.parser import ParsedResume
from src.skills import extract_skills

_JD_YEARS_RE = re.compile(r"(\d{1,2})\s*\+?\s*(?:years|yrs)", re.IGNORECASE)


@dataclass
class CandidateReport:
    rank: int
    filename: str
    candidate_name: str
    email: Optional[str]
    phone: Optional[str]
    overall_score: float
    tfidf_score: float
    skill_match_score: float
    experience_score: float
    match_tier: str
    matched_skills: List[str]
    missing_skills: List[str]
    bonus_skills: List[str]
    all_skills: List[str]
    skills_by_category: Dict[str, List[str]]
    estimated_years_experience: Optional[int]
    education_lines: List[str]
    experience_lines: List[str]
    summary_report: str
    parser_used: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _extract_jd_required_years(job_description: str) -> Optional[int]:
    matches = [int(m.group(1)) for m in _JD_YEARS_RE.finditer(job_description)]
    return min(matches) if matches else None


def _compute_experience_score(
    resume: ParsedResume,
    jd_required_years: Optional[int],
) -> float:
    """Return a 0-100 score reflecting experience & structured profile completeness."""
    score = 0.0
    if resume.experience_lines or "experience" in resume.sections:
        score += 35.0
    if resume.education_lines or "education" in resume.sections:
        score += 25.0

    if jd_required_years is not None and resume.estimated_years_experience is not None:
        ratio = min(1.0, resume.estimated_years_experience / max(1, jd_required_years))
        score += 40.0 * ratio
    elif resume.estimated_years_experience is not None:
        score += min(40.0, resume.estimated_years_experience * 8.0)
    elif resume.experience_lines:
        score += 20.0

    return round(min(100.0, score), 1)


def _get_match_tier(score: float) -> str:
    if score >= 75.0:
        return "Strong Match"
    if score >= 55.0:
        return "Good Match"
    if score >= 35.0:
        return "Moderate Match"
    return "Low Match"


def _build_summary_report(
    name: str,
    overall_score: float,
    tier: str,
    matched_skills: List[str],
    missing_skills: List[str],
    years_exp: Optional[int],
    education_lines: List[str],
) -> str:
    parts: List[str] = [f"{name} is a {tier} ({overall_score:.1f}% overall relevance)."]

    if matched_skills:
        top_matched = ", ".join(matched_skills[:6])
        extra = f" (+{len(matched_skills) - 6} more)" if len(matched_skills) > 6 else ""
        parts.append(f"Matched key skills: {top_matched}{extra}.")
    else:
        parts.append("No exact taxonomy skill overlap detected with the job description.")

    if missing_skills:
        top_missing = ", ".join(missing_skills[:4])
        extra_m = f" (+{len(missing_skills) - 4} more)" if len(missing_skills) > 4 else ""
        parts.append(f"Missing JD skills: {top_missing}{extra_m}.")

    if years_exp is not None:
        parts.append(f"Estimated experience: ~{years_exp} year(s).")

    if education_lines:
        parts.append(f"Education highlight: {education_lines[0][:100]}.")

    return " ".join(parts)


def rank_resumes(
    job_description: str,
    resumes: List[ParsedResume],
) -> Dict[str, Any]:
    """
    Score and rank parsed resumes against a job description.

    Uses a hybrid scoring model:
      - Skill Match Score (55% weight when JD specifies skills)
      - TF-IDF Cosine Similarity on lemmatized unigrams+bigrams (35% weight, or 85% if no JD skills)
      - Experience & Profile Completeness Score (10% weight, or 15% if no JD skills)
    """
    if not job_description or not job_description.strip():
        raise ValueError("Job description cannot be empty.")
    if not resumes:
        return {"jd_skills": [], "jd_required_years": None, "candidates": []}

    jd_skill_info = extract_skills(job_description)
    jd_skills: List[str] = jd_skill_info["skills"]  # type: ignore[assignment]
    jd_skills_set = set(jd_skills)
    jd_required_years = _extract_jd_required_years(job_description)

    processed_jd = preprocess_text(job_description)
    processed_resumes = [preprocess_text(r.raw_text) for r in resumes]

    # Compute TF-IDF cosine similarity across [JD, Resume_1, ..., Resume_N]
    corpus = [processed_jd] + processed_resumes
    tfidf_scores: List[float] = [0.0] * len(resumes)

    if any(doc.strip() for doc in corpus):
        vectorizer = TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True, min_df=1)
        tfidf_matrix = vectorizer.fit_transform(corpus)
        similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()
        # Scale cosine similarity (typically 0.05–0.65 for resumes) smoothly to 0–100
        tfidf_scores = [round(min(100.0, float(sim) * 145.0), 1) for sim in similarities]

    scored_candidates: List[CandidateReport] = []
    for idx, resume in enumerate(resumes):
        cand_skills_set = set(resume.skills)
        matched_skills = sorted(jd_skills_set & cand_skills_set)
        missing_skills = sorted(jd_skills_set - cand_skills_set)
        bonus_skills = sorted(cand_skills_set - jd_skills_set)

        tfidf_score = tfidf_scores[idx]
        exp_score = _compute_experience_score(resume, jd_required_years)

        if jd_skills_set:
            skill_match_score = round((len(matched_skills) / len(jd_skills_set)) * 100.0, 1)
            overall_score = round(
                (0.55 * skill_match_score) + (0.35 * tfidf_score) + (0.10 * exp_score),
                1,
            )
        else:
            skill_match_score = 0.0
            overall_score = round((0.85 * tfidf_score) + (0.15 * exp_score), 1)

        tier = _get_match_tier(overall_score)
        summary = _build_summary_report(
            name=resume.candidate_name,
            overall_score=overall_score,
            tier=tier,
            matched_skills=matched_skills,
            missing_skills=missing_skills,
            years_exp=resume.estimated_years_experience,
            education_lines=resume.education_lines,
        )

        scored_candidates.append(
            CandidateReport(
                rank=0,
                filename=resume.filename,
                candidate_name=resume.candidate_name,
                email=resume.email,
                phone=resume.phone,
                overall_score=overall_score,
                tfidf_score=tfidf_score,
                skill_match_score=skill_match_score,
                experience_score=exp_score,
                match_tier=tier,
                matched_skills=matched_skills,
                missing_skills=missing_skills,
                bonus_skills=bonus_skills,
                all_skills=resume.skills,
                skills_by_category=resume.skills_by_category,
                estimated_years_experience=resume.estimated_years_experience,
                education_lines=resume.education_lines,
                experience_lines=resume.experience_lines,
                summary_report=summary,
                parser_used=resume.parser_used,
            )
        )

    scored_candidates.sort(
        key=lambda c: (c.overall_score, c.skill_match_score, c.tfidf_score),
        reverse=True,
    )
    for rank_idx, candidate in enumerate(scored_candidates, start=1):
        candidate.rank = rank_idx

    return {
        "jd_skills": jd_skills,
        "jd_skills_by_category": jd_skill_info["by_category"],
        "jd_required_years": jd_required_years,
        "total_candidates": len(scored_candidates),
        "candidates": [c.to_dict() for c in scored_candidates],
    }

