"""
File: app/services/export_service.py
Purpose: Generate PDF and Markdown exports of a complete startup blueprint.
Responsibilities:
  - Compile all agent reports into an ordered blueprint document
  - Generate a styled PDF using ReportLab
  - Generate a clean Markdown file
Dependencies:
  - reportlab (PDF generation)
  - app.models.idea (Idea)
  - app.models.report (Report, AgentType)
"""

import io
from typing import Any

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from app.models.idea import Idea
from app.models.report import AgentType, Report

# Ordered list of agent sections in the blueprint output
BLUEPRINT_ORDER = [
    AgentType.MARKET_RESEARCH,
    AgentType.COMPETITOR_ANALYSIS,
    AgentType.PRODUCT_MANAGER,
    AgentType.TECHNICAL_ARCHITECT,
    AgentType.DATABASE_ARCHITECT,
    AgentType.API_DESIGN,
    AgentType.UIUX,
    AgentType.ROADMAP,
    AgentType.MARKETING,
    AgentType.RISK_ANALYSIS,
]

AGENT_LABELS = {
    AgentType.MARKET_RESEARCH: "1. Market Research",
    AgentType.COMPETITOR_ANALYSIS: "2. Competitor Analysis",
    AgentType.PRODUCT_MANAGER: "3. Product Requirements",
    AgentType.TECHNICAL_ARCHITECT: "4. Technical Architecture",
    AgentType.DATABASE_ARCHITECT: "5. Database Design",
    AgentType.API_DESIGN: "6. API Design",
    AgentType.UIUX: "7. UI/UX Design",
    AgentType.ROADMAP: "8. MVP Roadmap",
    AgentType.MARKETING: "9. Go-To-Market Strategy",
    AgentType.RISK_ANALYSIS: "10. Risk Analysis",
}


class ExportService:
    """
    Description: Generates downloadable exports of the startup blueprint.
    Responsibilities:
      - Build a report map from a list of Report objects
      - Generate PDF binary via ReportLab
      - Generate Markdown text
    """

    def __init__(self, idea: Idea, reports: list[Report]):
        """
        Purpose: Initialize with the idea and its completed reports.
        Parameters:
          idea: The Idea ORM object.
          reports: List of Report ORM objects (any status — completed ones used).
        """
        self.idea = idea
        self.report_map: dict[AgentType, dict[str, Any]] = {
            r.agent_type: r.output for r in reports if r.output
        }

    def generate_markdown(self) -> str:
        """
        Purpose: Build a complete Markdown startup blueprint.
        Returns:
          str: Full Markdown document as a string.
        """
        lines = [
            f"# {self.idea.title} — Startup Blueprint",
            "",
            f"**Problem Statement:** {self.idea.problem_statement}",
            f"**Target Audience:** {self.idea.target_audience}",
            "",
            "---",
            "",
        ]

        for agent_type in BLUEPRINT_ORDER:
            label = AGENT_LABELS[agent_type]
            output = self.report_map.get(agent_type)

            lines.append(f"## {label}")
            lines.append("")

            if not output:
                lines.append("*Analysis not completed.*")
                lines.append("")
                continue

            self._render_section_markdown(lines, output)
            lines.append("")

        return "\n".join(lines)

    def _render_section_markdown(self, lines: list, output: dict) -> None:
        """
        Purpose: Recursively render a dict as Markdown key-value pairs.
        Parameters:
          lines: Mutable list of strings to append to.
          output: The agent's output dict.
        """
        for key, value in output.items():
            formatted_key = key.replace("_", " ").title()
            if isinstance(value, list):
                lines.append(f"**{formatted_key}:**")
                for item in value:
                    if isinstance(item, dict):
                        for k, v in item.items():
                            lines.append(f"  - **{k}:** {v}")
                    else:
                        lines.append(f"- {item}")
            elif isinstance(value, dict):
                lines.append(f"**{formatted_key}:**")
                for k, v in value.items():
                    lines.append(f"  - **{k}:** {v}")
            else:
                lines.append(f"**{formatted_key}:** {value}")
            lines.append("")

    def generate_pdf(self) -> bytes:
        """
        Purpose: Build a complete PDF startup blueprint using ReportLab.
        Returns:
          bytes: Binary PDF content ready to stream as a response.
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=2 * cm,
            leftMargin=2 * cm,
            topMargin=2 * cm,
            bottomMargin=2 * cm,
        )

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            "BlueprintTitle",
            parent=styles["Title"],
            fontSize=24,
            textColor=colors.HexColor("#1a1a2e"),
            spaceAfter=12,
        )
        heading_style = ParagraphStyle(
            "SectionHeading",
            parent=styles["Heading1"],
            fontSize=16,
            textColor=colors.HexColor("#16213e"),
            spaceBefore=20,
            spaceAfter=8,
        )
        body_style = ParagraphStyle(
            "Body",
            parent=styles["BodyText"],
            fontSize=10,
            leading=16,
            spaceAfter=6,
        )

        story = [
            Paragraph(f"{self.idea.title}", title_style),
            Paragraph("Startup Blueprint — Generated by FounderOS", styles["Italic"]),
            Spacer(1, 0.5 * cm),
            Paragraph(f"<b>Problem:</b> {self.idea.problem_statement}", body_style),
            Paragraph(f"<b>Target Audience:</b> {self.idea.target_audience}", body_style),
            Spacer(1, 0.5 * cm),
        ]

        for agent_type in BLUEPRINT_ORDER:
            label = AGENT_LABELS[agent_type]
            output = self.report_map.get(agent_type)

            story.append(Paragraph(label, heading_style))

            if not output:
                story.append(Paragraph("Analysis not completed.", body_style))
                continue

            for key, value in output.items():
                formatted_key = key.replace("_", " ").title()
                if isinstance(value, list):
                    story.append(Paragraph(f"<b>{formatted_key}:</b>", body_style))
                    for item in value:
                        text = str(item) if not isinstance(item, dict) else str(item)
                        story.append(Paragraph(f"• {text}", body_style))
                elif isinstance(value, str):
                    story.append(
                        Paragraph(f"<b>{formatted_key}:</b> {value}", body_style)
                    )
                story.append(Spacer(1, 0.2 * cm))

        doc.build(story)
        return buffer.getvalue()
