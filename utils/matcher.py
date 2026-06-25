from __future__ import annotations

import re
from dataclasses import asdict, dataclass

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from utils.skill_extractor import SkillExtractionResult, extract_keywords, extract_skills


SECTION_PATTERNS = {
    "summary": [r"\bsummary\b", r"\bprofile\b", r"\bobjective\b"],
    "skills": [r"\bskills\b", r"\btechnical skills\b", r"\bcore competencies\b"],
    "experience": [r"\bexperience\b", r"\bemployment\b", r"\bwork history\b"],
    "education": [r"\beducation\b", r"\bdegree\b", r"\buniversity\b"],
    "projects": [r"\bprojects\b", r"\bportfolio\b"],
    "certifications": [r"\bcertifications?\b", r"\blicenses?\b"],
}

ACTION_VERBS = {
    "achieved",
    "automated",
    "built",
    "created",
    "delivered",
    "designed",
    "developed",
    "improved",
    "implemented",
    "launched",
    "led",
    "managed",
    "optimized",
    "reduced",
    "shipped",
}


@dataclass(frozen=True)
class MatchResult:
    resume_skills: list[str]
    job_skills: list[str]
    matching_skills: list[str]
    missing_skills: list[str]
    additional_skills: list[str]
    match_percentage: float
    ats_score: float
    semantic_similarity: float
    skill_coverage: float
    keyword_overlap: float
    resume_extraction: SkillExtractionResult
    job_extraction: SkillExtractionResult

    def to_dict(self) -> dict:
        return asdict(self)


def calculate_text_similarity(resume_text: str, job_text: str) -> float:
    """Return TF-IDF cosine similarity as a 0-100 percentage."""
    if not resume_text.strip() or not job_text.strip():
        return 0.0

    try:
        vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2), max_features=5000)
        matrix = vectorizer.fit_transform([resume_text, job_text])
        score = cosine_similarity(matrix[0:1], matrix[1:2])[0][0]
        return round(float(score) * 100, 2)
    except ValueError:
        return 0.0


def calculate_keyword_overlap(resume_text: str, job_text: str) -> float:
    """Compare the top job-description keywords against resume text."""
    job_keywords = extract_keywords(job_text, limit=30)
    if not job_keywords:
        return 0.0

    resume_lower = resume_text.lower()
    matched = sum(1 for keyword in job_keywords if re.search(rf"\b{re.escape(keyword)}\b", resume_lower))
    return round((matched / len(job_keywords)) * 100, 2)


def calculate_structure_score(resume_text: str) -> float:
    """Estimate whether the resume text has ATS-friendly sections and language."""
    lower_text = resume_text.lower()
    present_sections = 0
    for patterns in SECTION_PATTERNS.values():
        if any(re.search(pattern, lower_text) for pattern in patterns):
            present_sections += 1

    section_score = (present_sections / len(SECTION_PATTERNS)) * 100

    word_count = len(re.findall(r"\b\w+\b", resume_text))
    if 350 <= word_count <= 950:
        length_score = 100.0
    elif 250 <= word_count < 350 or 950 < word_count <= 1200:
        length_score = 80.0
    elif 120 <= word_count < 250 or 1200 < word_count <= 1600:
        length_score = 60.0
    else:
        length_score = 40.0

    bullet_count = len(re.findall(r"(?m)^\s*[-*]", resume_text))
    action_verb_count = sum(1 for verb in ACTION_VERBS if re.search(rf"\b{verb}\b", lower_text))
    impact_score = min(100.0, 35.0 + bullet_count * 4.0 + action_verb_count * 5.0)

    return round(section_score * 0.50 + length_score * 0.25 + impact_score * 0.25, 2)


def calculate_contact_score(resume_text: str) -> float:
    """Reward common contact and profile signals that parsers expect."""
    checks = [
        bool(re.search(r"[\w.+-]+@[\w-]+\.[\w.-]+", resume_text)),
        bool(re.search(r"(\+?\d[\d\s().-]{7,}\d)", resume_text)),
        "linkedin" in resume_text.lower(),
        "github" in resume_text.lower() or "portfolio" in resume_text.lower(),
    ]
    return round((sum(checks) / len(checks)) * 100, 2)


def calculate_ats_score(
    resume_text: str,
    job_text: str,
    skill_coverage: float,
    keyword_overlap: float,
) -> float:
    structure_score = calculate_structure_score(resume_text)
    contact_score = calculate_contact_score(resume_text)

    score = (
        skill_coverage * 0.40
        + keyword_overlap * 0.25
        + structure_score * 0.20
        + contact_score * 0.15
    )
    return round(max(0.0, min(100.0, score)), 2)


def analyze_match(resume_text: str, job_text: str) -> MatchResult:
    """Compare resume and job text and return the full matching analysis."""
    resume_extraction = extract_skills(resume_text)
    job_extraction = extract_skills(job_text)

    resume_skills = set(resume_extraction.all_skills)
    job_skills = set(job_extraction.all_skills)

    matching_skills = sorted(resume_skills & job_skills)
    missing_skills = sorted(job_skills - resume_skills)
    additional_skills = sorted(resume_skills - job_skills)

    semantic_similarity = calculate_text_similarity(resume_text, job_text)
    keyword_overlap = calculate_keyword_overlap(resume_text, job_text)

    if job_skills:
        skill_coverage = round((len(matching_skills) / len(job_skills)) * 100, 2)
    else:
        skill_coverage = semantic_similarity

    match_percentage = round(
        min(100.0, skill_coverage * 0.70 + keyword_overlap * 0.20 + semantic_similarity * 0.10),
        2,
    )
    ats_score = calculate_ats_score(resume_text, job_text, skill_coverage, keyword_overlap)

    return MatchResult(
        resume_skills=sorted(resume_skills),
        job_skills=sorted(job_skills),
        matching_skills=matching_skills,
        missing_skills=missing_skills,
        additional_skills=additional_skills,
        match_percentage=match_percentage,
        ats_score=ats_score,
        semantic_similarity=semantic_similarity,
        skill_coverage=skill_coverage,
        keyword_overlap=keyword_overlap,
        resume_extraction=resume_extraction,
        job_extraction=job_extraction,
    )
