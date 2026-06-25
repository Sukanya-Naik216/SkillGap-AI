from __future__ import annotations

import json
import os
import warnings
from typing import Any

from dotenv import load_dotenv

from utils.matcher import MatchResult
from utils.skill_extractor import get_skill_category

try:
    from google import genai as google_genai
    from google.genai import types as genai_types
except ImportError:  # pragma: no cover - handled by local fallback
    google_genai = None
    genai_types = None

try:
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", FutureWarning)
        import google.generativeai as legacy_genai
except ImportError:  # pragma: no cover - only used for legacy installations
    legacy_genai = None


CERTIFICATION_MAP = {
    "AWS": "AWS Certified Cloud Practitioner or AWS Certified Solutions Architect Associate",
    "Azure": "Microsoft Certified: Azure Fundamentals",
    "Google Cloud": "Google Cloud Digital Leader or Associate Cloud Engineer",
    "Machine Learning": "Google Professional Machine Learning Engineer or AWS Machine Learning Specialty",
    "Data Analysis": "Google Data Analytics Professional Certificate",
    "Power BI": "Microsoft Power BI Data Analyst Associate",
    "Tableau": "Tableau Desktop Specialist",
    "Cybersecurity": "CompTIA Security+",
    "Kubernetes": "Certified Kubernetes Application Developer",
    "Scrum": "Professional Scrum Master I",
}


def _api_key() -> str | None:
    load_dotenv()
    return os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")


def _model_name() -> str:
    return os.getenv("GEMINI_MODEL", "gemini-2.5-flash")


def _extract_json_object(text: str) -> dict[str, Any] | None:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        cleaned = cleaned.removeprefix("json").strip()

    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start == -1 or end == -1 or start >= end:
        return None

    try:
        return json.loads(cleaned[start : end + 1])
    except json.JSONDecodeError:
        return None


def _call_gemini(prompt: str) -> dict[str, Any] | None:
    key = _api_key()
    if not key:
        return None

    if google_genai is not None and genai_types is not None:
        try:
            client = google_genai.Client(api_key=key)
            response = client.models.generate_content(
                model=_model_name(),
                contents=prompt,
                config=genai_types.GenerateContentConfig(
                    temperature=0.25,
                    max_output_tokens=1800,
                    response_mime_type="application/json",
                ),
            )
            response_text = getattr(response, "text", "") or ""
            return _extract_json_object(response_text)
        except Exception:
            return None

    if legacy_genai is None:
        return None

    try:
        legacy_genai.configure(api_key=key)
        model = legacy_genai.GenerativeModel(_model_name())
        response = model.generate_content(
            prompt,
            generation_config={
                "temperature": 0.25,
                "max_output_tokens": 1800,
                "response_mime_type": "application/json",
            },
        )
        response_text = getattr(response, "text", "") or ""
        return _extract_json_object(response_text)
    except Exception:
        return None


def _timeline_for_missing_skills(missing_count: int) -> str:
    if missing_count == 0:
        return "1-2 weeks for portfolio polish and targeted interview practice"
    low = max(4, missing_count * 2)
    high = max(6, missing_count * 3)
    return f"{low}-{high} weeks"


def _activities_for_skill(skill: str) -> list[str]:
    category = get_skill_category(skill)
    return [
        f"Study core {skill} concepts and terminology used in job descriptions.",
        f"Complete a hands-on {skill} exercise tied to a realistic {category.lower()} workflow.",
        f"Add one measurable resume bullet showing how you applied {skill}.",
    ]


def _project_ideas(missing_skills: list[str], matching_skills: list[str]) -> list[str]:
    if not missing_skills:
        return [
            "Refactor an existing portfolio project and add a concise case study with outcomes.",
            "Create a role-specific interview story bank using your strongest matching skills.",
            "Build a one-page project README that maps your experience to the target job requirements.",
        ]

    primary = missing_skills[:4]
    projects = [
        f"Build an end-to-end project using {', '.join(primary[:2])} and document the architecture decisions.",
        f"Create a dashboard or demo that proves practical use of {primary[0]} with measurable outputs.",
    ]
    if matching_skills:
        projects.append(
            f"Extend an existing {matching_skills[0]} project by adding {primary[-1]} to show adjacent growth."
        )
    else:
        projects.append(f"Publish a focused mini-project that demonstrates {primary[-1]} from scratch.")
    return projects


def _certifications_for_skills(missing_skills: list[str]) -> list[str]:
    certifications = []
    for skill in missing_skills:
        if skill in CERTIFICATION_MAP:
            certifications.append(CERTIFICATION_MAP[skill])

    if not certifications:
        certifications = [
            "Google Career Certificate aligned with the target role",
            "LinkedIn Learning role-based learning path certificate",
            "Coursera or edX specialization for the highest-priority missing skill",
        ]

    return list(dict.fromkeys(certifications))[:5]


