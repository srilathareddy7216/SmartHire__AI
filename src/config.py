"""
Central configuration for SmartHire.
All paths and tunable constants live here so nothing is hard-coded elsewhere.
"""
from pathlib import Path

# ---------------------------------------------------------------------------
# Directories
# ---------------------------------------------------------------------------
ROOT_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = ROOT_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
INTERIM_DIR = DATA_DIR / "interim"
PROCESSED_DIR = DATA_DIR / "processed"

MODELS_DIR = ROOT_DIR / "models"
REPORTS_DIR = ROOT_DIR / "reports"
FIGURES_DIR = REPORTS_DIR / "figures"

for d in [RAW_DIR, INTERIM_DIR, PROCESSED_DIR, MODELS_DIR, FIGURES_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Raw dataset file names (place your own files in data/raw with these names,
# or edit the names below to match whatever you download)
# ---------------------------------------------------------------------------
RESUME_CSV = RAW_DIR / "Resume_25.csv"
NAUKRI_CSV = RAW_DIR / "naukri.csv"
LINKEDIN_CSV = RAW_DIR / "Linkedin_dataset.csv"

# ---------------------------------------------------------------------------
# Processed artifact file names
# ---------------------------------------------------------------------------
JOB_CORPUS_PARQUET = PROCESSED_DIR / "job_corpus.parquet"
JOB_CORPUS_CSV = PROCESSED_DIR / "job_corpus.csv"
RESUME_CLEAN_PARQUET = PROCESSED_DIR / "resumes_clean.parquet"
RESUME_CLEAN_CSV = PROCESSED_DIR / "resumes_clean.csv"

# Slim, compressed version of the job corpus that actually ships with the app
# (drops training-only columns and truncates long descriptions so the repo
# stays small and Streamlit Cloud loads fast). This is the file the app reads.
JOB_CORPUS_APP = PROCESSED_DIR / "job_corpus_app.csv.gz"
APP_DESCRIPTION_MAX_CHARS = 1500

# ---------------------------------------------------------------------------
# Model artifact file names
# ---------------------------------------------------------------------------
CLASSIFIER_MODEL = MODELS_DIR / "resume_classifier.pkl"
CLASSIFIER_VECTORIZER = MODELS_DIR / "resume_tfidf_vectorizer.pkl"
CLASSIFIER_LABEL_ENCODER = MODELS_DIR / "label_encoder.pkl"

JOB_VECTORIZER = MODELS_DIR / "job_tfidf_vectorizer.pkl"
JOB_TFIDF_MATRIX = MODELS_DIR / "job_tfidf_matrix.npz"

KMEANS_MODEL = MODELS_DIR / "job_kmeans.pkl"
PCA_MODEL = MODELS_DIR / "job_pca.pkl"

FIT_PREDICTOR_MODEL = MODELS_DIR / "fit_predictor.pkl"

METRICS_JSON = REPORTS_DIR / "metrics.json"

# ---------------------------------------------------------------------------
# Modelling constants
# ---------------------------------------------------------------------------
RANDOM_STATE = 42

# TF-IDF
TFIDF_MAX_FEATURES_JOBS = 25_000
TFIDF_MAX_FEATURES_RESUME = 15_000
TFIDF_NGRAM_RANGE = (1, 2)
TFIDF_MIN_DF = 2

# Classifier
CLASSIFIER_TEST_SIZE = 0.2

# Clustering
KMEANS_K_RANGE = range(4, 15)
KMEANS_DEFAULT_K = 10

# Recommender
TOP_N_DEFAULT = 10

# Sample cap so the demo stays fast on Streamlit Community Cloud's free tier.
# Set to None to use the full dataset (recommended for local / final training).
MAX_JOBS_FOR_INDEX = None
