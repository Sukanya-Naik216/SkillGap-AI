from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass
from functools import lru_cache
from typing import Iterable, Mapping

import spacy


TECHNICAL_SKILL_GROUPS: Mapping[str, Mapping[str, Iterable[str]]] = {
    "Programming": {
        "Python": ["python"],
        "Java": ["java"],
        "JavaScript": ["javascript", "java script", "js"],
        "TypeScript": ["typescript", "type script"],
        "SQL": ["sql", "structured query language"],
        "NoSQL": ["nosql", "no sql"],
        "C++": ["c++", "cpp"],
        "C#": ["c#", "c sharp"],
        "Go": ["golang", "go language"],
        "Rust": ["rust"],
        "PHP": ["php"],
        "Ruby": ["ruby"],
    },
    "Web Development": {
        "HTML": ["html", "html5"],
        "CSS": ["css", "css3"],
        "React": ["react", "react.js", "reactjs"],
        "Angular": ["angular"],
        "Vue.js": ["vue", "vue.js", "vuejs"],
        "Node.js": ["node.js", "nodejs", "node js"],
        "Express.js": ["express.js", "expressjs", "express js"],
        "Django": ["django"],
        "Flask": ["flask"],
        "FastAPI": ["fastapi", "fast api"],
        "Streamlit": ["streamlit"],
        "REST APIs": ["rest api", "rest apis", "restful api", "restful apis"],
        "GraphQL": ["graphql", "graph ql"],
        "Tailwind CSS": ["tailwind", "tailwind css"],
        "Bootstrap": ["bootstrap"],
    },
    "Data and AI": {
        "Pandas": ["pandas"],
        "NumPy": ["numpy", "num py"],
        "scikit-learn": ["scikit-learn", "scikit learn", "sklearn"],
        "TensorFlow": ["tensorflow", "tensor flow"],
        "PyTorch": ["pytorch", "py torch"],
        "spaCy": ["spacy"],
        "NLP": ["nlp", "natural language processing"],
        "Machine Learning": ["machine learning", "ml"],
        "Deep Learning": ["deep learning"],
        "Generative AI": ["generative ai", "gen ai"],
        "LLM": ["llm", "large language model", "large language models"],
        "Prompt Engineering": ["prompt engineering"],
        "RAG": ["rag", "retrieval augmented generation"],
        "Computer Vision": ["computer vision"],
        "Data Analysis": ["data analysis", "data analytics"],
        "Data Visualization": ["data visualization", "data visualisation"],
        "Statistics": ["statistics", "statistical analysis"],
        "A/B Testing": ["a/b testing", "ab testing"],
    },
    "Cloud and DevOps": {
        "AWS": ["aws", "amazon web services"],
        "Azure": ["azure", "microsoft azure"],
        "Google Cloud": ["google cloud", "gcp"],
        "Docker": ["docker"],
        "Kubernetes": ["kubernetes", "k8s"],
        "Terraform": ["terraform"],
        "Linux": ["linux"],
        "Git": ["git"],
        "GitHub Actions": ["github actions"],
        "CI/CD": ["ci/cd", "cicd", "continuous integration", "continuous delivery"],
        "Jenkins": ["jenkins"],
    },
    "Databases and Data Engineering": {
        "PostgreSQL": ["postgresql", "postgres"],
        "MySQL": ["mysql"],
        "MongoDB": ["mongodb", "mongo db"],
        "Redis": ["redis"],
        "Snowflake": ["snowflake"],
        "BigQuery": ["bigquery", "big query"],
        "Spark": ["spark", "apache spark"],
        "Airflow": ["airflow", "apache airflow"],
        "ETL": ["etl", "extract transform load"],
    },
    "Quality and Security": {
        "Unit Testing": ["unit testing", "unit tests"],
        "Pytest": ["pytest"],
        "Cybersecurity": ["cybersecurity", "cyber security"],
        "OAuth": ["oauth", "oauth2", "oauth 2"],
        "JWT": ["jwt", "json web token"],
        "Agile": ["agile"],
        "Scrum": ["scrum"],
    },
    "Business Tools": {
        "Excel": ["excel", "microsoft excel"],
        "Power BI": ["power bi", "powerbi"],
        "Tableau": ["tableau"],
        "Jira": ["jira"],
    },
}

