# 🧭 SmartHire — Resume-to-Job Matching & Career Guidance Engine

An end-to-end **classical machine learning** project (no LLMs, no generative AI, no live
scraping) that combines supervised and unsupervised techniques to recommend jobs, predict
shortlisting fit, and generate CV improvement reports — with a polished Streamlit web portal.

- **Model A (supervised):** Resume category classifier — TF-IDF + Logistic Regression
- **Model B (supervised, optional):** Shortlisting / fit predictor — engineered match features + Logistic Regression
- **Core engine (unsupervised):** Content-based job recommender — TF-IDF + cosine similarity
- **Discovery (unsupervised):** Job clustering — K-Means + elbow/silhouette + 2D visualization
- **Insight:** Skill-gap report comparing your resume to top matches and your closest job cluster
- **Stretch goal:** Rule-based "mentor" Q&A (not a chatbot / not an LLM)

This README assumes **zero prior setup** on your machine. Follow it top to bottom.

---

## 0. What you need before starting

1. **Python 3.11** installed (3.10–3.12 also work). Check with:
   ```bash
   python3 --version
   ```
   If you don't have Python, install it from [python.org](https://www.python.org/downloads/).
2. **Git** installed. Check with `git --version`. Install from [git-scm.com](https://git-scm.com/) if missing.
3. A **free GitHub account** ([github.com](https://github.com)).
4. A **free Streamlit Community Cloud account** ([share.streamlit.io](https://share.streamlit.io)) — sign in with your GitHub account when you get to deployment.
5. Your three dataset CSVs (you said you'll provide your own). This project expects, by default:
   - `Resume_25.csv` — columns `Category`, `Resume`
   - `naukri.csv` — columns `title`, `company`, `experience`, `salary`, `location`, `job-description`, `skills`
   - `Linkedin_dataset.csv` — columns `title`, `description`, `skills`

   **If your column names differ**, either rename the columns in your CSV to match the above,
   or edit `src/data/preprocess.py` (`clean_naukri`, `clean_linkedin`, `clean_resumes` functions) —
   they're short and clearly commented.

---

## 1. Project structure (already set up for you)

```
smarthire/
├── README.md                    <- you are here
├── requirements.txt              <- pinned dependencies
├── runtime.txt                   <- Python version for Streamlit Cloud
├── .gitignore
├── .streamlit/
│   └── config.toml               <- app theme colors
│
├── data/
│   ├── raw/                      <- PUT YOUR 3 CSV FILES HERE (gitignored, stays local)
│   ├── interim/                  <- (unused placeholder, kept for the brief's structure)
│   └── processed/                <- cleaned datasets get written here by the training script
│
├── notebooks/                    <- exploration notebooks (run with Jupyter, optional)
│   ├── 01_eda.ipynb
│   ├── 02_resume_classifier.ipynb
│   ├── 03_recommender.ipynb
│   ├── 04_clustering_topics.ipynb
│   └── 05_fit_predictor.ipynb
│
├── src/                          <- all reusable Python code (the actual ML pipeline)
│   ├── config.py                 <- every path & constant lives here
│   ├── data/
│   │   ├── load_data.py
│   │   └── preprocess.py
│   ├── features/
│   │   ├── text_features.py
│   │   └── match_features.py
│   ├── models/
│   │   ├── classifier.py         <- Model A
│   │   ├── recommender.py        <- core engine
│   │   ├── clustering.py         <- discovery
│   │   ├── fit_predictor.py      <- Model B
│   │   └── mentor.py             <- stretch goal
│   ├── parsing/
│   │   └── resume_parser.py      <- PDF/DOCX/TXT text extraction
│   └── evaluate.py
│
├── models/                       <- trained model files land here (.pkl, .npz) — committed to git
├── app/
│   ├── streamlit_app.py          <- the web portal (run this with `streamlit run`)
│   ├── data_loader.py            <- cached artifact loaders
│   └── theme.py                  <- custom CSS / visual design
│
├── reports/
│   ├── figures/                  <- (optional) exported plots
│   └── metrics.json              <- all model metrics, written by training, read by the app
│
├── scripts/
│   └── train_all.py              <- ONE COMMAND runs the entire ML pipeline
│
└── tests/
    └── test_features.py          <- basic unit tests
```

---

## 2. Local setup, step by step

Open a terminal and run these commands **one at a time**, from the folder that contains this
project (i.e. after you `cd` into the unzipped `smarthire/` folder).

### 2.1 Create and activate a virtual environment

**macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows (PowerShell):**
```powershell
python -m venv venv
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
venv\Scripts\Activate.ps1
```

You'll know it worked because your terminal prompt now starts with `(venv)`.
(Run this `activate` command again every time you open a new terminal for this project.)

### 2.2 Install dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```
This installs Streamlit, scikit-learn, pandas, Plotly, pdfplumber, python-docx, and everything
else the project needs. It takes 1-3 minutes.

### 2.3 Add your datasets

Copy your three CSV files into `data/raw/` so it looks like this:
```
data/raw/Resume_25.csv
data/raw/naukri.csv
data/raw/Linkedin_dataset.csv
```
(On macOS/Linux you can do this with `cp /path/to/your/file.csv data/raw/`, or just drag-and-drop
them in Finder/Explorer.)

> If your filenames are different, either rename them to match the above, or open
> `src/config.py` and change `RESUME_CSV`, `NAUKRI_CSV`, `LINKEDIN_CSV` to your actual filenames.

### 2.4 Train every model (one command)

```bash
python scripts/train_all.py
```

This single script:
1. Loads and cleans your 3 raw CSVs into one unified job corpus + a clean resume dataset
2. Trains the resume category classifier (Model A) and prints accuracy/F1
3. Builds the TF-IDF job recommender index (core engine)
4. Runs K-Means clustering with an elbow/silhouette search to pick k, and saves a 2D
   visualization projection
5. Trains the shortlisting/fit predictor (Model B) and prints ROC-AUC/F1
6. Saves every artifact into `models/` and `data/processed/`, and writes
   `reports/metrics.json` for the app to display

**Expect this to take anywhere from ~2 to ~15 minutes**, depending on your dataset size and
computer speed — it prints progress for every step, so you'll see exactly what's happening.

If it finishes without errors, you're ready for the next step.

### 2.5 Run the app locally

```bash
streamlit run app/streamlit_app.py
```

Your browser should open automatically to `http://localhost:8501`. If it doesn't, open that URL
manually. Try uploading a resume (PDF/DOCX/TXT) on the **Analyze My Resume** page.

Press `Ctrl+C` in the terminal to stop the app when you're done.

---

## 3. Running the notebooks (optional, for exploration/grading)

The notebooks in `notebooks/` mirror the pipeline in `scripts/train_all.py` but with extra
plots and explanations — useful for a project report or presentation.

```bash
pip install jupyter matplotlib seaborn
jupyter notebook notebooks/
```
Open each `.ipynb` file and run cells top to bottom. Run them **after** step 2.3 (raw CSVs in
`data/raw/`) — they load data the same way the training script does.

---

## 4. Running the tests

```bash
python -m pytest tests/ -v
```
or, without pytest:
```bash
python tests/test_features.py
```

---

## 5. Pushing this project to GitHub

From the project root (with your virtual environment activated):

```bash
git init
git add .
git commit -m "Initial commit: SmartHire ML project"
```

Now create a new **empty** repository on GitHub (don't initialize it with a README — you
already have one):
1. Go to [github.com/new](https://github.com/new)
2. Name it, e.g., `smarthire`
3. Leave "Add a README file" unchecked
4. Click **Create repository**

GitHub will show you a page with commands like this — copy YOUR repository's URL and run:

```bash
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/smarthire.git
git push -u origin main
```

**Important — what actually gets pushed:**
- ✅ All source code (`src/`, `app/`, `scripts/`, `notebooks/`, `tests/`)
- ✅ Trained model files (`models/*.pkl`, `models/*.npz`) — needed so the deployed app
  doesn't have to retrain from scratch
- ✅ The slim, compressed job corpus the app reads (`data/processed/job_corpus_app.csv.gz`)
- ✅ `reports/metrics.json`
- ❌ Your raw CSVs (`data/raw/*.csv`) — excluded by `.gitignore` on purpose, since they're
  large and are your own data. Anyone who clones the repo can still run the full pipeline
  themselves if they supply their own raw CSVs.
- ❌ The full (untrimmed) `data/processed/job_corpus.csv` — also large, and not needed at
  runtime; only the slim `.csv.gz` version is.

If `git push` is rejected for being too large, see **Troubleshooting → "push rejected, file
too large"** below.

---

## 6. Deploying to Streamlit Community Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub.
2. Click **"Create app"** (or **"New app"**).
3. Choose **"Deploy a public app from GitHub"**.
4. Fill in:
   - **Repository:** `YOUR-USERNAME/smarthire`
   - **Branch:** `main`
   - **Main file path:** `app/streamlit_app.py`
5. Click **"Deploy"**.

Streamlit Cloud will install everything from `requirements.txt` and launch your app. The first
deploy takes a few minutes. You'll get a public URL like
`https://YOUR-USERNAME-smarthire.streamlit.app` that you can share with anyone.

**Whenever you `git push` new changes to `main`, the deployed app auto-updates.**

### Free-tier resource limits

Streamlit Community Cloud's free tier gives your app about 1 GB of RAM. This project's default
settings (25,000 TF-IDF features over the full job corpus) are tuned to fit comfortably, but if
you significantly grow your dataset and the app crashes or shows a memory error:
- Open `src/config.py` and lower `TFIDF_MAX_FEATURES_JOBS` (e.g. from `25_000` to `12_000`), or
- Set `MAX_JOBS_FOR_INDEX` to a number (e.g. `30_000`) to subsample the job corpus,
- then re-run `python scripts/train_all.py` locally and `git push` the updated `models/` files.

---

## 7. How the ML actually works (short version)

| Feature | Technique | Type |
|---|---|---|
| Resume category prediction | TF-IDF + Logistic Regression (multi-class) | Supervised |
| Ranked job recommendations | TF-IDF + cosine similarity | Unsupervised |
| Shortlisting / fit score | Engineered features (similarity, skill overlap, experience match, title overlap) + Logistic Regression | Supervised (weak-labeled, see below) |
| Job family discovery | K-Means (k chosen via elbow + silhouette) + Truncated SVD for 2D plotting | Unsupervised |
| Skill-gap report | Set comparison: resume tokens vs. job/cluster keywords | Rule-based on top of the above |
| Career mentor | Pattern-matched Q&A over the above outputs | Rule-based, not generative AI |

### An honest note on the Fit Predictor (Model B)

No public dataset contains real "was this candidate shortlisted" labels. Model B is trained
with **weak supervision**: for thousands of random (resume, job) pairs, we compute the same
match features used at inference time, rank them by a composite of text-similarity and
skill-overlap percentiles, and label the top quartile as "fit". A Logistic Regression model
then learns a smooth, calibrated probability from these noisy heuristic labels — which is more
useful in the app than a hard threshold rule, but it is **not** a real hiring-outcome predictor.
This is documented again inside `src/models/fit_predictor.py` and shown as a caption directly in
the app's Shortlisting Fit tab, so it's never presented as more than it is.

### A note on the resume classifier's categories

The classifier can only predict categories that exist in your resume training data (by default:
ACCOUNTANT, ADVOCATE, AGRICULTURE, APPAREL, ARTS, AVIATION, BANKING, BUSINESS-DEVELOPMENT, CHEF,
CONSTRUCTION, CONSULTANT, DESIGNER, DIGITAL-MEDIA, DevOps Engineer, ENGINEERING, FINANCE,
FITNESS, HEALTHCARE, HR, INFORMATION-TECHNOLOGY, Java Developer, PUBLIC-RELATIONS, SALES,
TEACHER, Testing — if you swap in your own resume dataset, this list changes automatically). A
resume that doesn't cleanly fit one of these (e.g. a niche specialization) will still get a
"best available" prediction with a lower confidence score — this is expected model behavior,
not a bug, and the app shows the full top-3 probability breakdown so it's transparent.

---

## 8. Retraining after you update your datasets

Any time you replace or grow the CSVs in `data/raw/`, just re-run:
```bash
python scripts/train_all.py
```
then commit and push the updated `models/` and `data/processed/job_corpus_app.csv.gz` files:
```bash
git add models/ data/processed/job_corpus_app.csv.gz reports/metrics.json
git commit -m "Retrain models on updated dataset"
git push
```
Streamlit Cloud will pick up the change automatically.

---

## 9. Troubleshooting

**`ModuleNotFoundError: No module named 'src'`**
Make sure you're running commands from the project root folder (the one containing
`requirements.txt`), and that your virtual environment is activated.

**`FileNotFoundError` for a CSV in `data/raw/`**
Double check the exact filename matches `src/config.py` (`RESUME_CSV`, `NAUKRI_CSV`,
`LINKEDIN_CSV`) — filenames are case-sensitive on macOS/Linux.

**Streamlit app says "Model artifacts not found"**
You haven't run `python scripts/train_all.py` yet (or it errored partway through — scroll up
in its terminal output to find the first error).

**`git push` rejected — "file too large" or times out**
GitHub blocks files over 100 MB. Check what's large with:
```bash
find . -type f -size +50M -not -path "./venv/*" -not -path "./data/raw/*"
```
Most likely culprit is `models/job_tfidf_matrix.npz` if you significantly grew the job corpus
or `TFIDF_MAX_FEATURES_JOBS`. Lower `TFIDF_MAX_FEATURES_JOBS` in `src/config.py`, retrain, and
push again — or set up [Git LFS](https://git-lfs.com/) for that one file.

**Streamlit Cloud build fails on `pdfplumber` or `python-docx`**
Make sure `requirements.txt` wasn't edited/corrupted — these are pure-Python packages and
should install without system dependencies. Check the "Manage app" logs on Streamlit Cloud
for the exact error.

**The app is slow the first time someone opens it**
That's normal — the first load reads the TF-IDF matrix and models into memory (`@st.cache_resource`
inside `app/data_loader.py`). Every subsequent interaction, and every other visitor, reuses the
cached copy and is fast.

---

## 10. Tech stack

Python · pandas · NumPy · scikit-learn · SciPy · Streamlit · Plotly · pdfplumber · python-docx

---

## 11. License / academic use

This is a project template for educational/portfolio use. Replace this section with your
university's or course's required attribution if applicable.
