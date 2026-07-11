"""
DISCOVERY - Job / role clustering.
K-Means over the job TF-IDF vectors to find natural job families, with the
elbow method + silhouette score to help choose k, and PCA for 2D visualization.
"""
from __future__ import annotations

import joblib
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA, TruncatedSVD
from sklearn.metrics import silhouette_score

from src import config


def evaluate_k_range(job_matrix, k_range=config.KMEANS_K_RANGE, sample_size: int = 5000, random_state=42):
    """Compute inertia + silhouette for a range of k values (on a sample for
    speed on large corpora). Returns a DataFrame with columns k, inertia, silhouette."""
    n = job_matrix.shape[0]
    rng = np.random.default_rng(random_state)
    if n > sample_size:
        idx = rng.choice(n, size=sample_size, replace=False)
        sample = job_matrix[idx]
    else:
        sample = job_matrix

    rows = []
    for k in k_range:
        km = KMeans(n_clusters=k, random_state=random_state, n_init=10)
        labels = km.fit_predict(sample)
        sil = silhouette_score(sample, labels, sample_size=min(2000, sample.shape[0]))
        rows.append({"k": k, "inertia": km.inertia_, "silhouette": sil})
    return pd.DataFrame(rows)


def fit_kmeans(job_matrix, k: int = config.KMEANS_DEFAULT_K, random_state=config.RANDOM_STATE) -> KMeans:
    km = KMeans(n_clusters=k, random_state=random_state, n_init=10)
    km.fit(job_matrix)
    return km


def fit_pca_2d(job_matrix, random_state=config.RANDOM_STATE):
    """TruncatedSVD works directly on sparse TF-IDF matrices (PCA needs dense)."""
    svd = TruncatedSVD(n_components=2, random_state=random_state)
    coords = svd.fit_transform(job_matrix)
    return svd, coords


def top_terms_per_cluster(kmeans: KMeans, vectorizer, top_n: int = 10) -> dict[int, list[str]]:
    order_centroids = kmeans.cluster_centers_.argsort()[:, ::-1]
    terms = np.array(vectorizer.get_feature_names_out())
    result = {}
    for i in range(kmeans.n_clusters):
        result[i] = terms[order_centroids[i, :top_n]].tolist()
    return result


def save_clustering(kmeans: KMeans, svd) -> None:
    joblib.dump(kmeans, config.KMEANS_MODEL)
    joblib.dump(svd, config.PCA_MODEL)


def load_clustering():
    kmeans = joblib.load(config.KMEANS_MODEL)
    svd = joblib.load(config.PCA_MODEL)
    return kmeans, svd


def skill_gap_report(resume_text: str, cluster_terms: list[str], top_n: int = 12) -> dict:
    """Compare candidate's resume text against a cluster's top terms to build
    a simple skill-gap report."""
    resume_lower = (resume_text or "").lower()
    have, missing = [], []
    for term in cluster_terms[:top_n]:
        if term in resume_lower:
            have.append(term)
        else:
            missing.append(term)
    return {"have": have, "missing": missing}
