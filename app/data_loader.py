"""
Cached loaders for every artifact the Streamlit app needs. Splitting these
out from streamlit_app.py keeps the UI file readable and makes the caching
boundaries explicit.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import scipy.sparse as sp
import streamlit as st

APP_DIR = Path(__file__).resolve().parent
ROOT_DIR = APP_DIR.parent
sys.path.insert(0, str(ROOT_DIR))

from src import config  # noqa: E402


@st.cache_data(show_spinner=False)
def load_job_corpus() -> pd.DataFrame:
    df = pd.read_csv(config.JOB_CORPUS_APP, compression="gzip")
    for c in ["description", "clean_title", "clean_skills", "skills_text", "company", "location"]:
        df[c] = df[c].fillna("")
    return df


@st.cache_resource(show_spinner=False)
def load_job_index():
    vectorizer = joblib.load(config.JOB_VECTORIZER)
    matrix = sp.load_npz(config.JOB_TFIDF_MATRIX)
    return vectorizer, matrix


@st.cache_resource(show_spinner=False)
def load_classifier_bundle():
    model = joblib.load(config.CLASSIFIER_MODEL)
    vectorizer = joblib.load(config.CLASSIFIER_VECTORIZER)
    label_encoder = joblib.load(config.CLASSIFIER_LABEL_ENCODER)
    return model, vectorizer, label_encoder


@st.cache_resource(show_spinner=False)
def load_clustering_bundle():
    kmeans = joblib.load(config.KMEANS_MODEL)
    svd = joblib.load(config.PCA_MODEL)
    return kmeans, svd


@st.cache_resource(show_spinner=False)
def load_fit_predictor():
    return joblib.load(config.FIT_PREDICTOR_MODEL)


@st.cache_data(show_spinner=False)
def load_cluster_labels() -> np.ndarray:
    return np.load(config.PROCESSED_DIR / "job_cluster_labels.npy")


@st.cache_data(show_spinner=False)
def load_coords_2d() -> np.ndarray:
    return np.load(config.PROCESSED_DIR / "job_coords_2d.npy")


@st.cache_data(show_spinner=False)
def load_cluster_terms() -> dict:
    path = config.PROCESSED_DIR / "cluster_terms.json"
    if not path.exists():
        return {}
    with open(path) as f:
        return json.load(f)


@st.cache_data(show_spinner=False)
def load_metrics() -> dict:
    if not config.METRICS_JSON.exists():
        return {}
    with open(config.METRICS_JSON) as f:
        return json.load(f)


def artifacts_ready() -> bool:
    required = [
        config.JOB_CORPUS_APP, config.JOB_VECTORIZER, config.JOB_TFIDF_MATRIX,
        config.CLASSIFIER_MODEL, config.CLASSIFIER_VECTORIZER, config.CLASSIFIER_LABEL_ENCODER,
        config.KMEANS_MODEL, config.PCA_MODEL,
    ]
    return all(p.exists() for p in required)
