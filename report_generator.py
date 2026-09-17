from io import BytesIO
from datetime import datetime
from xml.sax.saxutils import escape

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
)


def _chart_image(fig, width=460, height=240):
    image_buffer = BytesIO()
    fig.savefig(image_buffer, format="png", dpi=160, bbox_inches="tight")
    plt.close(fig)
    image_buffer.seek(0)
    img = Image(image_buffer, width=width, height=height)
    img.hAlign = "CENTER"
    return img


def _language_chart(languages):
    items = sorted(languages.items(), key=lambda x: x[1], reverse=True)[:8]
    if not items:
        return None
    labels = [k for k, _ in items]
    values = [v for _, v in items]
    fig, ax = plt.subplots(figsize=(7, 3.4))
    ax.bar(labels, values)
    ax.set_title("Top Languages by Code Volume")
    ax.set_ylabel("Bytes")
    ax.tick_params(axis="x", rotation=30)
    fig.tight_layout()
    return _chart_image(fig)


def _growth_chart(repos_per_year):
    if not repos_per_year:
        return None
    years = list(repos_per_year.keys())
    values = list(repos_per_year.values())
    fig, ax = plt.subplots(figsize=(7, 3.2))
    ax.plot(years, values, marker="o")
    ax.set_title("Repositories Created per Year")
    ax.set_xlabel("Year")
    ax.set_ylabel("Repositories")
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    return _chart_image(fig)


def build_report_pdf(user, repos, score, score_breakdown, languages, insights, repos_per_year=None):
    """Generate a professional PDF report from GitHub analysis results."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=42,
        bottomMargin=42,
        title="GitHub Developer Report Card",
        author="GitHub Developer Report Card",
    )

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="ReportTitle", parent=styles["Title"], alignment=TA_CENTER, fontSize=22, spaceAfter=8))
    styles.add(ParagraphStyle(name="SubTitle", parent=styles["Normal"], alignment=TA_CENTER, fontSize=10, textColor=colors.grey, spaceAfter=18))
    styles.add(ParagraphStyle(name="Section", parent=styles["Heading2"], fontSize=14, spaceBefore=12, spaceAfter=8))

    def safe(value):
        return escape(str(value))

    story = []
    login = user.get("login", "Unknown")
    name = user.get("name") or login
    bio = user.get("bio") or "No bio provided."
    profile_url = user.get("html_url", "")
    created = user.get("created_at", "")[:10] or "N/A"

    story.append(Paragraph("GitHub Developer Report Card", styles["ReportTitle"]))
    story.append(Paragraph(
        f"Generated for <b>{safe(name)}</b> (@{safe(login)}) • {datetime.now().strftime('%d %b %Y')}",
        styles["SubTitle"]
    ))

    profile_data = [
        ["Profile", "Details"],
        ["Name", safe(name)],
        ["Username", f"@{safe(login)}"],
        ["Bio", safe(bio)],
        ["Followers", str(user.get("followers", 0))],
        ["Following", str(user.get("following", 0))],
        ["Public Repositories", str(user.get("public_repos", 0))],
        ["Account Created", created],
        ["GitHub", safe(profile_url)],
    ]
    table = Table(profile_data, colWidths=[135, 355], repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#24292f")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.lightgrey),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("PADDING", (0, 0), (-1, -1), 6),
    ]))
    story += [Paragraph("1. Profile Overview", styles["Section"]), table, Spacer(1, 8)]

    story.append(Paragraph("2. Profile Strength Score", styles["Section"]))
    story.append(Paragraph(f"<b>{score}/100</b>", styles["Heading1"]))
    breakdown = [["Category", "Score"]] + [[safe(k), safe(v)] for k, v in score_breakdown.items()]
    score_table = Table(breakdown, colWidths=[300, 90], repeatRows=1)
    score_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#24292f")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.lightgrey),
        ("PADDING", (0, 0), (-1, -1), 6),
    ]))
    story += [score_table, Spacer(1, 8)]
    story.append(Paragraph(
        "Note: this score summarizes public GitHub profile and repository signals; it is not a measure of programming ability.",
        styles["Normal"]
    ))

    story.append(Paragraph("3. Technology Analysis", styles["Section"]))
    lang_chart = _language_chart(languages)
    if lang_chart:
        story += [lang_chart, Spacer(1, 8)]
    lang_rows = [["Language", "Code Volume"]]
    for lang, value in sorted(languages.items(), key=lambda x: x[1], reverse=True):
        lang_rows.append([safe(lang), f"{value:,}"])
    if len(lang_rows) == 1:
        lang_rows.append(["No language data", "—"])
    lang_table = Table(lang_rows, colWidths=[220, 170], repeatRows=1)
    lang_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#24292f")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.lightgrey),
        ("PADDING", (0, 0), (-1, -1), 6),
    ]))
    story += [lang_table, Spacer(1, 8)]

    story.append(Paragraph("4. Repository Activity", styles["Section"]))
    growth_chart = _growth_chart(repos_per_year or {})
    if growth_chart:
        story += [growth_chart, Spacer(1, 8)]

    story.append(Paragraph("5. Repository Analysis", styles["Section"]))
    repo_rows = [["Repository", "Language", "Stars", "Forks"]]
    for r in sorted(repos, key=lambda x: x.get("stargazers_count", 0), reverse=True)[:15]:
        repo_rows.append([
            safe(r.get("name", ""))[:32],
            safe(r.get("language") or "N/A"),
            str(r.get("stargazers_count", 0)),
            str(r.get("forks_count", 0)),
        ])
    if len(repo_rows) == 1:
        repo_rows.append(["No public repositories", "—", "—", "—"])
    repo_table = Table(repo_rows, colWidths=[220, 120, 55, 55], repeatRows=1)
    repo_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#24292f")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.lightgrey),
        ("PADDING", (0, 0), (-1, -1), 5),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
    ]))
    story += [repo_table, Spacer(1, 8)]

    story.append(Paragraph("6. Developer Insights", styles["Section"]))
    if insights:
        for insight in insights:
            story.append(Paragraph(f"• {safe(insight)}", styles["Normal"]))
            story.append(Spacer(1, 4))
    else:
        story.append(Paragraph("No additional insights available.", styles["Normal"]))

    story.append(Spacer(1, 18))
    story.append(Paragraph("Generated by GitHub Developer Report Card", styles["SubTitle"]))
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()
