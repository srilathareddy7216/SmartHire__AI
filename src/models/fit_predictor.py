"""
MODEL B (optional) - Shortlisting / Fit Predictor.

There is no ground-truth "was this candidate shortlisted for this job"
label in any public dataset, so this model is trained with WEAK SUPERVISION:
for a large sample of (resume, job) pairs we compute the same match features
the model will see at inference time (text similarity, skill overlap,
experience match, title overlap) and derive a heuristic pseudo-label
  fit = 1  if text_similarity >= 0.18 AND skill_overlap >= 0.25
  fit = 0  otherwise
This is a standard, honest weak-supervision technique for bootstrapping a
supervised model when no labels exist -- it is documented here and again in
the README so nobody mistakes it for real hiring-outcome data. The model
(Logistic Regression, optionally compared with XGBoost/GradientBoosting)
then learns a *smooth, calibrated probability* out of these noisy 0/1 rules,
which is what makes it useful: instead of a hard threshold, the UI gets a
continuous fit score plus a probability the user can interpret.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import joblib
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, precision_score, recall_score, f1_score
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.model_selection import train_test_split

from src import config
from src.features.match_features import build_match_feature_vector, FEATURE_NAMES


def generate_training_pairs(resumes_df: pd.DataFrame, job_corpus: pd.DataFrame,
                             vectorizer, job_matrix, n_pairs: int = 6000,
                             random_state: int = config.RANDOM_STATE) -> pd.DataFrame:
    """Sample random (resume, job) pairs, compute match features + a weak label."""
    rng = np.random.default_rng(random_state)
    n_resumes = len(resumes_df)
    n_jobs = len(job_corpus)

    resume_idx = rng.integers(0, n_resumes, size=n_pairs)
    job_idx = rng.integers(0, n_jobs, size=n_pairs)

    resume_texts = resumes_df["clean_text"].values
    resume_years = resumes_df["years_experience"].values

    resume_vecs = vectorizer.transform(resume_texts[resume_idx])
    job_vecs = job_matrix[job_idx]
    sims = cosine_similarity(resume_vecs, job_vecs).diagonal()

    rows = []
    for i, (r_i, j_i, sim) in enumerate(zip(resume_idx, job_idx, sims)):
        job_row = job_corpus.iloc[j_i]
        feats = build_match_feature_vector(resume_texts[r_i], resume_years[r_i], job_row, sim)
        rows.append(feats)

    df = pd.DataFrame(rows, columns=FEATURE_NAMES)

    # Data-driven weak label: combine normalized text similarity + skill overlap
    # into one composite score, then label the top quartile as "fit" (1). Using
    # relative percentiles (instead of fixed absolute thresholds) makes this
    # robust to any corpus size/diversity, since raw cosine-similarity scale
    # shifts with vocabulary size and how heterogeneous the job corpus is.
    sim_rank = df["text_similarity"].rank(pct=True)
    overlap_rank = df["skill_overlap"].rank(pct=True)
    composite = 0.6 * sim_rank + 0.4 * overlap_rank
    threshold = composite.quantile(0.75)
    df["fit_label"] = (composite >= threshold).astype(int)
    return df


def train_fit_predictor(pairs_df: pd.DataFrame, model_type: str = "logreg"):
    X = pairs_df[FEATURE_NAMES].values
    y = pairs_df["fit_label"].values

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=config.RANDOM_STATE, stratify=y
    )

    if model_type == "gboost":
        model = GradientBoostingClassifier(random_state=config.RANDOM_STATE)
    else:
        model = LogisticRegression(max_iter=1000, class_weight="balanced")

    model.fit(X_train, y_train)
    y_prob = model.predict_proba(X_test)[:, 1]
    y_pred = (y_prob >= 0.5).astype(int)

    metrics = {
        "model_type": model_type,
        "roc_auc": float(roc_auc_score(y_test, y_prob)) if len(set(y_test)) > 1 else None,
        "precision": float(precision_score(y_test, y_pred, zero_division=0)),
        "recall": float(recall_score(y_test, y_pred, zero_division=0)),
        "f1": float(f1_score(y_test, y_pred, zero_division=0)),
        "n_train": int(len(y_train)),
        "n_test": int(len(y_test)),
        "positive_rate": float(y.mean()),
    }
    return model, metrics


def save_fit_predictor(model) -> None:
    joblib.dump(model, config.FIT_PREDICTOR_MODEL)


def load_fit_predictor():
    return joblib.load(config.FIT_PREDICTOR_MODEL)


def predict_fit(model, resume_text: str, resume_years: float, job_row, text_similarity: float) -> float:
    feats = build_match_feature_vector(resume_text, resume_years, job_row, text_similarity)
    prob = model.predict_proba([feats])[0, 1]
    return float(prob)
