from __future__ import annotations

import streamlit as st

from utils.resume_parser import FileValidationError
from utils.streamlit_ui import (
    create_current_report,
    get_insights,
    get_match_result,
    prepare_page,
    render_analysis_gate,
    render_report_preview,
)


prepare_page(
    "Reports",
    "Generate a polished PDF report with match scores, ATS score, missing skills, roadmap, and recommendations.",
)

if not render_analysis_gate("Reports"):
    st.stop()

match_result = get_match_result()
insights = get_insights()
if match_result is None or insights is None:
    st.error("Report data is unavailable. Run the analysis again.")
    st.stop()

render_report_preview(match_result, insights)

st.subheader("Generate PDF")
try:
    if st.button("Generate report", type="primary", use_container_width=True):
        with st.spinner("Building PDF report..."):
            create_current_report()
        st.success("Report generated.")

    report_bytes = st.session_state.get("last_report_bytes")
    if report_bytes is None:
        report_bytes = create_current_report()

    st.download_button(
        "Download PDF report",
        data=report_bytes,
        file_name="skillgap-ai-report.pdf",
        mime="application/pdf",
        use_container_width=True,
    )
except FileValidationError as exc:
    st.error(str(exc))
except Exception as exc:
    st.error(f"PDF report could not be generated: {exc}")
