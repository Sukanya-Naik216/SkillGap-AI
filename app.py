from __future__ import annotations

import streamlit as st

from utils.streamlit_ui import prepare_page, render_page_links

prepare_page("SkillGap AI", "Launch the multi-page SkillGap AI dashboard from the sidebar.", page_icon=":material/home:")

st.markdown(
    """
    <section class="sg-hero">
        <h1>Welcome to SkillGap AI</h1>
        <p>Use the sidebar to navigate between Resume Upload, Job Description, Analysis, AI Roadmap, Career Recommendations, and Reports.</p>
    </section>
    """,
    unsafe_allow_html=True,
)

st.subheader("Get started")
st.markdown(
    "Choose a page from the sidebar to begin your analysis workflow. Your uploaded resume and job description remain available across all pages."
)

render_page_links(
    [
        "pages/1_Home.py",
        "pages/2_Resume_Upload.py",
        "pages/3_Job_Description.py",
        "pages/4_Analysis_Dashboard.py",
        "pages/5_AI_Learning_Roadmap.py",
        "pages/6_Career_Recommendations.py",
        "pages/7_Reports.py",
    ]
)
