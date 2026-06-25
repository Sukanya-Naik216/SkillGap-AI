from __future__ import annotations

import streamlit as st

from utils.streamlit_ui import (
    get_insights,
    prepare_page,
    render_analysis_gate,
    render_career_suggestions,
)


prepare_page(
    "Career Recommendations",
    "Review resume improvement tips, interview preparation prompts, and career growth guidance.",
)

if not render_analysis_gate("Career recommendations"):
    st.stop()

insights = get_insights()
if insights is None:
    st.error("Recommendation data is unavailable. Run the analysis again.")
    st.stop()

render_career_suggestions(insights["career_suggestions"])
