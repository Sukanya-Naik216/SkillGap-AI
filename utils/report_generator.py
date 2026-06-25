from __future__ import annotations

from datetime import datetime
from typing import Any

from fpdf import FPDF

from utils.matcher import MatchResult


def _clean_text(value: Any) -> str:
    replacements = {
        "\u2013": "-",
        "\u2014": "-",
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u2022": "-",
    }
    text = str(value)
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text.encode("latin-1", "replace").decode("latin-1")


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


class SkillGapPDF(FPDF):
    def header(self) -> None:
        self.set_font("Helvetica", "B", 14)
        self.cell(0, 10, "SkillGap AI Report", new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(20, 83, 45)
        self.line(10, 20, 200, 20)
        self.ln(8)

    def footer(self) -> None:
        self.set_y(-15)
        self.set_font("Helvetica", "", 8)
        self.set_text_color(90, 90, 90)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")


def _section(pdf: FPDF, title: str) -> None:
    pdf.ln(4)
    pdf.set_x(pdf.l_margin)
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 8, _clean_text(title), new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(20, 20, 20)


def _bullet_list(pdf: FPDF, items: list[Any]) -> None:
    pdf.set_x(pdf.l_margin)
    if not items:
        pdf.multi_cell(0, 6, "- None")
        return
    for item in items:
        pdf.set_x(pdf.l_margin)
        pdf.multi_cell(0, 6, f"- {_clean_text(item)}")


def _write_metric_grid(pdf: FPDF, match_result: MatchResult) -> None:
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(47, 9, "Match Score", border=1)
    pdf.cell(47, 9, "ATS Score", border=1)
    pdf.cell(47, 9, "Skill Coverage", border=1)
    pdf.cell(47, 9, "Keyword Overlap", border=1, new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 11)
    pdf.cell(47, 9, f"{match_result.match_percentage:.1f}%", border=1)
    pdf.cell(47, 9, f"{match_result.ats_score:.1f}/100", border=1)
    pdf.cell(47, 9, f"{match_result.skill_coverage:.1f}%", border=1)
    pdf.cell(47, 9, f"{match_result.keyword_overlap:.1f}%", border=1, new_x="LMARGIN", new_y="NEXT")


def _write_learning_sequence(pdf: FPDF, sequence: list[dict[str, Any]]) -> None:
    if not sequence:
        pdf.multi_cell(0, 6, "- No roadmap phases generated.")
        return

    for item in sequence:
        phase = item.get("phase", "")
        focus = _clean_text(item.get("focus", "Learning phase"))
        duration = _clean_text(item.get("duration", ""))
        heading = f"Phase {phase}: {focus}" if phase else focus
        if duration:
            heading += f" ({duration})"
        pdf.set_x(pdf.l_margin)
        pdf.set_font("Helvetica", "B", 10)
        pdf.multi_cell(0, 6, heading)
        pdf.set_font("Helvetica", "", 10)
        _bullet_list(pdf, _as_list(item.get("activities")))


def create_pdf_report(
    match_result: MatchResult,
    roadmap: dict[str, Any],
    career_suggestions: dict[str, Any],
) -> bytes:
    """Build a downloadable PDF report from the completed analysis."""
    pdf = SkillGapPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_title("SkillGap AI Report")

    pdf.set_font("Helvetica", "", 10)
    pdf.set_x(pdf.l_margin)
    pdf.multi_cell(0, 6, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

    _section(pdf, "Scores")
    _write_metric_grid(pdf, match_result)

    _section(pdf, "Matching Skills")
    _bullet_list(pdf, match_result.matching_skills)

    _section(pdf, "Missing Skills")
    _bullet_list(pdf, match_result.missing_skills)

    _section(pdf, "Additional Resume Skills")
    _bullet_list(pdf, match_result.additional_skills)

    _section(pdf, "Learning Roadmap")
    pdf.set_x(pdf.l_margin)
    pdf.multi_cell(0, 6, f"Estimated timeline: {_clean_text(roadmap.get('estimated_timeline', 'Not available'))}")
    _write_learning_sequence(pdf, _as_list(roadmap.get("learning_sequence")))

    _section(pdf, "Suggested Projects")
    _bullet_list(pdf, _as_list(roadmap.get("suggested_projects")))

    _section(pdf, "Recommended Certifications")
    _bullet_list(pdf, _as_list(roadmap.get("recommended_certifications")))

    _section(pdf, "Resume Improvement Tips")
    _bullet_list(pdf, _as_list(career_suggestions.get("resume_improvement_tips")))

    _section(pdf, "Interview Preparation")
    _bullet_list(pdf, _as_list(career_suggestions.get("interview_preparation_suggestions")))

    _section(pdf, "Career Growth Recommendations")
    _bullet_list(pdf, _as_list(career_suggestions.get("career_growth_recommendations")))

    output = pdf.output(dest="S")
    if isinstance(output, str):
        return output.encode("latin-1")
    return bytes(output)
