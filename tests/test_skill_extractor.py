from utils.skill_extractor import extract_skills


def test_extracts_technical_and_soft_skills() -> None:
    text = """
    Built Python and SQL machine learning workflows with Pandas, NumPy, and scikit-learn.
    Presented results through Tableau and improved stakeholder communication.
    """

    result = extract_skills(text)

    assert "Python" in result.technical_skills
    assert "SQL" in result.technical_skills
    assert "Machine Learning" in result.technical_skills
    assert "Communication" in result.soft_skills
    assert "Tableau" in result.all_skills


def test_extract_skills_handles_empty_text() -> None:
    result = extract_skills("")

    assert result.all_skills == []
    assert result.keyword_counts == {}
