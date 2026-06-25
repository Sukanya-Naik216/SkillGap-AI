from __future__ import annotations

import streamlit as st

from utils.resume_parser import FileValidationError
from utils.streamlit_ui import (
    clear_analysis,
    extract_document_skills,
    load_sample_resume,
    prepare_page,
    process_resume_upload,
    render_document_preview,
    render_skill_pills,
)


prepare_page(
    "Resume Upload",
    "Upload and validate the candidate resume. Extracted text is preserved across all pages.",
)

left, right = st.columns([0.9, 1.1])

with left:
    st.subheader("Upload Resume")
    uploaded_resume = st.file_uploader(
        "Resume file",
        type=["pdf", "docx", "txt"],
        help="Supported formats: PDF, DOCX, TXT. Maximum size follows MAX_UPLOAD_SIZE_MB.",
    )

    if uploaded_resume is not None:
        signature = f"{uploaded_resume.name}:{uploaded_resume.size}"
        if signature != st.session_state.get("resume_upload_signature"):
            try:
                process_resume_upload(uploaded_resume)
                st.success("Resume validated and saved.")
            except FileValidationError as exc:
                st.error(str(exc))
            except Exception as exc:
                st.error(f"Resume upload could not be processed: {exc}")
        else:
            st.success("Resume is already saved in this session.")

    if st.button("Use bundled sample resume", use_container_width=True):
        try:
            load_sample_resume()
            st.success("Sample resume loaded.")
            st.rerun()
        except Exception as exc:
            st.error(f"Sample resume could not be loaded: {exc}")

    if st.session_state.get("resume_text") and st.button("Clear resume", use_container_width=True):
        st.session_state["resume_text"] = ""
        st.session_state["resume_filename"] = ""
        st.session_state["resume_source"] = ""
        st.session_state["resume_upload_signature"] = ""
        clear_analysis()
        st.rerun()

with right:
    render_document_preview(
        "Resume Preview",
        st.session_state.get("resume_text", ""),
        st.session_state.get("resume_filename", ""),
        st.session_state.get("resume_source", ""),
    )

if st.session_state.get("resume_text"):
    skills = extract_document_skills(st.session_state["resume_text"])
    col1, col2 = st.columns(2)
    with col1:
        render_skill_pills("Technical Skills Found", skills.technical_skills, "sg-pill-blue")
    with col2:
        render_skill_pills("Soft Skills Found", skills.soft_skills, "sg-pill-green")
