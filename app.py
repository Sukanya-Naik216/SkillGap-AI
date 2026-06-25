from __future__ import annotations

import streamlit as st

from utils.streamlit_ui import prepare_page, render_page_links

prepare_page(
    "SkillGap AI",
)

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

st.info("Use the sidebar navigation to explore all SkillGap AI features.")
