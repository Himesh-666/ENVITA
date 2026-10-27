"""General-purpose helper utilities for ENVITA."""
import re
from datetime import datetime


def format_datetime(dt=None):
    """Return a formatted datetime string. Defaults to now."""
    if dt is None:
        dt = datetime.utcnow()
    return dt.strftime("%B %d, %Y at %H:%M UTC")


def safe_float(value, default=0.0):
    """Convert value to float safely."""
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def safe_int(value, default=0):
    """Convert value to int safely."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def markdown_to_html(text: str) -> str:
    """
    Lightweight Markdown → HTML converter for AI response rendering.
    Handles: ## headers, **bold**, bullet lists, line breaks.
    """
    if not text:
        return ""

    lines = text.split("\n")
    html_lines = []
    in_list = False

    for line in lines:
        stripped = line.strip()

        # H2 headers  (## text)
        if stripped.startswith("## "):
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            content = stripped[3:].strip()
            # Inline bold
            content = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", content)
            html_lines.append(f'<h5 class="ai-section-title mt-3 mb-2">{content}</h5>')

        # Bullet list items
        elif stripped.startswith("- ") or stripped.startswith("* "):
            if not in_list:
                html_lines.append('<ul class="ai-list">')
                in_list = True
            content = stripped[2:].strip()
            content = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", content)
            html_lines.append(f"  <li>{content}</li>")

        # Empty line
        elif stripped == "":
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            html_lines.append("")

        # Regular paragraph
        else:
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            content = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", stripped)
            html_lines.append(f"<p>{content}</p>")

    if in_list:
        html_lines.append("</ul>")

    return "\n".join(html_lines)


def uv_description(uv_index: float) -> str:
    uv = safe_float(uv_index)
    if uv < 3:   return "Low"
    if uv < 6:   return "Moderate"
    if uv < 8:   return "High"
    if uv < 11:  return "Very High"
    return "Extreme"


def uv_color_class(uv_index: float) -> str:
    uv = safe_float(uv_index)
    if uv < 3:  return "success"
    if uv < 6:  return "warning"
    if uv < 8:  return "orange"
    if uv < 11: return "danger"
    return "dark"


def temp_description(temp: float) -> str:
    t = safe_float(temp)
    if t < 0:   return "Freezing"
    if t < 10:  return "Cold"
    if t < 20:  return "Cool"
    if t < 28:  return "Comfortable"
    if t < 35:  return "Warm"
    if t < 38:  return "Hot"
    return "Extreme Heat"
