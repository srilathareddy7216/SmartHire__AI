"""
MODEL A - Resume Category Classifier
TF-IDF + Logistic Regression (multi-class) that predicts a candidate's job
domain (e.g. "INFORMATION-TECHNOLOGY", "HR", "SALES") from raw resume text.
"""
from __future__ import annotations

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.svm import LinearSVC

from src import config
from src.features.text_features import fit_tfidf, save_vectorizer, load_vectorizer


def train_classifier(resumes_df: pd.DataFrame, model_type: str = "logreg"):
    """Train the resume category classifier and return (model, vectorizer,
    label_encoder, metrics_dict)."""
    X_text = resumes_df["clean_text"].values
    y_raw = resumes_df["category"].values

    label_encoder = LabelEncoder()
    y = label_encoder.fit_transform(y_raw)

    X_train_text, X_test_text, y_train, y_test = train_test_split(
        X_text, y, test_size=config.CLASSIFIER_TEST_SIZE,
        random_state=config.RANDOM_STATE, stratify=y,
    )

    vectorizer = fit_tfidf(
        X_train_text,
        max_features=config.TFIDF_MAX_FEATURES_RESUME,
        ngram_range=config.TFIDF_NGRAM_RANGE,
        min_df=1,
    )
    X_train = vectorizer.transform(X_train_text)
    X_test = vectorizer.transform(X_test_text)

    if model_type == "random_forest":
        model = RandomForestClassifier(
            n_estimators=300, random_state=config.RANDOM_STATE, n_jobs=-1, class_weight="balanced"
        )
    elif model_type == "svm":
        model = LinearSVC(random_state=config.RANDOM_STATE, class_weight="balanced")
    else:
        model = LogisticRegression(
            max_iter=2000, random_state=config.RANDOM_STATE, class_weight="balanced", n_jobs=-1
        )

    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    metrics = {
        "model_type": model_type,
        "accuracy": float(accuracy_score(y_test, y_pred)),
        "precision_macro": float(precision_score(y_test, y_pred, average="macro", zero_division=0)),
        "recall_macro": float(recall_score(y_test, y_pred, average="macro", zero_division=0)),
        "f1_macro": float(f1_score(y_test, y_pred, average="macro", zero_division=0)),
        "confusion_matrix": confusion_matrix(y_test, y_pred).tolist(),
        "labels": label_encoder.classes_.tolist(),
        "classification_report": classification_report(
            y_test, y_pred, target_names=label_encoder.classes_, output_dict=True, zero_division=0
        ),
        "n_train": int(len(y_train)),
        "n_test": int(len(y_test)),
    }
    return model, vectorizer, label_encoder, metrics


def save_classifier(model, vectorizer, label_encoder) -> None:
    joblib.dump(model, config.CLASSIFIER_MODEL)
    save_vectorizer(vectorizer, config.CLASSIFIER_VECTORIZER)
    joblib.dump(label_encoder, config.CLASSIFIER_LABEL_ENCODER)


def load_classifier():
    model = joblib.load(config.CLASSIFIER_MODEL)
    vectorizer = load_vectorizer(config.CLASSIFIER_VECTORIZER)
    label_encoder = joblib.load(config.CLASSIFIER_LABEL_ENCODER)
    return model, vectorizer, label_encoder


def predict_category(clean_text: str, model, vectorizer, label_encoder, top_k: int = 3):
    """Return a list of (category, confidence) tuples, best first."""
    X = vectorizer.transform([clean_text])
    if hasattr(model, "predict_proba"):
        proba = model.predict_proba(X)[0]
        order = np.argsort(proba)[::-1][:top_k]
        return [(label_encoder.classes_[i], float(proba[i])) for i in order]
    else:
        # LinearSVC has no predict_proba; use decision_function as a pseudo-score
        scores = model.decision_function(X)[0]
        probs = np.exp(scores) / np.exp(scores).sum()
        order = np.argsort(probs)[::-1][:top_k]
        return [(label_encoder.classes_[i], float(probs[i])) for i in order]
