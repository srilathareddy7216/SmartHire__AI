"""
Stretch goal - Rule-based "mentor" assistant.

Deliberately NOT an LLM / generative model. It answers a small set of
recognizable question patterns by querying the outputs of the other ML
modules (classifier, recommender, clustering, skill-gap report). This keeps
the whole system classical ML end-to-end, per the project brief.
"""
from __future__ import annotations

import re

GREETING_RE = re.compile(r"\b(hi|hello|hey)\b", re.I)
SKILLS_FOR_RE = re.compile(r"skills?.*(?:for|need|require)", re.I)
HOW_TO_IMPROVE_RE = re.compile(r"(improve|better|boost).*(cv|resume)", re.I)
WHAT_IS_MATCH_RE = re.compile(r"(what|how).*(match|fit).*(score|mean)", re.I)
BEST_ROLE_RE = re.compile(r"(best|top|which).*(role|job|career)", re.I)


def answer(question: str, context: dict) -> str:
    """context may contain: predicted_category, top_missing_skills,
    top_job_title, avg_match_score, cluster_terms (list[str])."""
    q = question.strip()
    if not q:
        return "Ask me something like *\"What skills am I missing?\"* or *\"How do I improve my CV?\"*"

    if GREETING_RE.search(q):
        return ("Hi! I'm the SmartHire mentor — a rule-based assistant, not a chatbot. "
                "I can answer questions about your predicted role, missing skills, and match scores "
                "based on what the ML models found.")

    if SKILLS_FOR_RE.search(q) or "missing" in q.lower():
        missing = context.get("top_missing_skills") or []
        if not missing:
            return "I don't see any major skill gaps for your top match — nice work! Upload a resume first if you haven't."
        listed = ", ".join(missing[:8])
        return (f"Based on your top job matches, the skills that show up most often in postings but "
                f"**not** in your resume are: **{listed}**. Adding even 2-3 of these to your CV "
                f"(with real projects/examples) should raise your match scores.")

    if HOW_TO_IMPROVE_RE.search(q):
        cat = context.get("predicted_category", "your field")
        missing = context.get("top_missing_skills") or []
        tip = f" Start with: {', '.join(missing[:3])}." if missing else ""
        return (f"Your resume was classified as **{cat}**. To improve it: (1) mirror the exact keywords "
                f"used in job postings for this role, (2) quantify achievements with numbers, "
                f"(3) close your top skill gaps.{tip}")

    if WHAT_IS_MATCH_RE.search(q):
        return ("The **match score** is the cosine similarity between your resume's TF-IDF vector and a "
                "job posting's TF-IDF vector, scaled to 0-100. It measures how much your resume's wording "
                "and skills overlap with that specific posting — it's a text-similarity signal, not a "
                "guarantee of being hired.")

    if BEST_ROLE_RE.search(q):
        cat = context.get("predicted_category")
        top_title = context.get("top_job_title")
        if cat and top_title:
            return (f"Given your resume's content, the classifier predicts **{cat}** as your strongest "
                    f"category, and your single best-matching posting is **\"{top_title}\"**. "
                    f"Check the 'Top Matches' tab for the full ranked list.")
        return "Upload a resume in the Analyze tab first, and I'll tell you your predicted category and best match."

    if "cluster" in q.lower() or "family" in q.lower() or "group" in q.lower():
        terms = context.get("cluster_terms") or []
        if terms:
            return (f"Your best-matching job cluster is characterized by these recurring terms: "
                    f"**{', '.join(terms[:10])}**. That's the 'job family' your resume is closest to overall.")
        return "Explore the 'Job Market' tab to see all discovered job clusters."

    return ("I can answer questions like: *\"What skills am I missing?\"*, *\"How do I improve my CV?\"*, "
            "*\"What does the match score mean?\"*, or *\"What's my best-fit role?\"* — try rephrasing!")
