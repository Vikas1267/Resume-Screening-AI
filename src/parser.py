"""Resume file parsing (PDF & text) and structured section extraction."""

from __future__ import annotations

import io
import os
import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional

import pdfplumber
from PyPDF2 import PdfReader

from src.nlp_processor import clean_raw_text
from src.skills import extract_skills

SECTION_HEADERS = {
    "skills": [
        "skills", "technical skills", "core competencies", "technologies",
        "tech stack", "key skills", "tools & technologies", "programming languages",
    ],
    "education": [
        "education", "academic background", "qualifications",
        "academic qualifications", "degrees", "certifications & education",
    ],
    "experience": [
        "experience", "work experience", "professional experience",
        "employment history", "career history", "internships", "work history",
    ],
    "projects": [
        "projects", "personal projects", "key projects", "academic projects",
    ],
    "summary": [
        "summary", "professional summary", "profile", "objective", "about me",
    ],
}

_EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
_PHONE_RE = re.compile(r"(?:\+?\d{1,3}[\s.-]?)?(?:\(?\d{3}\)?[\s.-]?)?\d{3}[\s.-]?\d{4}")
_YEARS_EXP_RE = re.compile(r"(\d{1,2})\s*\+?\s*(?:years|yrs)(?:\s+of)?\s+(?:experience|exp)", re.IGNORECASE)
_DATE_RANGE_RE = re.compile(r"\b(20\d{2}|19\d{2})\s*[-–—to]+\s*(20\d{2}|19\d{2}|present|current|now)\b", re.IGNORECASE)


@dataclass
class ParsedResume:
    filename: str
    candidate_name: str
    email: Optional[str]
    phone: Optional[str]
    raw_text: str
    skills: List[str] = field(default_factory=list)
    skills_by_category: Dict[str, List[str]] = field(default_factory=dict)
    education_lines: List[str] = field(default_factory=list)
    experience_lines: List[str] = field(default_factory=list)
    estimated_years_experience: Optional[int] = None
    sections: Dict[str, str] = field(default_factory=dict)
    parser_used: str = "text"


def extract_text_from_pdf_bytes(file_bytes: bytes) -> tuple[str, str]:
    """Extract text from PDF bytes using pdfplumber first, falling back to PyPDF2."""
    text_parts: List[str] = []
    try:
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text() or ""
                if page_text.strip():
                    text_parts.append(page_text)
        combined = clean_raw_text("\n".join(text_parts))
        if combined:
            return combined, "pdfplumber"
    except Exception:
        pass

    # Fallback to PyPDF2
    try:
        reader = PdfReader(io.BytesIO(file_bytes))
        fallback_parts = [page.extract_text() or "" for page in reader.pages]
        combined = clean_raw_text("\n".join(fallback_parts))
        if combined:
            return combined, "PyPDF2"
    except Exception as exc:
        raise ValueError(f"Failed to parse PDF file: {exc}") from exc

    return "", "pdfplumber"


def extract_text_from_bytes(file_bytes: bytes, filename: str) -> tuple[str, str]:
    """Extract raw text from PDF or plain text bytes based on extension."""
    ext = os.path.splitext(filename)[1].lower()
    if ext == ".pdf":
        return extract_text_from_pdf_bytes(file_bytes)
    if ext in {".txt", ".md", ".rtf"}:
        for encoding in ("utf-8", "utf-8-sig", "latin-1"):
            try:
                return clean_raw_text(file_bytes.decode(encoding)), "text"
            except UnicodeDecodeError:
                continue
        return clean_raw_text(file_bytes.decode("utf-8", errors="ignore")), "text"
    raise ValueError(f"Unsupported file format '{ext}'. Please upload PDF or TXT files.")


def _detect_section_header(line: str) -> Optional[str]:
    cleaned = re.sub(r"[:\-–—|_#*]+", " ", line).strip().lower()
    if not cleaned or len(cleaned) > 45:
        return None
    for section_key, aliases in SECTION_HEADERS.items():
        if cleaned in aliases:
            return section_key
    return None


