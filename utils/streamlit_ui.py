from __future__ import annotations

import hashlib
import os
import re
from pathlib import Path
from typing import Any

import pandas as pd
import plotly.express as px
import streamlit as st
from dotenv import load_dotenv

from utils.ai_generator import generate_ai_insights
from utils.matcher import MatchResult, analyze_match
from utils.report_generator import create_pdf_report
from utils.resume_parser import FileValidationError, extract_text_from_upload, normalize_whitespace, validate_text_input
from utils.skill_extractor import SkillExtractionResult, extract_skills, get_skill_category


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"


PAGE_LINKS = [
    ("pages/1_Home.py", "Home", ":material/home:"),
    ("pages/2_Resume_Upload.py", "Resume Upload", ":material/upload_file:"),
    ("pages/3_Job_Description.py", "Job Description", ":material/description:"),
    ("pages/4_Analysis_Dashboard.py", "Analysis Dashboard", ":material/dashboard:"),
    ("pages/5_AI_Learning_Roadmap.py", "AI Learning Roadmap", ":material/map:"),
    ("pages/6_Career_Recommendations.py", "Career Recommendations", ":material/work:"),
    ("pages/7_Reports.py", "Reports", ":material/picture_as_pdf:"),
]


def load_local_text(filename: str) -> str:
    """Read bundled sample content used for demos and tests."""
    return (DATA_DIR / filename).read_text(encoding="utf-8")


def configure_app(page_title: str = "SkillGap AI", page_icon: str = "SG") -> None:
    """Configure Streamlit once from the router script or within a page script."""
    load_dotenv(BASE_DIR / ".env")
    st.set_page_config(
        page_title=page_title,
        page_icon=page_icon,
        layout="wide",
        initial_sidebar_state="expanded",
    )
    initialize_session_state()
    apply_dark_theme()


def prepare_page(title: str, subtitle: str | None = None, page_icon: str = "SG") -> None:
    """Apply shared state, theme, navigation, and page heading for page scripts."""
    configure_app(page_title=title, page_icon=page_icon)
    render_sidebar_navigation()
    render_sidebar_status()
    render_page_header(title, subtitle)


def render_sidebar_navigation() -> None:
    """Render the persistent sidebar navigation links for the multi-page app."""
    st.sidebar.title("SkillGap AI")
    st.sidebar.markdown("### Navigation")
    for page_file, label, icon in PAGE_LINKS:
        try:
            st.sidebar.page_link(page_file, label=label, icon=icon)
        except Exception:
            st.sidebar.markdown(f"- {icon} **{label}**")
    st.sidebar.divider()


