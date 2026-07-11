"""
Feature engineering for the fit/shortlisting predictor: quantifies how well
a resume matches a specific job posting.
"""
from __future__ import annotations

import re

_TOKEN_RE = re.compile(r"[a-zA-Z][a-zA-Z0-9+#.\-]{1,}")


def tokenize(text: str) -> set[str]:
    if not isinstance(text, str):
        return set()
    return set(_TOKEN_RE.findall(text.lower()))


def skill_overlap_ratio(resume_text: str, job_skills_text: str) -> float:
    """Fraction of the job's required skill tokens that also appear in the resume."""
    job_tokens = tokenize(job_skills_text)
    if not job_tokens:
        return 0.0
    resume_tokens = tokenize(resume_text)
    overlap = job_tokens & resume_tokens
    return len(overlap) / len(job_tokens)


def missing_skills(resume_text: str, job_skills: list[str]) -> list[str]:
    """Skills required by the job that are NOT found (as substrings) in the resume."""
    resume_lower = (resume_text or "").lower()
    missing = []
    for skill in job_skills:
        s = skill.strip().lower()
        if not s:
            continue
        # A skill "counts" as present if all its significant words appear in resume.
        words = [w for w in re.split(r"\s+", s) if len(w) > 1]
        if not words:
            continue
        if all(w in resume_lower for w in words):
            continue
        missing.append(skill)
    return missing


def experience_match_score(resume_years: float, exp_min: float, exp_max: float) -> float:
    """1.0 if the candidate's years of experience fall inside the job's required
    range, decaying smoothly outside it."""
    if exp_max <= 0:
        return 0.5  # unknown requirement -> neutral
    if exp_min <= resume_years <= exp_max:
        return 1.0
    distance = min(abs(resume_years - exp_min), abs(resume_years - exp_max))
    return max(0.0, 1.0 - distance / 5.0)


def build_match_feature_vector(resume_text, resume_years, job_row, text_similarity: float) -> list[float]:
    """Assemble the numeric feature vector used by the fit predictor model."""
    overlap = skill_overlap_ratio(resume_text, job_row.get("clean_skills", ""))
    exp_score = experience_match_score(resume_years, job_row.get("exp_min", 0.0), job_row.get("exp_max", 0.0))
    title_overlap = skill_overlap_ratio(resume_text, job_row.get("clean_title", ""))
    return [text_similarity, overlap, exp_score, title_overlap]


FEATURE_NAMES = ["text_similarity", "skill_overlap", "experience_match", "title_overlap"]
