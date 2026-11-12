"""Command-line interface for Resume Screening AI."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import List

from src.exporter import candidates_to_csv_string
from src.parser import ParsedResume, parse_resume_bytes
from src.scorer import rank_resumes


def collect_resume_files(inputs: List[str]) -> List[Path]:
    files: List[Path] = []
    for item in inputs:
        p = Path(item)
        if p.is_dir():
            for ext in ("*.pdf", "*.txt", "*.md"):
                files.extend(sorted(p.glob(ext)))
        elif p.is_file():
            files.append(p)
        else:
            print(f"[WARN] Path not found: {item}")
    return files


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Resume Screening AI — Parse, score, and rank resumes against a job description."
    )
    parser.add_argument(
        "--jd",
        required=True,
        help="Path to the job description text file.",
    )
    parser.add_argument(
        "--resumes",
        nargs="+",
        required=True,
        help="One or more resume files (.pdf/.txt) or directories containing resumes.",
    )
    parser.add_argument(
        "--out",
        default=None,
        help="Optional output path to save the candidate ranking CSV report.",
    )
    args = parser.parse_args()

    jd_path = Path(args.jd)
    if not jd_path.is_file():
        raise SystemExit(f"Job description file not found: {jd_path}")

    job_description = jd_path.read_text(encoding="utf-8")
    resume_paths = collect_resume_files(args.resumes)
    if not resume_paths:
        raise SystemExit("No valid resume files (.pdf or .txt) found.")

    parsed_resumes: List[ParsedResume] = []
    for path in resume_paths:
        try:
            parsed = parse_resume_bytes(path.read_bytes(), path.name)
            parsed_resumes.append(parsed)
        except Exception as exc:
            print(f"[WARN] Skipping {path.name}: {exc}")

    results = rank_resumes(job_description, parsed_resumes)
    print(f"\nJD Required Skills ({len(results['jd_skills'])}): {', '.join(results['jd_skills']) or 'None detected'}")
    print("=" * 88)
    print(f"{'Rank':<5} {'Candidate':<24} {'Score':<8} {'Skill%':<8} {'TF-IDF%':<9} {'Tier'}")
    print("-" * 88)

    for c in results["candidates"]:
        print(
            f"#{c['rank']:<4} {c['candidate_name'][:23]:<24} "
            f"{c['overall_score']:<7.1f}% {c['skill_match_score']:<7.1f}% "
            f"{c['tfidf_score']:<8.1f}% {c['match_tier']}"
        )
        print(f"      Summary: {c['summary_report']}")
        print("-" * 88)

    if args.out:
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(candidates_to_csv_string(results["candidates"]), encoding="utf-8")
        print(f"\nCSV report saved to: {out_path}")


if __name__ == "__main__":
    main()

