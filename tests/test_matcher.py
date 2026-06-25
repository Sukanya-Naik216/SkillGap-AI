from utils.matcher import analyze_match


def test_analyze_match_returns_scores_and_skill_sets() -> None:
    resume = """
    Summary
    Python data analyst with SQL, Pandas, NumPy, scikit-learn, Tableau, and communication skills.
    Experience
    - Built machine learning models and automated reporting workflows.
    Education
    B.Tech Computer Science
    Email: test@example.com
    Phone: +1 555 555 5555
    LinkedIn: linkedin.com/in/test
    GitHub: github.com/test
    """
    job = """
    We need Python, SQL, Machine Learning, NLP, Generative AI, Docker, and FastAPI.
    Strong communication and problem solving are required.
    """

    result = analyze_match(resume, job)

    assert result.match_percentage > 0
    assert result.ats_score > 0
    assert "Python" in result.matching_skills
    assert "NLP" in result.missing_skills
    assert "Docker" in result.missing_skills
