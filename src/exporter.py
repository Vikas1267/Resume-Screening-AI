"""Export candidate ranking results to CSV format."""

from __future__ import annotations

import csv
import io
from typing import Any, Dict, List


CSV_HEADERS = [
    "Rank",
    "Candidate Name",
    "Filename",
    "Email",
    "Phone",
    "Overall Score (%)",
    "Match Tier",
    "Skill Match (%)",
    "TF-IDF Similarity (%)",
    "Experience Score (%)",
    "Estimated Years Experience",
    "Matched Skills",
    "Missing Skills",
    "All Extracted Skills",
    "Summary Report",
]


def candidates_to_csv_string(candidates: List[Dict[str, Any]]) -> str:
    """Serialize ranked candidate dictionaries into a UTF-8 CSV string."""
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(CSV_HEADERS)

    for c in candidates:
        writer.writerow([
            c.get("rank", ""),
            c.get("candidate_name", ""),
            c.get("filename", ""),
            c.get("email") or "",
            c.get("phone") or "",
            c.get("overall_score", 0.0),
            c.get("match_tier", ""),
            c.get("skill_match_score", 0.0),
            c.get("tfidf_score", 0.0),
            c.get("experience_score", 0.0),
            c.get("estimated_years_experience") if c.get("estimated_years_experience") is not None else "",
            "; ".join(c.get("matched_skills", [])),
            "; ".join(c.get("missing_skills", [])),
            "; ".join(c.get("all_skills", [])),
            c.get("summary_report", ""),
        ])

    return output.getvalue()