SOFT_SKILLS: Mapping[str, Iterable[str]] = {
    "Communication": ["communication", "written communication", "verbal communication"],
    "Leadership": ["leadership", "team leadership"],
    "Problem Solving": ["problem solving", "problem-solving"],
    "Teamwork": ["teamwork", "team work"],
    "Collaboration": ["collaboration", "cross-functional"],
    "Time Management": ["time management"],
    "Critical Thinking": ["critical thinking"],
    "Adaptability": ["adaptability", "adaptable"],
    "Stakeholder Management": ["stakeholder management", "stakeholder communication"],
    "Mentoring": ["mentoring", "coaching"],
    "Project Management": ["project management"],
    "Analytical Thinking": ["analytical thinking"],
    "Creativity": ["creativity", "creative thinking"],
    "Presentation": ["presentation", "presentations"],
    "Negotiation": ["negotiation"],
    "Ownership": ["ownership", "accountability"],
    "Attention to Detail": ["attention to detail", "detail-oriented", "detail oriented"],
}


@dataclass(frozen=True)
class SkillExtractionResult:
    technical_skills: list[str]
    soft_skills: list[str]
    all_skills: list[str]
    keyword_counts: dict[str, int]
    inferred_keywords: list[str]


def _flatten_technical_skills() -> dict[str, Iterable[str]]:
    flattened: dict[str, Iterable[str]] = {}
    for group in TECHNICAL_SKILL_GROUPS.values():
        flattened.update(group)
    return flattened


TECHNICAL_SKILLS = _flatten_technical_skills()
SKILL_CATEGORIES = {
    skill: category for category, skills in TECHNICAL_SKILL_GROUPS.items() for skill in skills
} | {skill: "Soft Skills" for skill in SOFT_SKILLS}


@lru_cache(maxsize=1)
def get_nlp():
    """Load a spaCy model when available, otherwise fall back to a blank English pipeline."""
    try:
        return spacy.load("en_core_web_sm", disable=["ner"])
    except OSError:
        return spacy.blank("en")


def _skill_pattern(variant: str) -> re.Pattern[str]:
    escaped = re.escape(variant.lower())
    # Dots are allowed after a match so sentence punctuation does not block words
    # like "communication.", while alphanumeric and symbol boundaries still keep
    # skills such as Java, C++, C#, and Node.js from matching inside longer terms.
    return re.compile(rf"(?<![a-z0-9+#.]){escaped}(?![a-z0-9+#])")


def _count_skill_mentions(text: str, variants: Iterable[str]) -> int:
    lower_text = text.lower()
    count = 0
    for variant in variants:
        count += len(_skill_pattern(variant).findall(lower_text))
    return count


def extract_keywords(text: str, limit: int = 25) -> list[str]:
    """Extract high-signal non-stopword terms with spaCy tokenization."""
    if not text.strip():
        return []

    nlp = get_nlp()
    doc = nlp(text[:200_000])
    terms: list[str] = []

    for token in doc:
        if token.is_stop or token.is_punct or token.like_num or not token.is_alpha:
            continue
        normalized = (token.lemma_ or token.text).lower().strip()
        if len(normalized) >= 3:
            terms.append(normalized)

    return [term for term, _ in Counter(terms).most_common(limit)]


def extract_skills(text: str) -> SkillExtractionResult:
    """Extract known technical and soft skills from resume or job description text."""
    if not text or not text.strip():
        return SkillExtractionResult([], [], [], {}, [])

    technical: list[str] = []
    soft: list[str] = []
    keyword_counts: dict[str, int] = {}

    for skill, variants in TECHNICAL_SKILLS.items():
        count = _count_skill_mentions(text, variants)
        if count:
            technical.append(skill)
            keyword_counts[skill] = count

    for skill, variants in SOFT_SKILLS.items():
        count = _count_skill_mentions(text, variants)
        if count:
            soft.append(skill)
            keyword_counts[skill] = count

    technical.sort()
    soft.sort()
    all_skills = sorted(set(technical + soft))

    return SkillExtractionResult(
        technical_skills=technical,
        soft_skills=soft,
        all_skills=all_skills,
        keyword_counts=keyword_counts,
        inferred_keywords=extract_keywords(text),
    )


def get_skill_category(skill: str) -> str:
    return SKILL_CATEGORIES.get(skill, "General")