def fallback_learning_roadmap(match_result: MatchResult) -> dict[str, Any]:
    missing_skills = match_result.missing_skills

    if missing_skills:
        learning_sequence = [
            {
                "phase": index + 1,
                "focus": skill,
                "duration": "2-3 weeks",
                "activities": _activities_for_skill(skill),
            }
            for index, skill in enumerate(missing_skills[:6])
        ]
    else:
        learning_sequence = [
            {
                "phase": 1,
                "focus": "Role alignment and interview readiness",
                "duration": "1-2 weeks",
                "activities": [
                    "Map each job requirement to a resume bullet with metrics.",
                    "Prepare STAR stories for the strongest matching skills.",
                    "Polish project documentation and portfolio links.",
                ],
            }
        ]

    return {
        "missing_skills": missing_skills,
        "learning_sequence": learning_sequence,
        "estimated_timeline": _timeline_for_missing_skills(len(missing_skills)),
        "suggested_projects": _project_ideas(missing_skills, match_result.matching_skills),
        "recommended_certifications": _certifications_for_skills(missing_skills),
        "generated_with": "SkillGap AI local recommendation engine",
    }


def fallback_career_suggestions(match_result: MatchResult) -> dict[str, Any]:
    missing = match_result.missing_skills[:5]
    matching = match_result.matching_skills[:5]

    resume_tips = [
        "Add a dedicated skills section that mirrors priority keywords from the job description.",
        "Rewrite experience bullets with action verbs, metrics, tools used, and business outcomes.",
        "Keep formatting ATS-friendly: standard headings, simple bullets, and no text inside images.",
    ]
    if missing:
        resume_tips.append(f"Add honest learning or project evidence for missing skills: {', '.join(missing)}.")
    if matching:
        resume_tips.append(f"Move strongest matching skills closer to the top: {', '.join(matching)}.")

    interview_tips = [
        "Prepare STAR stories for projects, conflicts, delivery constraints, and measurable impact.",
        "Practice explaining tradeoffs behind your most relevant technical decisions.",
        "Build a short answer for each missing skill that shows your learning plan and current progress.",
    ]

    growth_tips = [
        "Prioritize the missing skills that appear in multiple target jobs, not only this posting.",
        "Publish one portfolio artifact per month that demonstrates job-relevant outcomes.",
        "Track applications, interview feedback, and repeated skill gaps in a simple spreadsheet.",
    ]

    return {
        "resume_improvement_tips": resume_tips,
        "interview_preparation_suggestions": interview_tips,
        "career_growth_recommendations": growth_tips,
        "generated_with": "SkillGap AI local recommendation engine",
    }


def _roadmap_prompt(match_result: MatchResult, resume_text: str, job_text: str) -> str:
    return f"""
Return strict JSON for a learning roadmap. Do not include markdown.

Schema:
{{
  "missing_skills": ["skill"],
  "learning_sequence": [
    {{"phase": 1, "focus": "topic", "duration": "time", "activities": ["activity"]}}
  ],
  "estimated_timeline": "timeline",
  "suggested_projects": ["project"],
  "recommended_certifications": ["certification"],
  "generated_with": "Google Gemini"
}}

Match score: {match_result.match_percentage}
ATS score: {match_result.ats_score}
Matching skills: {match_result.matching_skills}
Missing skills: {match_result.missing_skills}

Resume excerpt:
{resume_text[:2500]}

Job description excerpt:
{job_text[:2500]}
""".strip()


def _suggestions_prompt(match_result: MatchResult, resume_text: str, job_text: str) -> str:
    return f"""
Return strict JSON for career recommendations. Do not include markdown.

Schema:
{{
  "resume_improvement_tips": ["tip"],
  "interview_preparation_suggestions": ["suggestion"],
  "career_growth_recommendations": ["recommendation"],
  "generated_with": "Google Gemini"
}}

Match score: {match_result.match_percentage}
ATS score: {match_result.ats_score}
Matching skills: {match_result.matching_skills}
Missing skills: {match_result.missing_skills}

Resume excerpt:
{resume_text[:2500]}

Job description excerpt:
{job_text[:2500]}
""".strip()


def _merge_with_fallback(ai_payload: dict[str, Any] | None, fallback: dict[str, Any]) -> dict[str, Any]:
    if not ai_payload:
        return fallback

    merged = fallback.copy()
    for key, value in ai_payload.items():
        if value:
            merged[key] = value
    merged["generated_with"] = ai_payload.get("generated_with", "Google Gemini")
    return merged


def generate_learning_roadmap(match_result: MatchResult, resume_text: str, job_text: str) -> dict[str, Any]:
    fallback = fallback_learning_roadmap(match_result)
    ai_payload = _call_gemini(_roadmap_prompt(match_result, resume_text, job_text))
    return _merge_with_fallback(ai_payload, fallback)


def generate_career_suggestions(match_result: MatchResult, resume_text: str, job_text: str) -> dict[str, Any]:
    fallback = fallback_career_suggestions(match_result)
    ai_payload = _call_gemini(_suggestions_prompt(match_result, resume_text, job_text))
    return _merge_with_fallback(ai_payload, fallback)


def generate_ai_insights(match_result: MatchResult, resume_text: str, job_text: str) -> dict[str, Any]:
    return {
        "roadmap": generate_learning_roadmap(match_result, resume_text, job_text),
        "career_suggestions": generate_career_suggestions(match_result, resume_text, job_text),
    }
