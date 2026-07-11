"""
Text cleaning, skill parsing, and job-corpus merging utilities.

This module turns the three raw datasets (Naukri, LinkedIn, Resume) into:
  1. A single clean "job corpus" with columns:
     title, company, location, skills, description, experience, source
  2. A cleaned resume dataframe with columns: category, resume_text, skills

All functions are pure (no side effects) so they are easy to unit-test and
reuse from notebooks, scripts, and the Streamlit app.
"""
from __future__ import annotations

import re
from typing import Iterable

import pandas as pd

# ---------------------------------------------------------------------------
# Generic text cleaning
# ---------------------------------------------------------------------------
_URL_RE = re.compile(r"http\S+|www\.\S+")
_EMAIL_RE = re.compile(r"\S+@\S+")
_MULTISPACE_RE = re.compile(r"\s+")
_NON_ALNUM_RE = re.compile(r"[^a-zA-Z0-9+#.\-\s]")


def clean_text(text: str) -> str:
    """Lowercase, strip URLs/emails, remove noisy punctuation, collapse whitespace.

    Keeps '+', '#', '.', '-' because they matter for tech tokens like
    'c++', 'c#', 'node.js', 'full-stack'.
    """
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = _URL_RE.sub(" ", text)
    text = _EMAIL_RE.sub(" ", text)
    text = text.encode("ascii", "ignore").decode("ascii")  # drop non-ascii junk (â€¢ etc.)
    text = _NON_ALNUM_RE.sub(" ", text)
    text = _MULTISPACE_RE.sub(" ", text).strip()
    return text


def parse_skill_list(raw) -> list[str]:
    """Parse a 'skills' cell that may be:
    - a plain space/comma separated string (Naukri)
    - a numpy-array-repr string like "['a' 'b' 'c']" (LinkedIn)
    - an actual python list
    - NaN / missing
    Returns a clean list of lowercase skill strings.
    """
    if raw is None:
        return []
    if isinstance(raw, float):  # NaN
        return []
    if isinstance(raw, (list, tuple, set)):
        items = list(raw)
    elif isinstance(raw, str):
        s = raw.strip()
        if s.startswith("[") and s.endswith("]"):
            # Extract every quoted substring directly. This handles both
            # real python-list-of-strings ("['a', 'b']") and numpy's
            # whitespace-separated repr ("['a' 'b'\n 'c']") uniformly.
            # (ast.literal_eval is deliberately NOT used here: Python's
            # adjacent-string-literal concatenation, e.g. 'a' 'b' -> 'ab',
            # would silently merge numpy-repr tokens into one garbled string.)
            matches = re.findall(r"'([^']*)'|\"([^\"]*)\"", s)
            items = [a or b for a, b in matches]
            if not items:
                # Not actually a bracketed string list -> fall back to raw content
                items = [s.strip("[]")]
        elif "," in s:
            items = s.split(",")
        else:
            # Naukri-style: space separated skill tags with no reliable multi-word
            # delimiter. Splitting on whitespace loses a few multi-word skill
            # names, but treating the whole thing as one giant blob makes
            # skill-gap chips and matching useless downstream, so per-token is
            # the more usable tradeoff here.
            items = s.split()
    else:
        items = []

    cleaned = []
    for it in items:
        it = str(it).strip().lower()
        it = _MULTISPACE_RE.sub(" ", it)
        if it and it not in cleaned:
            cleaned.append(it)
    return cleaned


def skills_to_text(skills: Iterable[str]) -> str:
    return " ".join(skills)


# ---------------------------------------------------------------------------
# Experience parsing ("2-7 Yrs" -> (2, 7))
# ---------------------------------------------------------------------------
_EXP_RE = re.compile(r"(\d+)\s*-\s*(\d+)")


def parse_experience_range(raw: str) -> tuple[float, float]:
    if not isinstance(raw, str):
        return (0.0, 0.0)
    m = _EXP_RE.search(raw)
    if m:
        return (float(m.group(1)), float(m.group(2)))
    nums = re.findall(r"\d+", raw)
    if nums:
        v = float(nums[0])
        return (v, v)
    return (0.0, 0.0)


def extract_years_from_resume(text: str) -> float:
    """Best-effort extraction of total years of experience mentioned in a resume."""
    if not isinstance(text, str):
        return 0.0
    matches = re.findall(r"(\d+(?:\.\d+)?)\s*\+?\s*(?:years|yrs|yr)\b", text.lower())
    years = [float(m) for m in matches if float(m) <= 45]
    return max(years) if years else 0.0


# ---------------------------------------------------------------------------
# Dataset-specific loaders / cleaners
# ---------------------------------------------------------------------------
def clean_naukri(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df = df.rename(columns={"job-description": "description"})
    df["skills_list"] = df["skills"].apply(parse_skill_list)
    df["skills_text"] = df["skills_list"].apply(skills_to_text)
    df["exp_min"], df["exp_max"] = zip(*df["experience"].apply(parse_experience_range))
    df["source"] = "naukri"
    keep = ["title", "company", "location", "skills_text", "skills_list",
            "description", "experience", "exp_min", "exp_max", "salary", "source"]
    for c in keep:
        if c not in df.columns:
            df[c] = ""
    return df[keep]


def clean_linkedin(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["skills_list"] = df["skills"].apply(parse_skill_list)
    df["skills_text"] = df["skills_list"].apply(skills_to_text)
    df["company"] = ""
    df["location"] = ""
    df["experience"] = ""
    df["exp_min"] = 0.0
    df["exp_max"] = 0.0
    df["salary"] = "Not disclosed"
    df["source"] = "linkedin"
    keep = ["title", "company", "location", "skills_text", "skills_list",
            "description", "experience", "exp_min", "exp_max", "salary", "source"]
    return df[keep]


def build_job_corpus(naukri_df: pd.DataFrame, linkedin_df: pd.DataFrame) -> pd.DataFrame:
    """Merge Naukri + LinkedIn postings into one unified, clean job corpus."""
    a = clean_naukri(naukri_df)
    b = clean_linkedin(linkedin_df)
    corpus = pd.concat([a, b], ignore_index=True)

    corpus["title"] = corpus["title"].fillna("").astype(str).str.strip()
    corpus["description"] = corpus["description"].fillna("").astype(str)
    corpus = corpus[(corpus["title"] != "") & (corpus["description"].str.len() > 10)]

    corpus["clean_title"] = corpus["title"].apply(clean_text)
    corpus["clean_description"] = corpus["description"].apply(clean_text)
    corpus["clean_skills"] = corpus["skills_text"].apply(clean_text)

    # The single field the recommender/clustering will vectorize.
    corpus["search_text"] = (
        (corpus["clean_title"] + " ") * 3  # up-weight the title
        + (corpus["clean_skills"] + " ") * 2  # up-weight skills
        + corpus["clean_description"]
    ).str.strip()

    corpus = corpus.drop_duplicates(subset=["title", "description"]).reset_index(drop=True)
    corpus["job_id"] = corpus.index.astype(str)
    return corpus


def clean_resumes(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df = df.rename(columns={"Category": "category", "Resume": "resume_text"})
    df["resume_text"] = df["resume_text"].fillna("").astype(str)
    df = df[df["resume_text"].str.len() > 20].reset_index(drop=True)
    df["clean_text"] = df["resume_text"].apply(clean_text)
    df["years_experience"] = df["resume_text"].apply(extract_years_from_resume)
    return df[["category", "resume_text", "clean_text", "years_experience"]]