def render_page_header(title: str, subtitle: str | None = None) -> None:
    subtitle_html = f'<div class="sg-page-subtitle">{subtitle}</div>' if subtitle else ""
    st.markdown(
        f"""
        <div>
            <div class="sg-page-kicker">SkillGap AI</div>
            <h1 class="sg-page-title">{title}</h1>
            {subtitle_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def initialize_session_state() -> None:
    """Create durable cross-page state for uploads, analysis, and reports."""
    defaults: dict[str, Any] = {
        "resume_text": "",
        "resume_filename": "",
        "resume_source": "",
        "resume_upload_signature": "",
        "job_description_text": "",
        "job_description_draft": "",
        "job_description_filename": "",
        "job_description_source": "",
        "job_upload_signature": "",
        "match_result": None,
        "insights": None,
        "analysis_signature": "",
        "last_analysis_error": "",
        "last_report_bytes": None,
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)

    # Keep the editable job-description widget in sync with persisted text.
    if st.session_state["job_description_text"] and not st.session_state["job_description_draft"]:
        st.session_state["job_description_draft"] = st.session_state["job_description_text"]


def apply_dark_theme() -> None:
    """Inject a consistent professional dark SaaS visual system."""
    st.markdown(
        """
        <style>
            :root {
                --sg-bg: #090d12;
                --sg-panel: #111820;
                --sg-panel-2: #151e28;
                --sg-border: #263241;
                --sg-text: #eef4f8;
                --sg-muted: #a6b4c3;
                --sg-green: #35c275;
                --sg-teal: #22d3c5;
                --sg-red: #f87171;
                --sg-blue: #60a5fa;
                --sg-amber: #fbbf24;
            }
            .stApp {
                background: var(--sg-bg);
                color: var(--sg-text);
            }
            [data-testid="stSidebar"] {
                background: #0b1117;
                border-right: 1px solid var(--sg-border);
            }
            [data-testid="stSidebar"] * {
                color: var(--sg-text);
            }
            .main .block-container {
                max-width: 1240px;
                padding-top: 2rem;
                padding-bottom: 3rem;
            }
            h1, h2, h3, h4, h5, h6, p, li, label, span {
                letter-spacing: 0;
            }
            .sg-page-kicker {
                color: var(--sg-teal);
                font-size: .78rem;
                font-weight: 700;
                text-transform: uppercase;
                letter-spacing: .08rem;
                margin-bottom: .35rem;
            }
            .sg-page-title {
                color: var(--sg-text);
                font-size: clamp(1.8rem, 3vw, 2.65rem);
                font-weight: 760;
                line-height: 1.08;
                margin: 0;
            }
            .sg-page-subtitle {
                color: var(--sg-muted);
                max-width: 820px;
                font-size: 1rem;
                margin: .65rem 0 1.35rem 0;
            }
            .sg-hero {
                background: #101720;
                border: 1px solid var(--sg-border);
                border-radius: 8px;
                padding: clamp(1.25rem, 3vw, 2rem);
                margin-bottom: 1.25rem;
                box-shadow: 0 18px 50px rgba(0, 0, 0, .24);
            }
            .sg-hero h1 {
                color: var(--sg-text);
                font-size: clamp(2.1rem, 5vw, 4.2rem);
                line-height: 1.02;
                margin: 0 0 .85rem 0;
                font-weight: 800;
            }
            .sg-hero p {
                color: var(--sg-muted);
                max-width: 760px;
                font-size: 1.08rem;
                margin: 0;
            }
            .sg-card {
                background: var(--sg-panel);
                border: 1px solid var(--sg-border);
                border-radius: 8px;
                padding: 1rem;
                min-height: 100%;
            }
            .sg-card h3 {
                margin: 0 0 .45rem 0;
                color: var(--sg-text);
                font-size: 1.02rem;
            }
            .sg-card p {
                color: var(--sg-muted);
                margin: 0;
                font-size: .93rem;
            }
            .sg-kpi {
                background: var(--sg-panel);
                border: 1px solid var(--sg-border);
                border-radius: 8px;
                padding: 1rem;
                min-height: 118px;
            }
            .sg-kpi-label {
                color: var(--sg-muted);
                font-size: .78rem;
                text-transform: uppercase;
                letter-spacing: .06rem;
                font-weight: 700;
            }
            .sg-kpi-value {
                color: var(--sg-text);
                font-size: clamp(1.6rem, 3vw, 2.45rem);
                line-height: 1.1;
                font-weight: 800;
                margin-top: .35rem;
                overflow-wrap: anywhere;
            }
            .sg-kpi-caption {
                color: var(--sg-muted);
                font-size: .83rem;
                margin-top: .55rem;
            }
            .sg-status-row {
                display: flex;
                align-items: center;
                justify-content: space-between;
                gap: .65rem;
                padding: .55rem .65rem;
                border: 1px solid var(--sg-border);
                border-radius: 8px;
                background: #0f151d;
                margin-bottom: .45rem;
            }
            .sg-status-good {
                color: var(--sg-green);
                font-weight: 700;
            }
            .sg-status-warn {
                color: var(--sg-amber);
                font-weight: 700;
            }
            .sg-pill {
                display: inline-block;
                padding: .28rem .58rem;
                border-radius: 999px;
                margin: .16rem .2rem .16rem 0;
                font-size: .82rem;
                border: 1px solid transparent;
                color: var(--sg-text);
            }
            .sg-pill-green {
                background: rgba(53, 194, 117, .16);
                border-color: rgba(53, 194, 117, .55);
            }
            .sg-pill-red {
                background: rgba(248, 113, 113, .16);
                border-color: rgba(248, 113, 113, .55);
            }
            .sg-pill-blue {
                background: rgba(96, 165, 250, .16);
                border-color: rgba(96, 165, 250, .55);
            }
            .sg-muted {
                color: var(--sg-muted);
            }
            .stButton > button, .stDownloadButton > button, [data-testid="stPageLink-NavLink"] {
                border-radius: 8px;
            }
            .stButton > button[kind="primary"] {
                background: var(--sg-green);
                border-color: var(--sg-green);
                color: #031009;
                font-weight: 750;
            }
            div[data-testid="stMetric"] {
                background: var(--sg-panel);
                border: 1px solid var(--sg-border);
                border-radius: 8px;
                padding: 1rem;
            }
            div[data-testid="stMetric"] label, div[data-testid="stMetric"] [data-testid="stMetricDelta"] {
                color: var(--sg-muted);
            }
            .stProgress > div > div > div > div {
                background-color: var(--sg-green);
            }
            code, pre {
                color: #d9f99d;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_page_header(title: str, subtitle: str | None = None) -> None:
    subtitle_html = f'<div class="sg-page-subtitle">{subtitle}</div>' if subtitle else ""
    st.markdown(
        f"""
        <div>
            <div class="sg-page-kicker">SkillGap AI</div>
            <h1 class="sg-page-title">{title}</h1>
            {subtitle_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar_status() -> None:
    """Show cross-page data readiness and quick sample actions."""
    st.sidebar.divider()
    st.sidebar.subheader("Workspace")

    resume_ready = bool(st.session_state.get("resume_text"))
    job_ready = bool(st.session_state.get("job_description_text"))
    analysis_ready = has_current_analysis()

    status_rows = [
        ("Resume", "Ready" if resume_ready else "Needed", resume_ready),
        ("Job description", "Ready" if job_ready else "Needed", job_ready),
        ("Analysis", "Current" if analysis_ready else "Not run", analysis_ready),
    ]
    for label, value, good in status_rows:
        css_class = "sg-status-good" if good else "sg-status-warn"
        st.sidebar.markdown(
            f"""
            <div class="sg-status-row">
                <span>{label}</span>
                <span class="{css_class}">{value}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    col1, col2 = st.sidebar.columns(2)
    if col1.button("Sample resume", use_container_width=True):
        load_sample_resume()
        st.rerun()
    if col2.button("Sample JD", use_container_width=True):
        load_sample_job_description()
        st.rerun()

    api_key_available = bool(os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"))
    if api_key_available:
        st.sidebar.success("Gemini API key detected")
    else:
        st.sidebar.info("Local recommendations active. Add GEMINI_API_KEY for Gemini output.")


def render_page_links(page_files: list[str]) -> None:
    """Render compact cross-page links for empty states and next steps."""
    for page_file, label, icon in PAGE_LINKS:
        if page_file in page_files:
            def render_page_links(page_files: list[str]) -> None:
    for page_file, label, icon in PAGE_LINKS:
        if page_file in page_files:
            st.page_link(page_file, label=label, icon=icon)


def clear_analysis() -> None:
    st.session_state["match_result"] = None
    st.session_state["insights"] = None
    st.session_state["analysis_signature"] = ""
    st.session_state["last_analysis_error"] = ""
    st.session_state["last_report_bytes"] = None


def _content_signature(resume_text: str, job_text: str) -> str:
    digest = hashlib.sha256()
    digest.update(normalize_whitespace(resume_text).encode("utf-8"))
    digest.update(b"\0")
    digest.update(normalize_whitespace(job_text).encode("utf-8"))
    return digest.hexdigest()


def _file_signature(uploaded_file: Any) -> str:
    name = getattr(uploaded_file, "name", "")
    size = getattr(uploaded_file, "size", 0)
    return f"{name}:{size}"


def _store_text(kind: str, text: str, filename: str, source: str) -> None:
    normalized = normalize_whitespace(text)

    text_key = f"{kind}_text" if kind == "resume" else "job_description_text"
    filename_key = f"{kind}_filename" if kind == "resume" else "job_description_filename"
    source_key = f"{kind}_source" if kind == "resume" else "job_description_source"

    if st.session_state.get(text_key, "") != normalized:
        clear_analysis()

    st.session_state[text_key] = normalized
    st.session_state[filename_key] = filename
    st.session_state[source_key] = source


def store_resume_text(text: str, filename: str, source: str, validate: bool = True) -> None:
    if validate:
        validate_text_input(text, label="Resume")
    _store_text("resume", text, filename, source)


def store_job_description_text(text: str, filename: str, source: str, validate: bool = False) -> None:
    if validate:
        validate_text_input(text, label="Job description")
    _store_text("job_description", text, filename, source)
    st.session_state["job_description_draft"] = st.session_state["job_description_text"]


def sync_job_description_draft() -> None:
    """Persist text-area changes without forcing an analysis rerun immediately."""
    draft = st.session_state.get("job_description_draft", "")
    store_job_description_text(draft, st.session_state.get("job_description_filename", ""), "Text area")


def load_sample_resume() -> None:
    store_resume_text(load_local_text("sample_resume.txt"), "sample_resume.txt", "Bundled sample", validate=True)
    st.session_state["resume_upload_signature"] = "sample_resume.txt"


def load_sample_job_description() -> None:
    store_job_description_text(
        load_local_text("sample_job_description.txt"),
        "sample_job_description.txt",
        "Bundled sample",
        validate=True,
    )
    st.session_state["job_upload_signature"] = "sample_job_description.txt"


def process_resume_upload(uploaded_file: Any) -> str:
    """Validate, extract, store, and return resume text from an upload."""
    text = extract_text_from_upload(uploaded_file)
    store_resume_text(text, getattr(uploaded_file, "name", "resume"), "Uploaded file", validate=True)
    st.session_state["resume_upload_signature"] = _file_signature(uploaded_file)
    return text


def process_job_upload(uploaded_file: Any) -> str:
    """Validate, extract, store, and return job-description text from an upload."""
    text = extract_text_from_upload(uploaded_file)
    store_job_description_text(text, getattr(uploaded_file, "name", "job_description"), "Uploaded file", validate=True)
    st.session_state["job_upload_signature"] = _file_signature(uploaded_file)
    return text


def has_required_inputs() -> bool:
    return bool(st.session_state.get("resume_text")) and bool(st.session_state.get("job_description_text"))


def has_current_analysis() -> bool:
    if not st.session_state.get("match_result") or not st.session_state.get("insights"):
        return False
    expected = _content_signature(st.session_state["resume_text"], st.session_state["job_description_text"])
    return st.session_state.get("analysis_signature") == expected


def get_match_result() -> MatchResult | None:
    result = st.session_state.get("match_result")
    return result if isinstance(result, MatchResult) else None


def get_insights() -> dict[str, Any] | None:
    insights = st.session_state.get("insights")
    return insights if isinstance(insights, dict) else None


def run_full_analysis() -> bool:
    """Run matching and AI generation, storing results for all pages."""
    try:
        resume_text = st.session_state.get("resume_text", "")
        job_text = st.session_state.get("job_description_text", "")
        validate_text_input(resume_text, label="Resume")
        validate_text_input(job_text, label="Job description")

        with st.spinner("Analyzing match quality, ATS readiness, and learning path..."):
            match_result = analyze_match(resume_text, job_text)
            insights = generate_ai_insights(match_result, resume_text, job_text)

        st.session_state["match_result"] = match_result
        st.session_state["insights"] = insights
        st.session_state["analysis_signature"] = _content_signature(resume_text, job_text)
        st.session_state["last_analysis_error"] = ""
        st.session_state["last_report_bytes"] = None
        return True
    except FileValidationError as exc:
        st.session_state["last_analysis_error"] = str(exc)
        st.error(str(exc))
        return False
    except Exception as exc:
        st.session_state["last_analysis_error"] = f"SkillGap AI could not complete the analysis: {exc}"
        st.error(st.session_state["last_analysis_error"])
        return False


def render_analysis_gate(context: str) -> bool:
    """Render an actionable empty state when a page needs analysis data."""
    if has_current_analysis():
        return True

    st.info(f"{context} needs a current resume and job-description analysis.")
    if not st.session_state.get("resume_text") or not st.session_state.get("job_description_text"):
        missing_pages = []
        if not st.session_state.get("resume_text"):
            missing_pages.append("pages/2_Resume_Upload.py")
        if not st.session_state.get("job_description_text"):
            missing_pages.append("pages/3_Job_Description.py")
        render_page_links(missing_pages)
        return False

    if st.button("Run analysis now", type="primary", use_container_width=True):
        if run_full_analysis():
            st.rerun()
    return False


def percent_progress(value: float) -> int:
    return max(0, min(100, int(round(value))))


def word_count(text: str) -> int:
    return len(re.findall(r"\b\w+\b", text))


def render_kpi_card(label: str, value: str, caption: str = "", accent: str = "green") -> None:
    colors = {
        "green": "var(--sg-green)",
        "teal": "var(--sg-teal)",
        "red": "var(--sg-red)",
        "blue": "var(--sg-blue)",
        "amber": "var(--sg-amber)",
    }
    color = colors.get(accent, "var(--sg-green)")
    st.markdown(
        f"""
        <div class="sg-kpi" style="border-top: 3px solid {color};">
            <div class="sg-kpi-label">{label}</div>
            <div class="sg-kpi-value">{value}</div>
            <div class="sg-kpi-caption">{caption}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_card(title: str, body: str) -> None:
    st.markdown(
        f"""
        <div class="sg-card">
            <h3>{title}</h3>
            <p>{body}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_document_preview(title: str, text: str, filename: str = "", source: str = "") -> None:
    st.subheader(title)
    if not text:
        st.info("No content is saved yet.")
        return

    cols = st.columns(3)
    cols[0].metric("Words", f"{word_count(text):,}")
    cols[1].metric("Characters", f"{len(text):,}")
    cols[2].metric("Source", source or "Manual")

    if filename:
        st.caption(f"File: {filename}")
    preview = text[:6000]
    if len(text) > len(preview):
        preview += "\n\n[Preview truncated in the interface. Full text is preserved for analysis.]"
    st.text_area(title, value=preview, height=320, disabled=True, label_visibility="collapsed")


def extract_document_skills(text: str) -> SkillExtractionResult:
    return extract_skills(text)


def render_skill_pills(title: str, skills: list[str], css_class: str) -> None:
    st.subheader(title)
    if not skills:
        st.caption("None detected")
        return
    pills = "".join(f'<span class="sg-pill {css_class}">{skill}</span>' for skill in skills)
    st.markdown(pills, unsafe_allow_html=True)


def build_skill_dataframe(match_result: MatchResult) -> pd.DataFrame:
    rows = []
    for skill in match_result.matching_skills:
        rows.append({"Skill": skill, "Status": "Matching", "Category": get_skill_category(skill)})
    for skill in match_result.missing_skills:
        rows.append({"Skill": skill, "Status": "Missing", "Category": get_skill_category(skill)})
    for skill in match_result.additional_skills:
        rows.append({"Skill": skill, "Status": "Additional", "Category": get_skill_category(skill)})
    return pd.DataFrame(rows)


def render_metric_panel(match_result: MatchResult) -> None:
    cols = st.columns(4)
    with cols[0]:
        render_kpi_card("Match Score", f"{match_result.match_percentage:.1f}%", "Overall role fit", "green")
    with cols[1]:
        render_kpi_card("ATS Score", f"{match_result.ats_score:.1f}/100", "Parser readiness", "teal")
    with cols[2]:
        render_kpi_card("Skills Found", str(len(match_result.resume_skills)), "Detected in resume", "blue")
    with cols[3]:
        render_kpi_card("Missing Skills", str(len(match_result.missing_skills)), "Required by job", "red")

    st.progress(percent_progress(match_result.match_percentage), text="Overall match progress")
    st.progress(percent_progress(match_result.ats_score), text="ATS compatibility progress")


def render_skill_charts(match_result: MatchResult) -> None:
    chart_df = pd.DataFrame(
        {
            "Status": ["Matching", "Missing", "Additional"],
            "Count": [
                len(match_result.matching_skills),
                len(match_result.missing_skills),
                len(match_result.additional_skills),
            ],
        }
    )
    colors = {"Matching": "#35c275", "Missing": "#f87171", "Additional": "#60a5fa"}

    col1, col2 = st.columns(2)
    with col1:
        if chart_df["Count"].sum() > 0:
            pie = px.pie(
                chart_df,
                names="Status",
                values="Count",
                hole=0.48,
                color="Status",
                color_discrete_map=colors,
                template="plotly_dark",
                title="Skill Distribution",
            )
            pie.update_layout(margin=dict(l=10, r=10, t=45, b=10), paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(pie, use_container_width=True)
        else:
            st.info("No skills were detected strongly enough to chart yet.")

    with col2:
        bar = px.bar(
            chart_df,
            x="Status",
            y="Count",
            color="Status",
            color_discrete_map=colors,
            template="plotly_dark",
            title="Skill Comparison",
        )
        bar.update_layout(showlegend=False, margin=dict(l=10, r=10, t=45, b=10), paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(bar, use_container_width=True)


def render_skill_details(match_result: MatchResult) -> None:
    col1, col2, col3 = st.columns(3)
    with col1:
        render_skill_pills("Matching Skills", match_result.matching_skills, "sg-pill-green")
    with col2:
        render_skill_pills("Missing Skills", match_result.missing_skills, "sg-pill-red")
    with col3:
        render_skill_pills("Additional Skills", match_result.additional_skills, "sg-pill-blue")

    skill_df = build_skill_dataframe(match_result)
    if not skill_df.empty:
        st.dataframe(skill_df, use_container_width=True, hide_index=True)


def render_roadmap(roadmap: dict[str, Any]) -> None:
    st.subheader("Timeline")
    st.markdown(f"Estimated timeline: **{roadmap.get('estimated_timeline', 'Not available')}**")

    for item in roadmap.get("learning_sequence", []):
        phase = item.get("phase", "")
        focus = item.get("focus", "Learning phase")
        duration = item.get("duration", "")
        label = f"Phase {phase}: {focus}" if phase else str(focus)
        with st.expander(label, expanded=phase in (1, "1")):
            if duration:
                st.caption(f"Duration: {duration}")
            for activity in item.get("activities", []):
                st.write(f"- {activity}")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Suggested Projects")
        for project in roadmap.get("suggested_projects", []):
            st.write(f"- {project}")
    with col2:
        st.subheader("Recommended Certifications")
        for certification in roadmap.get("recommended_certifications", []):
            st.write(f"- {certification}")

    st.caption(f"Generated with: {roadmap.get('generated_with', 'SkillGap AI')}")


def render_career_suggestions(suggestions: dict[str, Any]) -> None:
    sections = [
        ("Resume Improvement Tips", suggestions.get("resume_improvement_tips", [])),
        ("Interview Preparation Tips", suggestions.get("interview_preparation_suggestions", [])),
        ("Career Guidance", suggestions.get("career_growth_recommendations", [])),
    ]

    for title, items in sections:
        st.subheader(title)
        if not items:
            st.caption("No recommendations generated for this section.")
            continue
        for item in items:
            st.write(f"- {item}")

    st.caption(f"Generated with: {suggestions.get('generated_with', 'SkillGap AI')}")


def create_current_report() -> bytes:
    match_result = get_match_result()
    insights = get_insights()
    if match_result is None or insights is None:
        raise FileValidationError("Run an analysis before generating a report.")

    report_bytes = create_pdf_report(
        match_result=match_result,
        roadmap=insights["roadmap"],
        career_suggestions=insights["career_suggestions"],
    )
    st.session_state["last_report_bytes"] = report_bytes
    return report_bytes


def render_report_preview(match_result: MatchResult, insights: dict[str, Any]) -> None:
    roadmap = insights["roadmap"]
    suggestions = insights["career_suggestions"]
    st.subheader("Report Preview")
    st.markdown(
        f"""
        **Match Score:** {match_result.match_percentage:.1f}%  
        **ATS Score:** {match_result.ats_score:.1f}/100  
        **Missing Skills:** {", ".join(match_result.missing_skills) if match_result.missing_skills else "None detected"}  
        **Estimated Timeline:** {roadmap.get("estimated_timeline", "Not available")}
        """
    )

    with st.expander("Learning roadmap summary", expanded=True):
        for item in roadmap.get("learning_sequence", [])[:4]:
            st.write(f"- Phase {item.get('phase', '')}: {item.get('focus', 'Learning phase')}")

    with st.expander("Recommendation summary", expanded=True):
        for item in suggestions.get("resume_improvement_tips", [])[:4]:
            st.write(f"- {item}")
