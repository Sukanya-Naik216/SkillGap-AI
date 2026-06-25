from __future__ import annotations

import streamlit as st

from utils.streamlit_ui import prepare_page, render_card, render_kpi_card, render_page_links


prepare_page(
    "Home",
    "A multi-page AI workspace for comparing resumes against job descriptions and turning skill gaps into action.",
)

st.markdown(
    """
    <section class="sg-hero">
        <h1>SkillGap AI</h1>
        <p>
            Analyze role fit, ATS readiness, missing skills, and career next steps from one focused Streamlit dashboard.
        </p>
    </section>
    """,
    unsafe_allow_html=True,
)

col1, col2, col3, col4 = st.columns(4)
with col1:
    render_kpi_card("Inputs", "PDF / DOCX / TXT", "Resume and job files", "teal")
with col2:
    render_kpi_card("Scoring", "Match + ATS", "Coverage, keywords, structure", "green")
with col3:
    render_kpi_card("AI Output", "Roadmap", "Skills, projects, certifications", "blue")
with col4:
    render_kpi_card("Export", "PDF", "Downloadable report", "amber")

st.subheader("Features")
feature_cols = st.columns(3)
features = [
    ("Resume Intelligence", "Extracts technical and soft skills from PDF, DOCX, and TXT resumes."),
    ("Job Matching", "Compares required skills, keyword overlap, and semantic similarity."),
    ("ATS Readiness", "Scores parser-friendly structure, contact signals, and job keyword coverage."),
    ("Learning Roadmap", "Creates a practical learning sequence with timeline and project ideas."),
    ("Career Guidance", "Generates resume, interview, and growth recommendations."),
    ("Report Export", "Builds a PDF report with scores, gaps, roadmap, and recommendations."),
]
for index, (title, body) in enumerate(features):
    with feature_cols[index % 3]:
        render_card(title, body)

st.subheader("Technology Stack")
tech_cols = st.columns(4)
stack = [
    ("App", "Streamlit multi-page UI"),
    ("Data", "Pandas, NumPy, Plotly"),
    ("NLP", "spaCy, scikit-learn"),
    ("Files", "PyPDF2, python-docx, FPDF"),
    ("AI", "Google Gemini API with local fallback"),
    ("Config", "python-dotenv environment variables"),
    ("Testing", "pytest smoke coverage"),
    ("Architecture", "Reusable utilities and session state"),
]
for index, (title, body) in enumerate(stack):
    with tech_cols[index % 4]:
        render_card(title, body)

st.subheader("Getting Started")
st.code(
    """python -m venv .venv
.venv\\Scripts\\activate
pip install -r requirements.txt
streamlit run app.py""",
    language="powershell",
)

st.markdown("Set `GEMINI_API_KEY` in `.env` for Gemini-generated recommendations. Without it, the local engine remains active.")

st.subheader("Workflow")
render_page_links(
    [
        "pages/2_Resume_Upload.py",
        "pages/3_Job_Description.py",
        "pages/4_Analysis_Dashboard.py",
        "pages/7_Reports.py",
    ]
)
