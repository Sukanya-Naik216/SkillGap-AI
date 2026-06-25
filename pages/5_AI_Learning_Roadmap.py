from __future__ import annotations

import streamlit as st

from utils.ai_generator import generate_ai_insights
from utils.streamlit_ui import (
    get_insights,
    get_match_result,
    prepare_page,
    render_analysis_gate,
    render_kpi_card,
    render_roadmap,
)


prepare_page(
    "AI Learning Roadmap",
    "Turn missing skills into a learning sequence, timeline, certifications, and portfolio projects.",
)

if not render_analysis_gate("The learning roadmap"):
    st.stop()

match_result = get_match_result()
insights = get_insights()
if match_result is None or insights is None:
    st.error("Analysis data is unavailable. Run the analysis again.")
    st.stop()

col1, col2, col3 = st.columns(3)
with col1:
    render_kpi_card("Missing Skills", str(len(match_result.missing_skills)), "Prioritized from the job", "red")
with col2:
    render_kpi_card(
        "Timeline",
        str(insights["roadmap"].get("estimated_timeline", "Not available")),
        "Estimated effort",
        "teal",
    )
with col3:
    render_kpi_card("Projects", str(len(insights["roadmap"].get("suggested_projects", []))), "Portfolio proof", "blue")

if st.button("Regenerate AI roadmap and recommendations", use_container_width=True):
    with st.spinner("Regenerating roadmap and recommendations..."):
        st.session_state["insights"] = generate_ai_insights(
            match_result,
            st.session_state["resume_text"],
            st.session_state["job_description_text"],
        )
    st.success("AI insights refreshed.")
    st.rerun()

render_roadmap(st.session_state["insights"]["roadmap"])
