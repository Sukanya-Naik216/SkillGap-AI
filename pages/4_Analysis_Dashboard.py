from __future__ import annotations

import streamlit as st

from utils.streamlit_ui import (
    get_match_result,
    has_current_analysis,
    has_required_inputs,
    prepare_page,
    render_analysis_gate,
    render_metric_panel,
    render_page_links,
    render_skill_charts,
    render_skill_details,
    run_full_analysis,
)


prepare_page(
    "Analysis Dashboard",
    "Review match quality, ATS readiness, detected skills, missing skills, and visual comparisons.",
)

if not has_required_inputs():
    st.warning("Add both a resume and a job description before running analysis.")
    render_page_links(["pages/2_Resume_Upload.py", "pages/3_Job_Description.py"])
    st.stop()

col1, col2 = st.columns([1, 1])
with col1:
    if st.button("Run analysis", type="primary", use_container_width=True):
        if run_full_analysis():
            st.rerun()
with col2:
    if st.button("Refresh analysis", use_container_width=True):
        if run_full_analysis():
            st.rerun()

if not has_current_analysis():
    render_analysis_gate("The dashboard")
    st.stop()

match_result = get_match_result()
if match_result is None:
    st.error("Analysis data is unavailable. Run the analysis again.")
    st.stop()

render_metric_panel(match_result)

st.subheader("Score Breakdown")
cols = st.columns(3)
cols[0].metric("Skill Coverage", f"{match_result.skill_coverage:.1f}%")
cols[1].metric("Keyword Overlap", f"{match_result.keyword_overlap:.1f}%")
cols[2].metric("Semantic Similarity", f"{match_result.semantic_similarity:.1f}%")

render_skill_charts(match_result)
render_skill_details(match_result)