def split_sections(raw_text: str) -> Dict[str, str]:
    """Segment resume text into logical sections (summary, skills, experience, education, projects)."""
    sections: Dict[str, List[str]] = {"header": []}
    current_section = "header"

    for line in raw_text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        detected = _detect_section_header(stripped)
        if detected:
            current_section = detected
            sections.setdefault(current_section, [])
        else:
            sections.setdefault(current_section, []).append(stripped)

    return {k: "\n".join(v) for k, v in sections.items() if v}


def _extract_candidate_name(raw_text: str, filename: str) -> str:
    """Infer candidate name from top lines of resume, falling back to filename."""
    lines = [ln.strip() for ln in raw_text.splitlines() if ln.strip()]
    for line in lines[:5]:
        # Skip contact lines or section headers
        if _EMAIL_RE.search(line) or _PHONE_RE.search(line):
            continue
        if _detect_section_header(line):
            continue
        if any(word in line.lower() for word in ("resume", "curriculum vitae", "cv", "http", "linkedin", "github")):
            continue
        # Strip trailing title after separator if e.g. "Alice Johnson | Senior Engineer"
        candidate = re.split(r"\s*[|•—–-]\s*", line)[0].strip()
        words = candidate.split()
        if 2 <= len(words) <= 4 and all(re.match(r"^[A-Za-z][A-Za-z.'-]*$", w) for w in words):
            return candidate

    stem = os.path.splitext(os.path.basename(filename))[0]
    cleaned_stem = re.sub(r"[_\-]+", " ", stem).strip()
    return cleaned_stem.title() if cleaned_stem else "Unknown Candidate"


def _estimate_years_experience(raw_text: str, experience_text: str) -> Optional[int]:
    explicit_matches = [int(m.group(1)) for m in _YEARS_EXP_RE.finditer(raw_text)]
    if explicit_matches:
        return max(explicit_matches)

    target_text = experience_text or raw_text
    ranges = _DATE_RANGE_RE.findall(target_text)
    if not ranges:
        return None

    current_year = 2026
    min_start = current_year
    max_end = 0
    for start_str, end_str in ranges:
        start = int(start_str)
        end = current_year if end_str.lower() in {"present", "current", "now"} else int(end_str)
        if 1980 <= start <= current_year and start <= end <= current_year:
            min_start = min(min_start, start)
            max_end = max(max_end, end)

    if max_end >= min_start and max_end > 0:
        return max(1, max_end - min_start)
    return None


def parse_resume_bytes(file_bytes: bytes, filename: str) -> ParsedResume:
    """Parse resume bytes (PDF/TXT) into a structured ParsedResume object."""
    raw_text, parser_used = extract_text_from_bytes(file_bytes, filename)
    if not raw_text:
        raise ValueError(f"No readable text could be extracted from '{filename}'.")

    sections = split_sections(raw_text)
    email_match = _EMAIL_RE.search(raw_text)
    phone_match = _PHONE_RE.search(raw_text)
    skill_info = extract_skills(raw_text)

    education_text = sections.get("education", "")
    experience_text = sections.get("experience", "")

    education_lines = [ln.strip("•- ") for ln in education_text.splitlines() if ln.strip()][:6]
    experience_lines = [ln.strip("•- ") for ln in experience_text.splitlines() if ln.strip()][:8]

    return ParsedResume(
        filename=filename,
        candidate_name=_extract_candidate_name(raw_text, filename),
        email=email_match.group(0) if email_match else None,
        phone=phone_match.group(0) if phone_match else None,
        raw_text=raw_text,
        skills=skill_info["skills"],  # type: ignore[arg-type]
        skills_by_category=skill_info["by_category"],  # type: ignore[arg-type]
        education_lines=education_lines,
        experience_lines=experience_lines,
        estimated_years_experience=_estimate_years_experience(raw_text, experience_text),
        sections=sections,
        parser_used=parser_used,
    )

