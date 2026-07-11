"""
Basic unit tests. Run with:  python -m pytest tests/ -v
(or simply: python tests/test_features.py)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.data.preprocess import clean_text, parse_skill_list, parse_experience_range, extract_years_from_resume
from src.features.match_features import skill_overlap_ratio, missing_skills, experience_match_score


def test_clean_text_lowercases_and_strips_urls():
    out = clean_text("Visit HTTP://Example.com for MORE info!!")
    assert "http" not in out
    assert out == out.lower()


def test_parse_skill_list_handles_numpy_repr():
    raw = "['Python' 'Machine Learning'\n 'SQL']"
    skills = parse_skill_list(raw)
    assert "python" in skills
    assert "sql" in skills


def test_parse_skill_list_handles_comma_separated():
    skills = parse_skill_list("Python, SQL, Excel")
    assert skills == ["python", "sql", "excel"]


def test_parse_experience_range():
    assert parse_experience_range("2-7 Yrs") == (2.0, 7.0)
    assert parse_experience_range("5 Yrs") == (5.0, 5.0)
    assert parse_experience_range("") == (0.0, 0.0)


def test_extract_years_from_resume():
    assert extract_years_from_resume("I have 5 years of experience") == 5.0
    assert extract_years_from_resume("no mention here") == 0.0


def test_skill_overlap_ratio():
    resume = "python django flask sql"
    job_skills = "python sql aws"
    ratio = skill_overlap_ratio(resume, job_skills)
    assert 0.0 < ratio <= 1.0


def test_missing_skills():
    resume = "experienced python developer with django and sql"
    job_skills = ["python", "django", "kubernetes", "sql"]
    missing = missing_skills(resume, job_skills)
    assert "kubernetes" in missing
    assert "python" not in missing


def test_experience_match_score_in_range():
    assert experience_match_score(4, 2, 7) == 1.0


def test_experience_match_score_out_of_range_decays():
    score = experience_match_score(15, 2, 7)
    assert 0.0 <= score < 1.0


if __name__ == "__main__":
    tests = [v for k, v in list(globals().items()) if k.startswith("test_")]
    passed = 0
    for t in tests:
        t()
        passed += 1
        print(f"  ok  {t.__name__}")
    print(f"\n{passed}/{len(tests)} tests passed.")
