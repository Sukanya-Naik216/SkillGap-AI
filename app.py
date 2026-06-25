from __future__ import annotations

import streamlit as st

from utils.streamlit_ui import configure_app

PAGES = [
    st.Page("pages/1_Home.py", title="Home", icon=":material/home:"),
    st.Page("pages/2_Resume_Upload.py", title="Resume Upload", icon=":material/upload_file:"),
    st.Page("pages/3_Job_Description.py", title="Job Description", icon=":material/description:"),
    st.Page("pages/4_Analysis_Dashboard.py", title="Analysis Dashboard", icon=":material/dashboard:"),
    st.Page("pages/5_AI_Learning_Roadmap.py", title="AI Learning Roadmap", icon=":material/map:"),
    st.Page("pages/6_Career_Recommendations.py", title="Career Recommendations", icon=":material/work:"),
    st.Page("pages/7_Reports.py", title="Reports", icon=":material/picture_as_pdf:"),
]


def main() -> None:
    """Entrypoint for the multi-page SkillGap AI app."""
    configure_app()
    selected_page = st.navigation(PAGES, position="sidebar", expanded=True)
    selected_page.run()


if __name__ == "__main__":
    main()

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
