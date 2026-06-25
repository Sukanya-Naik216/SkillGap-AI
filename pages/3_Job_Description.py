from __future__ import annotations

import streamlit as st

from utils.resume_parser import FileValidationError, validate_text_input
from utils.streamlit_ui import (
    extract_document_skills,
    load_sample_job_description,
    prepare_page,
    process_job_upload,
    render_document_preview,
    render_skill_pills,
    store_job_description_text,
    sync_job_description_draft,
)


prepare_page(
    "Job Description",
    "Paste or upload the target role requirements. Saved text is used by the analysis dashboard and report.",
)

left, right = st.columns([0.95, 1.05])

with left:
    st.subheader("Job Input")
    uploaded_job = st.file_uploader(
        "Upload job description",
        type=["pdf", "docx", "txt"],
        help="Supported formats: PDF, DOCX, TXT.",
    )

    if uploaded_job is not None:
        signature = f"{uploaded_job.name}:{uploaded_job.size}"
        if signature != st.session_state.get("job_upload_signature"):
            try:
                process_job_upload(uploaded_job)
                st.success("Job description file validated and saved.")
                st.rerun()
            except FileValidationError as exc:
                st.error(str(exc))
            except Exception as exc:
                st.error(f"Job description upload could not be processed: {exc}")
        else:
            st.success("Uploaded job description is already saved in this session.")

    st.text_area(
        "Paste or edit job description",
        key="job_description_draft",
        height=330,
        placeholder="Paste the job description here...",
        on_change=sync_job_description_draft,
    )

    col1, col2 = st.columns(2)
    if col1.button("Save text", type="primary", use_container_width=True):
        try:
            validate_text_input(st.session_state.get("job_description_draft", ""), label="Job description")
            store_job_description_text(
                st.session_state["job_description_draft"],
                st.session_state.get("job_description_filename", ""),
                "Text area",
                validate=False,
            )
            st.success("Job description saved.")
        except FileValidationError as exc:
            st.error(str(exc))

    if col2.button("Use sample JD", use_container_width=True):
        try:
            load_sample_job_description()
            st.success("Sample job description loaded.")
            st.rerun()
        except Exception as exc:
            st.error(f"Sample job description could not be loaded: {exc}")

with right:
    render_document_preview(
        "Job Description Preview",
        st.session_state.get("job_description_text", ""),
        st.session_state.get("job_description_filename", ""),
        st.session_state.get("job_description_source", ""),
    )

if st.session_state.get("job_description_text"):
    skills = extract_document_skills(st.session_state["job_description_text"])
    col1, col2 = st.columns(2)
    with col1:
        render_skill_pills("Required Technical Skills", skills.technical_skills, "sg-pill-blue")
    with col2:
        render_skill_pills("Required Soft Skills", skills.soft_skills, "sg-pill-green")
