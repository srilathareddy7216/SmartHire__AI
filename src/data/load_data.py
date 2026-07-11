"""
Raw dataset loaders. Keeps pandas.read_csv quirks (encoding, bad lines,
mixed dtypes) in one place.
"""
from __future__ import annotations

import pandas as pd

from src import config


def load_resumes(path=None) -> pd.DataFrame:
    path = path or config.RESUME_CSV
    df = pd.read_csv(path, engine="python", on_bad_lines="skip", encoding="utf-8", encoding_errors="ignore")
    return df


def load_naukri(path=None) -> pd.DataFrame:
    path = path or config.NAUKRI_CSV
    df = pd.read_csv(path, engine="python", on_bad_lines="skip", encoding="utf-8", encoding_errors="ignore")
    return df


def load_linkedin(path=None) -> pd.DataFrame:
    path = path or config.LINKEDIN_CSV
    df = pd.read_csv(path, engine="python", on_bad_lines="skip", encoding="utf-8", encoding_errors="ignore")
    return df
