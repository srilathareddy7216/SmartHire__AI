"""
TF-IDF vectorization helpers shared by the classifier, recommender, and
clustering modules.
"""
from __future__ import annotations

import joblib
import scipy.sparse as sp
from sklearn.feature_extraction.text import TfidfVectorizer

from src import config


def fit_tfidf(texts, max_features=20_000, ngram_range=(1, 2), min_df=2) -> TfidfVectorizer:
    vectorizer = TfidfVectorizer(
        max_features=max_features,
        ngram_range=ngram_range,
        min_df=min_df,
        stop_words="english",
        sublinear_tf=True,
    )
    vectorizer.fit(texts)
    return vectorizer


def save_vectorizer(vectorizer: TfidfVectorizer, path) -> None:
    joblib.dump(vectorizer, path)


def load_vectorizer(path) -> TfidfVectorizer:
    return joblib.load(path)


def save_sparse_matrix(matrix, path) -> None:
    sp.save_npz(path, matrix)


def load_sparse_matrix(path):
    return sp.load_npz(path)
