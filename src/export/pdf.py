"""PDF export for the AI Governance Framework Helper using WeasyPrint."""

import logging
from typing import Optional

from src.export.markdown import generate_markdown

logger = logging.getLogger(__name__)

HTML_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }}
h1 {{ color: #1a237e; border-bottom: 2px solid #1a237e; padding-bottom: 10px; }}
h2 {{ color: #283593; margin-top: 30px; }}
h3 {{ color: #3949ab; }}
blockquote {{ background: #f5f5f5; border-left: 4px solid #1a237e; padding: 10px 20px; margin: 20px 0; }}
table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
th {{ background-color: #e8eaf6; }}
.warning {{ color: #d32f2f; font-weight: bold; }}
.high {{ color: #d32f2f; }}
.medium {{ color: #f57c00; }}
.low {{ color: #388e3c; }}
ul {{ margin: 5px 0; }}
</style>
</head>
<body>
{content}
</body>
</html>"""


def generate_pdf(advice: dict, profile: dict) -> Optional[bytes]:
    """Generate a PDF compliance report using WeasyPrint.

    Uses WeasyPrint to convert HTML to PDF. Returns None if WeasyPrint
    is not available (the API layer handles the fallback to Markdown).

    Args:
        advice: ComplianceAdvice dictionary.
        profile: ProjectProfile dictionary.

    Returns:
        PDF file content as bytes, or None if PDF generation fails.
    """
    # Generate markdown first, then convert to HTML
    md_content = generate_markdown(advice, profile)
    html_content = _markdown_to_html(md_content)
    full_html = HTML_TEMPLATE.format(content=html_content)

    try:
        from weasyprint import HTML

        pdf_bytes = HTML(string=full_html).write_pdf()
        return pdf_bytes
    except ImportError:
        logger.warning("WeasyPrint not installed. PDF generation unavailable.")
        return None
    except Exception as e:
        logger.error(f"PDF generation failed: {e}")
        return None


def _markdown_to_html(md_text: str) -> str:
    """Simple markdown to HTML conversion for the report.

    Converts the structured markdown output from generate_markdown into
    basic HTML suitable for PDF rendering via WeasyPrint.
    """
    lines = md_text.split("\n")
    html_lines: list[str] = []
    in_list = False

    for line in lines:
        stripped = line.strip()

        if stripped.startswith("# "):
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            html_lines.append(f"<h1>{_escape_html(stripped[2:])}</h1>")
        elif stripped.startswith("## "):
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            html_lines.append(f"<h2>{_escape_html(stripped[3:])}</h2>")
        elif stripped.startswith("### "):
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            html_lines.append(f"<h3>{_escape_html(stripped[4:])}</h3>")
        elif stripped.startswith("> "):
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            html_lines.append(f"<blockquote>{_escape_html(stripped[2:])}</blockquote>")
        elif stripped.startswith("- "):
            if not in_list:
                html_lines.append("<ul>")
                in_list = True
            content = stripped[2:]
            if content.startswith("[ ] "):
                content = content[4:]
            html_lines.append(f"<li>{_escape_html(content)}</li>")
        elif stripped.startswith("  - "):
            # Nested list item
            content = stripped[4:]
            if not in_list:
                html_lines.append("<ul>")
                in_list = True
            html_lines.append(f"<li style=\"margin-left: 20px;\">{_escape_html(content)}</li>")
        elif stripped.startswith("    - "):
            # Double-nested list item
            content = stripped[6:]
            if not in_list:
                html_lines.append("<ul>")
                in_list = True
            html_lines.append(f"<li style=\"margin-left: 40px;\">{_escape_html(content)}</li>")
        elif stripped.startswith("**") and stripped.endswith("**"):
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            html_lines.append(f"<p><strong>{_escape_html(stripped[2:-2])}</strong></p>")
        elif stripped == "":
            if in_list:
                html_lines.append("</ul>")
                in_list = False
        else:
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            html_lines.append(f"<p>{_escape_html(stripped)}</p>")

    if in_list:
        html_lines.append("</ul>")

    return "\n".join(html_lines)


def _escape_html(text: str) -> str:
    """Escape HTML special characters in text content."""
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )
