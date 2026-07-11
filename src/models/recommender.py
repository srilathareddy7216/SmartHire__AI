"""
CORE ENGINE - Content-based job recommender.
Vectorizes the job corpus with TF-IDF, then ranks jobs against a resume by
cosine similarity. Pure unsupervised vector-space model.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

from src import config
from src.features.text_features import (
    fit_tfidf,
    save_vectorizer,
    load_vectorizer,
    save_sparse_matrix,
    load_sparse_matrix,
)


def build_job_index(job_corpus: pd.DataFrame):
    """Fit a TF-IDF vectorizer over the job corpus's search_text and transform it."""
    vectorizer = fit_tfidf(
        job_corpus["search_text"].values,
        max_features=config.TFIDF_MAX_FEATURES_JOBS,
        ngram_range=config.TFIDF_NGRAM_RANGE,
        min_df=config.TFIDF_MIN_DF,
    )
    job_matrix = vectorizer.transform(job_corpus["search_text"].values)
    return vectorizer, job_matrix


def save_job_index(vectorizer, job_matrix) -> None:
    save_vectorizer(vectorizer, config.JOB_VECTORIZER)
    save_sparse_matrix(job_matrix, config.JOB_TFIDF_MATRIX)


def load_job_index():
    vectorizer = load_vectorizer(config.JOB_VECTORIZER)
    job_matrix = load_sparse_matrix(config.JOB_TFIDF_MATRIX)
    return vectorizer, job_matrix


def recommend_jobs(resume_clean_text: str, job_corpus: pd.DataFrame, vectorizer, job_matrix, top_n: int = 10):
    """Return the top-N most similar jobs to the given (already-cleaned) resume text.

    Output: a DataFrame slice of job_corpus with an added 'match_score' column
    (0-100), sorted best first.
    """
    resume_vec = vectorizer.transform([resume_clean_text])
    sims = cosine_similarity(resume_vec, job_matrix).flatten()
    top_idx = np.argsort(sims)[::-1][:top_n]

    result = job_corpus.iloc[top_idx].copy()
    result["similarity"] = sims[top_idx]
    result["match_score"] = (result["similarity"] * 100).round(1)
    return result.reset_index(drop=True)


def precision_at_k(job_corpus: pd.DataFrame, vectorizer, job_matrix, category_col: str,
                    query_category: str, query_text: str, k: int = 10) -> float:
    """Qualitative evaluation helper: treat jobs whose title contains keywords
    related to `query_category` as 'relevant', then measure Precision@K for a
    sample query. Used in the evaluation notebook."""
    recs = recommend_jobs(query_text, job_corpus, vectorizer, job_matrix, top_n=k)
    keyword = query_category.lower().split("-")[0]
    relevant = recs["clean_title"].str.contains(keyword, case=False, na=False)
    return float(relevant.mean())
