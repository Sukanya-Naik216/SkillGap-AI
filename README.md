# SkillGap AI

SkillGap AI is a Streamlit web application that compares a candidate resume against a job description, identifies skill gaps, calculates match and ATS scores, and generates a learning roadmap with career recommendations.

## Features

- Resume upload for PDF, DOCX, and TXT files
- Job description input through text area or file upload
- Technical and soft skill extraction with spaCy tokenization and keyword matching
- Match score, ATS compatibility score, matching skills, missing skills, and additional skills
- AI learning roadmap powered by Google Gemini when an API key is configured
- Local deterministic recommendations when no API key is available
- Interactive dashboard with progress indicators, pie chart, and bar chart
- Downloadable PDF report
- Sample resume and job description for quick testing

## Project Structure

```text
skillgap-ai/
|-- app.py
|-- requirements.txt
|-- README.md
|-- .env.example
|-- .gitignore
|-- pytest.ini
|-- utils/
|   |-- __init__.py
|   |-- resume_parser.py
|   |-- skill_extractor.py
|   |-- matcher.py
|   |-- ai_generator.py
|   |-- report_generator.py
|-- assets/
|   |-- .gitkeep
|-- data/
|   |-- sample_resume.txt
|   |-- sample_job_description.txt
|-- tests/
|   |-- test_skill_extractor.py
|   |-- test_matcher.py
```

## Setup

Use Python 3.11 or newer.

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Optional but recommended for stronger NLP tokenization:

```bash
python -m spacy download en_core_web_sm
```

Create a local environment file:

```bash
copy .env.example .env
```

Set your Gemini key in `.env`:

```text
GEMINI_API_KEY=your_google_gemini_api_key_here
GEMINI_MODEL=gemini-2.5-flash
```

The app still runs without a Gemini API key and uses local rule-based roadmap generation.

## Run

```bash
streamlit run app.py
```

Open the local URL shown by Streamlit. In the sidebar, you can load the bundled sample job description and enable the bundled sample resume.

## Test

```bash
pytest
```

## Notes

- Supported upload formats are `.pdf`, `.docx`, and `.txt`.
- Default upload size limit is 8 MB. Override it with `MAX_UPLOAD_SIZE_MB` in `.env`.
- Scanned image-only PDFs may not contain extractable text. Convert them with OCR before uploading.
