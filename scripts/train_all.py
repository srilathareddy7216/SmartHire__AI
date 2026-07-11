"""
End-to-end training pipeline for SmartHire.

Run this once (from the project root) after placing your raw CSVs in
data/raw/ :

    python scripts/train_all.py

It will:
  1. Load & clean the Naukri + LinkedIn datasets into one job corpus
  2. Load & clean the Resume dataset
  3. Train the resume category classifier (Model A)
  4. Build the TF-IDF job recommender index (core unsupervised engine)
  5. Fit K-Means job clustering + 2D projection (for the Explore Jobs page)
  6. Train the optional fit/shortlisting predictor (Model B, weak-supervised)
  7. Save every artifact to models/ and data/processed/, and write
     reports/metrics.json for the Streamlit app to display

Each step prints progress and timing so you can see exactly what's happening.
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src import config
from src.data import load_data, preprocess
from src.models import classifier, recommender, clustering, fit_predictor
from src.evaluate import save_metrics


def step(msg):
    print(f"\n{'='*70}\n{msg}\n{'='*70}")


def main():
    t0 = time.time()
    all_metrics = {}

    # ------------------------------------------------------------------
    step("STEP 1/6 — Loading raw datasets")
    naukri_raw = load_data.load_naukri()
    linkedin_raw = load_data.load_linkedin()
    resumes_raw = load_data.load_resumes()
    print(f"Naukri: {len(naukri_raw):,} rows | LinkedIn: {len(linkedin_raw):,} rows | "
          f"Resumes: {len(resumes_raw):,} rows")

    # ------------------------------------------------------------------
    step("STEP 2/6 — Cleaning & building the unified job corpus")
    job_corpus = preprocess.build_job_corpus(naukri_raw, linkedin_raw)
    if config.MAX_JOBS_FOR_INDEX:
        job_corpus = job_corpus.sample(
            n=min(config.MAX_JOBS_FOR_INDEX, len(job_corpus)), random_state=config.RANDOM_STATE
        ).reset_index(drop=True)
        job_corpus["job_id"] = job_corpus.index.astype(str)
    resumes_clean = preprocess.clean_resumes(resumes_raw)
    print(f"Job corpus: {len(job_corpus):,} postings | Clean resumes: {len(resumes_clean):,}")

    job_corpus.to_csv(config.JOB_CORPUS_CSV, index=False)
    resumes_clean.to_csv(config.RESUME_CLEAN_CSV, index=False)

    # Slim, compressed version that ships with the app / gets committed to git.
    app_cols = ["job_id", "title", "company", "location", "skills_text", "skills_list",
                "description", "experience", "exp_min", "exp_max", "salary", "source",
                "clean_title", "clean_skills"]
    app_corpus = job_corpus[app_cols].copy()
    app_corpus["description"] = app_corpus["description"].str.slice(0, config.APP_DESCRIPTION_MAX_CHARS)
    app_corpus.to_csv(config.JOB_CORPUS_APP, index=False, compression="gzip")
    print(f"Slim app corpus saved: {config.JOB_CORPUS_APP.name} "
          f"({config.JOB_CORPUS_APP.stat().st_size / 1e6:.1f} MB)")

    try:
        job_corpus.to_parquet(config.JOB_CORPUS_PARQUET, index=False)
        resumes_clean.to_parquet(config.RESUME_CLEAN_PARQUET, index=False)
    except ImportError:
        print("(pyarrow not installed - skipped .parquet, CSV files saved instead.)")
    print("Saved cleaned datasets to data/processed/ (full versions, git-ignored)")

    # ------------------------------------------------------------------
    step("STEP 3/6 — Training Model A: Resume Category Classifier")
    model, vectorizer, label_encoder, clf_metrics = classifier.train_classifier(
        resumes_clean, model_type="logreg"
    )
    classifier.save_classifier(model, vectorizer, label_encoder)
    all_metrics["classifier"] = clf_metrics
    print(f"Accuracy: {clf_metrics['accuracy']:.3f} | F1 (macro): {clf_metrics['f1_macro']:.3f}")

    # ------------------------------------------------------------------
    step("STEP 4/6 — Building the Job Recommender (TF-IDF + cosine similarity)")
    job_vectorizer, job_matrix = recommender.build_job_index(job_corpus)
    recommender.save_job_index(job_vectorizer, job_matrix)
    print(f"Job TF-IDF matrix: {job_matrix.shape[0]:,} jobs x {job_matrix.shape[1]:,} terms")

    sample_scores = []
    for cat in resumes_clean["category"].unique()[:8]:
        sample_text = resumes_clean[resumes_clean["category"] == cat]["clean_text"].iloc[0]
        p_at_10 = recommender.precision_at_k(
            job_corpus, job_vectorizer, job_matrix, "category", cat, sample_text, k=10
        )
        sample_scores.append(p_at_10)
    all_metrics["recommender"] = {
        "avg_precision_at_10_sample": float(sum(sample_scores) / len(sample_scores)) if sample_scores else None,
        "n_jobs_indexed": int(job_matrix.shape[0]),
        "n_terms": int(job_matrix.shape[1]),
    }
    print(f"Sampled Precision@10 across categories: {all_metrics['recommender']['avg_precision_at_10_sample']:.3f}")

    # ------------------------------------------------------------------
    step("STEP 5/6 — Clustering jobs into role families (K-Means + SVD)")
    k_eval = clustering.evaluate_k_range(job_matrix, k_range=range(6, 13), sample_size=4000)
    best_k = int(k_eval.loc[k_eval["silhouette"].idxmax(), "k"])
    print(f"Best k by silhouette score: {best_k}")
    print(k_eval.to_string(index=False))

    kmeans = clustering.fit_kmeans(job_matrix, k=best_k)
    svd, coords_2d = clustering.fit_pca_2d(job_matrix)
    clustering.save_clustering(kmeans, svd)

    import numpy as np
    np.save(config.PROCESSED_DIR / "job_cluster_labels.npy", kmeans.labels_)
    np.save(config.PROCESSED_DIR / "job_coords_2d.npy", coords_2d)

    cluster_terms = clustering.top_terms_per_cluster(kmeans, job_vectorizer, top_n=12)
    import json
    with open(config.PROCESSED_DIR / "cluster_terms.json", "w") as f:
        json.dump({str(k): v for k, v in cluster_terms.items()}, f, indent=2)

    all_metrics["clustering"] = {
        "best_k": best_k,
        "silhouette_at_best_k": float(k_eval.loc[k_eval["k"] == best_k, "silhouette"].iloc[0]),
        "k_eval_table": k_eval.to_dict("records"),
    }

    # ------------------------------------------------------------------
    step("STEP 6/6 — Training Model B: Fit / Shortlisting Predictor (weak-supervised)")
    pairs = fit_predictor.generate_training_pairs(
        resumes_clean, job_corpus, job_vectorizer, job_matrix, n_pairs=6000
    )
    fp_model, fp_metrics = fit_predictor.train_fit_predictor(pairs, model_type="logreg")
    fit_predictor.save_fit_predictor(fp_model)
    all_metrics["fit_predictor"] = fp_metrics
    print(f"ROC-AUC: {fp_metrics['roc_auc']:.3f} | F1: {fp_metrics['f1']:.3f} | "
          f"Positive rate: {fp_metrics['positive_rate']:.3f}")

    # ------------------------------------------------------------------
    save_metrics(all_metrics)
    elapsed = time.time() - t0
    step(f"DONE in {elapsed/60:.1f} minutes. All artifacts saved to models/ and data/processed/.")
    print("You can now run:  streamlit run app/streamlit_app.py")


if __name__ == "__main__":
    main()
