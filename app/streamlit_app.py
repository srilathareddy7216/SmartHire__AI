"""
SmartHire — Resume-to-Job Matching & Career Guidance Engine
Streamlit portal. Run with:  streamlit run app/streamlit_app.py
"""
from __future__ import annotations

import sys
from pathlib import Path
import inspect

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st
from sklearn.metrics.pairwise import cosine_similarity

APP_DIR = Path(__file__).resolve().parent
ROOT_DIR = APP_DIR.parent
sys.path.insert(0, str(ROOT_DIR))

from app import data_loader as dl
from app import theme
from src import config
from src.data.preprocess import clean_text, extract_years_from_resume
from src.features.match_features import missing_skills, skill_overlap_ratio, build_match_feature_vector
from src.models.mentor import answer as mentor_answer
from src.parsing.resume_parser import extract_resume_text

import ast


def _parse_skills_list(raw) -> list[str]:
    """Safely parse the stringified skills_list column back into a python list."""
    if not isinstance(raw, str) or not raw.strip().startswith("["):
        return []
    try:
        val = ast.literal_eval(raw)
        return list(val) if isinstance(val, (list, tuple)) else []
    except (ValueError, SyntaxError):
        return []


# ---------------------------------------------------------------------------
# Engineering subfield heuristic — layered on top of the broad classifier
# label so "Engineering" becomes e.g. "Engineering · AI / Machine Learning"
# without needing to retrain the classifier on finer-grained categories.
# ---------------------------------------------------------------------------
ENGINEERING_SUBFIELDS = {
    "Computer Science / Software": [
        "software", "programming", "algorithm", "data structure", "backend",
        "frontend", "full stack", "java", "python", "c++", "sql", "git", "api",
    ],
    "AI / Machine Learning": [
        "machine learning", "deep learning", "neural network", "tensorflow",
        "pytorch", "nlp", "computer vision", "data science",
    ],
    "Electrical / Electronics": [
        "electrical", "circuit", "voltage", "pcb", "embedded", "microcontroller",
        "power system", "vlsi", "signal processing",
    ],
    "Mechanical": [
        "mechanical", "cad", "solidworks", "thermodynamics", "manufacturing",
        "autocad", "hvac", "fluid mechanics",
    ],
    "Civil": [
        "civil engineer", "structural", "construction", "surveying", "concrete",
        "geotechnical",
    ],
    "Chemical / Process": [
        "chemical process", "reactor", "distillation", "process engineer",
        "plant operation", "petrochemical",
    ],
}


def detect_subfield(clean_resume_text: str) -> str | None:
    """Heuristic keyword match to add a specialization hint on top of the
    broad predicted category. Returns None if no keywords matched."""
    best_label, best_hits = None, 0
    for label, keywords in ENGINEERING_SUBFIELDS.items():
        hits = sum(1 for kw in keywords if kw in clean_resume_text)
        if hits > best_hits:
            best_label, best_hits = label, hits
    return best_label if best_hits > 0 else None


# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="SmartHire — Resume-to-Job Matching",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded",
)
theme.inject()
st.markdown(theme.main_header(), unsafe_allow_html=True)

# ---------------------------------------------------------------------------
if not dl.artifacts_ready():
    st.error(
        "**Model artifacts not found.**\n\n"
        "Run the training pipeline first, from the project root:\n\n"
        "```bash\npython scripts/train_all.py\n```\n\n"
        "This trains every model and saves the files this app needs into `models/` "
        "and `data/processed/`. See the README for full setup steps."
    )
    st.stop()

job_corpus = dl.load_job_corpus()
job_vectorizer, job_matrix = dl.load_job_index()
clf_model, clf_vectorizer, label_encoder = dl.load_classifier_bundle()
kmeans, svd = dl.load_clustering_bundle()
fit_model = dl.load_fit_predictor()
cluster_labels = dl.load_cluster_labels()
coords_2d = dl.load_coords_2d()
cluster_terms = dl.load_cluster_terms()
metrics = dl.load_metrics()

if "resume_text" not in st.session_state:
    st.session_state.resume_text = ""
    st.session_state.resume_name = ""
    st.session_state.analyzed = False

# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown(theme.sidebar_brand(), unsafe_allow_html=True)
    page = st.radio(
        "Navigate",
        ["🏠 Home", "📄 Analyze My Resume", "🗺️ Explore Job Market", "📊 Model Performance", "💬 Career Mentor", "ℹ️ About"],
        label_visibility="collapsed",
    )
    st.markdown("---")
    st.caption(f"Jobs indexed: **{len(job_corpus):,}**")
    st.caption(f"Job categories learned: **{len(label_encoder.classes_)}**")
    st.caption("Built with classical ML only — no LLMs, no live scraping.")

# ===========================================================================
# HOME
# ===========================================================================
if page == "🏠 Home":
    st.markdown(
        f"""
        <div class="sh-hero">
          <span class="eyebrow">Supervised + Unsupervised ML · scikit-learn</span>
          <h1>Find the jobs your resume<br>is actually built for.</h1>
          <p class="sub">Upload your CV and SmartHire ranks it against {len(job_corpus):,} real postings,
          predicts your job category, scores your shortlisting fit, and tells you exactly which
          skills to add next — all with classical machine learning, end to end.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(theme.stat_card(f"{len(job_corpus):,}", "job postings indexed"), unsafe_allow_html=True)
    with c2:
        st.markdown(theme.stat_card(f"{len(label_encoder.classes_)}", "resume categories"), unsafe_allow_html=True)
    with c3:
        acc = metrics.get("classifier", {}).get("accuracy")
        st.markdown(theme.stat_card(f"{acc*100:.0f}%" if acc else "—", "classifier accuracy"), unsafe_allow_html=True)
    with c4:
        st.markdown(theme.stat_card(f"{kmeans.n_clusters}", "job families found"), unsafe_allow_html=True)

    st.write("")
    st.markdown('<span class="sh-eyebrow">How it works</span>', unsafe_allow_html=True)
    steps = [
        ("01", "Upload", "Drop in a PDF, DOCX, or TXT resume. We extract the raw text locally — nothing leaves your session."),
        ("02", "Classify", "A TF-IDF + Logistic Regression model predicts your job domain from 25 learned categories."),
        ("03", "Match & Score", "Cosine similarity ranks the job corpus against your resume; a second model predicts shortlisting fit."),
        ("04", "Close the gap", "A skill-gap report compares your resume to each match and to your closest job cluster."),
    ]
    cols = st.columns(4)
    for col, (n, title, desc) in zip(cols, steps):
        with col:
            st.markdown(
                f'<div class="sh-card"><span class="sh-eyebrow">{n}</span>'
                f'<h4 style="margin:0 0 0.4rem 0;">{title}</h4>'
                f'<p style="color:var(--muted); font-size:0.9rem; margin:0;">{desc}</p></div>',
                unsafe_allow_html=True,
            )

    st.write("")
    st.info("👈 Head to **Analyze My Resume** in the sidebar to try it on your own CV.")

# ===========================================================================
# ANALYZE MY RESUME
# ===========================================================================
elif page == "📄 Analyze My Resume":
    st.markdown('<span class="sh-eyebrow">Step 1</span>', unsafe_allow_html=True)
    st.markdown("## Upload your resume")

    left, right = st.columns([1, 1.4])
    with left:
        uploaded = st.file_uploader("PDF, DOCX, or TXT", type=["pdf", "docx", "txt"])
        paste_mode = st.checkbox("...or paste resume text instead")
        pasted_text = ""
        if paste_mode:
            pasted_text = st.text_area("Paste resume text", height=200)

        top_n = st.slider("How many job matches to return?", 5, 30, 10)
        run = st.button("✨ Analyze Resume", type="primary", use_container_width=True)

    with right:
        st.markdown(
            '<div class="sh-card"><b>Privacy note.</b> Your resume is processed only in this '
            'session\'s memory to compute predictions — it is not stored, logged, or sent to any '
            'third-party API. Everything here runs on classical ML models trained ahead of time.</div>',
            unsafe_allow_html=True,
        )

    if run:
        raw_text = ""
        if uploaded is not None:
            try:
                raw_text = extract_resume_text(uploaded.name, uploaded.read())
            except Exception as e:
                st.error(f"Couldn't read that file: {e}")
        elif pasted_text.strip():
            raw_text = pasted_text

        if not raw_text or len(raw_text.strip()) < 30:
            st.warning("Please upload a resume file or paste enough text (30+ characters) to analyze.")
        else:
            st.session_state.resume_text = raw_text
            st.session_state.resume_name = uploaded.name if uploaded else "Pasted resume"
            st.session_state.analyzed = True
            st.session_state.top_n = top_n

    if st.session_state.analyzed and st.session_state.resume_text:
        raw_text = st.session_state.resume_text
        clean = clean_text(raw_text)
        years_exp = extract_years_from_resume(raw_text)

        # ---- Model A: classify ----
        X_clf = clf_vectorizer.transform([clean])
        proba = clf_model.predict_proba(X_clf)[0]
        order = np.argsort(proba)[::-1][:3]
        top_categories = [(label_encoder.classes_[i], float(proba[i])) for i in order]
        predicted_category = top_categories[0][0]

        # ---- Recommender: top-N jobs ----
        resume_vec = job_vectorizer.transform([clean])
        sims = cosine_similarity(resume_vec, job_matrix).flatten()
        top_idx = np.argsort(sims)[::-1][: st.session_state.get("top_n", 10)]
        matches = job_corpus.iloc[top_idx].copy()
        matches["similarity"] = sims[top_idx]
        matches["match_score"] = (matches["similarity"] * 100).round(1)

        # ---- Fit predictor for each match ----
        fit_scores = []
        for _, row in matches.iterrows():
            feats = build_match_feature_vector(clean, years_exp, row, row["similarity"])
            fit_scores.append(fit_model.predict_proba([feats])[0, 1] * 100)
        matches["fit_score"] = fit_scores

        st.markdown("---")
        st.markdown(f'<span class="sh-eyebrow">Resume: {st.session_state.resume_name}</span>', unsafe_allow_html=True)

        badge_cols = st.columns([1.6, 1, 1])
        with badge_cols[0]:
            cat_label = predicted_category
            if "engineer" in predicted_category.lower():
                sub = detect_subfield(clean)
                if sub:
                    cat_label = f"{predicted_category} · {sub}"
            st.markdown(
                f'<span class="badge match">Predicted category: {cat_label}</span>',
                unsafe_allow_html=True,
            )
        with badge_cols[1]:
            st.markdown(f'<span class="badge amber">~{years_exp:.0f} yrs experience detected</span>', unsafe_allow_html=True)
        with badge_cols[2]:
            st.markdown(f'<span class="badge signal">Avg match score: {matches["match_score"].mean():.0f}%</span>', unsafe_allow_html=True)

        st.write("")
        with st.expander("See all category probabilities"):
            for cat, p in top_categories:
                st.write(f"**{cat}** — {p*100:.1f}%")
                st.progress(min(1.0, p))

        tab1, tab2, tab3, tab4 = st.tabs(["🎯 Top Matches", "✅ Shortlisting Fit", "🧩 Skill Gap Report", "📥 Download Report"])

        # --- Tab 1: Top Matches (NEW grid card UI) ---
        # --- Tab 1: Top Matches (NEW "orbit badge" grid UI) ---
        # --- Tab 1: Top Matches (colorful grid UI, fixed sizing) ---
        with tab1:
            st.markdown(f"**{len(matches)} best-matching postings**, ranked by content similarity.")
            st.write("")

            match_rows = list(matches.iterrows())
            n_cols = 3
            for i in range(0, len(match_rows), n_cols):
                row_chunk = match_rows[i : i + n_cols]
                cols = st.columns(n_cols, gap="medium")
                for col, (orig_idx, row) in zip(cols, row_chunk):
                    with col:
                        st.markdown(
                            theme.job_recommendation_card(
                                title=row["title"].title(),
                                company=row["company"] or row["source"].title(),
                                location=row["location"] or "—",
                                job_id=orig_idx,
                                match_pct=row["match_score"],
                            ),
                            unsafe_allow_html=True,
                        )

        # --- Tab 2: Fit predictor (custom colorful panel, no plain gauge) ---
        with tab2:
            st.markdown("Pick a posting to see its predicted **shortlisting probability** and why.")
            options = [f"{i}: {r['title'].title()} ({r['company'] or r['source']})" for i, r in matches.reset_index().iterrows()]
            choice = st.selectbox("Job posting", options, key="fit_choice")
            idx = int(choice.split(":")[0])
            row = matches.reset_index(drop=True).iloc[idx]

            feats = build_match_feature_vector(clean, years_exp, row, row["similarity"])
            fit_prob = fit_model.predict_proba([feats])[0, 1] * 100

            features = [
                ("📝", "Text similarity", feats[0] * 100, "#2F5BFF"),
                ("🧩", "Skill overlap", feats[1] * 100, "#1FA971"),
                ("📅", "Experience match", feats[2] * 100, "#FF7A1A"),
                ("🏷️", "Title overlap", feats[3] * 100, "#FF4FA3"),
            ]

            st.markdown(
                theme.fit_panel(
                    job_title=row["title"].title(),
                    company=row["company"] or row["source"].title(),
                    fit_pct=fit_prob,
                    features=features,
                ),
                unsafe_allow_html=True,
            )
        
        # --- Tab 3: Skill Gap ---
        with tab3:
            st.markdown("**Skills to add**, based on your top matches and closest job cluster.")
            top_job = matches.iloc[0]
            job_skills_list = _parse_skills_list(top_job["skills_list"])
            gap = missing_skills(raw_text, job_skills_list)

            c1, c2 = st.columns(2)
            with c1:
                st.markdown("**✅ Skills you already show**")
                have = [s for s in job_skills_list if s not in gap]
                if have:
                    st.markdown("".join(f'<span class="chip have">{s}</span>' for s in have), unsafe_allow_html=True)
                else:
                    st.caption("No direct overlap detected with the top match's listed skills.")
            with c2:
                st.markdown("**🔺 Skills worth adding**")
                if gap:
                    st.markdown("".join(f'<span class="chip missing">{s}</span>' for s in gap), unsafe_allow_html=True)
                else:
                    st.caption("Great — no major gaps detected for your top match!")

            st.write("")
            # cluster-based gap
            resume_cluster = int(kmeans.predict(resume_vec)[0])
            terms = cluster_terms.get(str(resume_cluster), [])
            st.markdown(f"**Your closest job family (cluster #{resume_cluster})** is defined by:")
            st.markdown("".join(f'<span class="chip cluster">{t}</span>' for t in terms), unsafe_allow_html=True)
            cluster_gap = [t for t in terms if t not in clean]
            if cluster_gap:
                st.caption(f"Terms from this cluster not found in your resume: {', '.join(cluster_gap[:8])}")

            st.session_state.mentor_context = {
                "predicted_category": predicted_category,
                "top_missing_skills": gap or cluster_gap,
                "top_job_title": top_job["title"].title(),
                "avg_match_score": float(matches["match_score"].mean()),
                "cluster_terms": terms,
            }

        # --- Tab 4: Download ---
        with tab4:
            report_lines = [
                "SMARTHIRE — CV ANALYSIS REPORT",
                "=" * 40,
                f"Resume: {st.session_state.resume_name}",
                f"Predicted category: {predicted_category}",
                f"Detected experience: ~{years_exp:.0f} years",
                "",
                "TOP CATEGORY PROBABILITIES",
                *[f"  - {c}: {p*100:.1f}%" for c, p in top_categories],
                "",
                f"TOP {len(matches)} JOB MATCHES",
            ]
            for _, row in matches.iterrows():
                report_lines.append(
                    f"  - {row['title'].title()} | {row['company'] or row['source']} | "
                    f"match {row['match_score']:.1f}% | fit {row['fit_score']:.1f}%"
                )
            report_text = "\n".join(report_lines)
            st.download_button(
                "⬇️ Download report (.txt)", report_text,
                file_name="smarthire_report.txt", mime="text/plain",
            )
            st.download_button(
                "⬇️ Download matches (.csv)",
                matches[["title", "company", "location", "match_score", "fit_score", "source"]].to_csv(index=False),
                file_name="smarthire_matches.csv", mime="text/csv",
            )

# ===========================================================================
# EXPLORE JOB MARKET
# ===========================================================================
elif page == "🗺️ Explore Job Market":
    st.markdown('<span class="sh-eyebrow">Unsupervised discovery</span>', unsafe_allow_html=True)
    st.markdown("## Job families discovered by clustering")
    st.caption(
        f"K-Means (k={kmeans.n_clusters}) over TF-IDF job vectors, projected to 2D with Truncated SVD "
        f"for visualization. Each point is one job posting; colors are learned clusters, not labels."
    )

    plot_df = pd.DataFrame({
        "x": coords_2d[:, 0], "y": coords_2d[:, 1],
        "cluster": cluster_labels.astype(str),
        "title": job_corpus["title"].str.title(),
        "source": job_corpus["source"],
    })
    n_sample = min(8000, len(plot_df))
    plot_sample = plot_df.sample(n=n_sample, random_state=42)

    fig = px.scatter(
        plot_sample, x="x", y="y", color="cluster", hover_data=["title", "source"],
        color_discrete_sequence=px.colors.qualitative.Bold,
        opacity=0.6,
    )
    fig.update_layout(
        height=520, plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        legend_title_text="Cluster", margin=dict(l=10, r=10, t=10, b=10),
    )
    fig.update_xaxes(showgrid=False, zeroline=False, title=None, showticklabels=False)
    fig.update_yaxes(showgrid=False, zeroline=False, title=None, showticklabels=False)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("### What's in each cluster?")
    cols = st.columns(3)
    for i, (cid, terms) in enumerate(sorted(cluster_terms.items(), key=lambda x: int(x[0]))):
        with cols[i % 3]:
            count = int((cluster_labels == int(cid)).sum())
            st.markdown(
                f'<div class="sh-card"><b>Cluster {cid}</b> · {count:,} postings<br><br>'
                + "".join(f'<span class="chip cluster">{t}</span>' for t in terms[:8])
                + "</div>",
                unsafe_allow_html=True,
            )

# ===========================================================================
# MODEL PERFORMANCE
# ===========================================================================
elif page == "📊 Model Performance":
    st.markdown('<span class="sh-eyebrow">Evaluation</span>', unsafe_allow_html=True)
    st.markdown("## How the models actually perform")
    st.caption("Computed once during training (scripts/train_all.py) and saved to reports/metrics.json.")

    clf_m = metrics.get("classifier", {})
    rec_m = metrics.get("recommender", {})
    clu_m = metrics.get("clustering", {})
    fit_m = metrics.get("fit_predictor", {})

    st.markdown("#### Model A — Resume Category Classifier")
    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(theme.stat_card(f"{clf_m.get('accuracy', 0)*100:.1f}%", "accuracy"), unsafe_allow_html=True)
    c2.markdown(theme.stat_card(f"{clf_m.get('precision_macro', 0)*100:.1f}%", "precision (macro)"), unsafe_allow_html=True)
    c3.markdown(theme.stat_card(f"{clf_m.get('recall_macro', 0)*100:.1f}%", "recall (macro)"), unsafe_allow_html=True)
    c4.markdown(theme.stat_card(f"{clf_m.get('f1_macro', 0)*100:.1f}%", "F1 (macro)"), unsafe_allow_html=True)

    if clf_m.get("confusion_matrix"):
        cm = np.array(clf_m["confusion_matrix"])
        labels = clf_m.get("labels", [])
        fig = px.imshow(
            cm, x=labels, y=labels, color_continuous_scale="Purples",
            labels=dict(x="Predicted", y="Actual", color="Count"),
        )
        fig.update_layout(height=560, margin=dict(l=10, r=10, t=30, b=10))
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("#### Core Engine — Job Recommender")
    c1, c2, c3 = st.columns(3)
    p10 = rec_m.get("avg_precision_at_10_sample")
    c1.markdown(theme.stat_card(f"{p10*100:.1f}%" if p10 is not None else "—", "sampled Precision@10"), unsafe_allow_html=True)
    c2.markdown(theme.stat_card(f"{rec_m.get('n_jobs_indexed', 0):,}", "jobs indexed"), unsafe_allow_html=True)
    c3.markdown(theme.stat_card(f"{rec_m.get('n_terms', 0):,}", "TF-IDF vocabulary size"), unsafe_allow_html=True)

    st.markdown("#### Discovery — Job Clustering")
    if clu_m.get("k_eval_table"):
        k_df = pd.DataFrame(clu_m["k_eval_table"])
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=k_df["k"], y=k_df["silhouette"], mode="lines+markers", name="Silhouette", line=dict(color="#6C5CE7")))
        fig.update_layout(
            height=320, margin=dict(l=10, r=10, t=30, b=10),
            xaxis_title="k (number of clusters)", yaxis_title="Silhouette score",
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig, use_container_width=True)
        st.caption(f"Chosen k = {clu_m.get('best_k')} (highest silhouette score in the sampled search).")

    st.markdown("#### Model B — Shortlisting / Fit Predictor (optional, weak-supervised)")
    c1, c2, c3, c4 = st.columns(4)
    auc = fit_m.get("roc_auc")
    c1.markdown(theme.stat_card(f"{auc:.2f}" if auc else "—", "ROC-AUC"), unsafe_allow_html=True)
    c2.markdown(theme.stat_card(f"{fit_m.get('precision', 0)*100:.1f}%", "precision"), unsafe_allow_html=True)
    c3.markdown(theme.stat_card(f"{fit_m.get('recall', 0)*100:.1f}%", "recall"), unsafe_allow_html=True)
    c4.markdown(theme.stat_card(f"{fit_m.get('f1', 0)*100:.1f}%", "F1"), unsafe_allow_html=True)
    st.caption(
        "⚠️ No public dataset contains real hiring outcomes, so this model is trained on weak "
        "(heuristic) labels derived from text-similarity + skill-overlap percentiles — see README "
        "for the full explanation. Treat metrics here as a sanity check on the modeling approach, "
        "not as real-world shortlisting accuracy."
    )

# ===========================================================================
# CAREER MENTOR
# ===========================================================================
elif page == "💬 Career Mentor":
    st.markdown('<span class="sh-eyebrow">Stretch goal · rule-based, not an LLM</span>', unsafe_allow_html=True)
    st.markdown("## Ask the SmartHire Mentor")
    st.caption(
        "This assistant recognizes a fixed set of question patterns and answers using outputs from "
        "the classifier, recommender, and skill-gap modules above. It is not a generative model."
    )

    if not st.session_state.get("mentor_context"):
        st.info("Analyze a resume first (see **Analyze My Resume → Skill Gap Report** tab) to get personalized answers.")
        context = {}
    else:
        context = st.session_state.mentor_context

    suggestions = [
        "What skills am I missing?",
        "How do I improve my CV?",
        "What does the match score mean?",
        "What's my best-fit role?",
    ]
    cols = st.columns(len(suggestions))
    clicked = None
    for col, s in zip(cols, suggestions):
        if col.button(s, use_container_width=True):
            clicked = s

    q = st.text_input("Or type your own question", value=clicked or "")
    if q:
        st.markdown(
            f'<div class="sh-card"><b>You:</b> {q}<br><br><b>Mentor:</b> {mentor_answer(q, context)}</div>',
            unsafe_allow_html=True,
        )

# ===========================================================================
# ABOUT
# ===========================================================================
elif page == "ℹ️ About":
    st.markdown('<span class="sh-eyebrow">Project</span>', unsafe_allow_html=True)
    st.markdown("## About SmartHire")
    st.markdown(
        """
        SmartHire is an end-to-end **classical machine learning** project (no LLMs, no generative AI,
        no live scraping) that combines supervised and unsupervised techniques to recommend jobs,
        predict shortlisting fit, and generate CV improvement reports.

        **Supervised components**
        - *Resume Category Classifier* — TF-IDF + Logistic Regression, multi-class.
        - *Shortlisting / Fit Predictor* — Logistic Regression over engineered match features
          (text similarity, skill overlap, experience match, title overlap), weak-supervised.

        **Unsupervised components**
        - *Job Recommender* — TF-IDF vector space model + cosine similarity, content-based ranking.
        - *Job Clustering* — K-Means over job vectors, k chosen via elbow method + silhouette score,
          visualized in 2D with Truncated SVD.
        - *Skill-Gap Report* — set comparison between resume tokens and target job / cluster
          keywords.

        **Stack:** Python, scikit-learn, pandas, Streamlit, Plotly.
        """
    )
    st.markdown("### Tech stack")
    st.markdown(
        "".join(f'<span class="chip tag">{t}</span>' for t in
                ["Python", "scikit-learn", "pandas", "NumPy", "SciPy", "Streamlit", "Plotly", "pdfplumber", "python-docx"]),
        unsafe_allow_html=True,
    )