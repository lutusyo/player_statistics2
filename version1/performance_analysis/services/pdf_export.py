
from io import BytesIO

from django.http import HttpResponse

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
    KeepTogether,
)


NAVY = colors.HexColor("#17365D")
BLUE = colors.HexColor("#D9EAF7")
LIGHT_GREY = colors.HexColor("#F3F5F7")
DARK_GREY = colors.HexColor("#555555")
WHITE = colors.white


def make_styles():
    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        name="ReportTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=25,
        textColor=NAVY,
        alignment=TA_CENTER,
        spaceAfter=8 * mm,
    ))

    styles.add(ParagraphStyle(
        name="TableHeaderText",
        parent=styles["BodyText"],
        fontName="Helvetica-Bold",
        fontSize=7,
        leading=9,
        textColor=WHITE,
    ))

    styles.add(ParagraphStyle(
        name="SectionHeading",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=15,
        textColor=NAVY,
        spaceBefore=5 * mm,
        spaceAfter=3 * mm,
    ))

    styles.add(ParagraphStyle(
        name="SmallText",
        parent=styles["BodyText"],
        fontSize=8,
        leading=10,
    ))

    styles.add(ParagraphStyle(
        name="TableText",
        parent=styles["BodyText"],
        fontSize=7,
        leading=9,
    ))

    styles.add(ParagraphStyle(
        name="InsightText",
        parent=styles["BodyText"],
        fontSize=9,
        leading=12,
        spaceAfter=3 * mm,
    ))

    return styles


def cell(value, style):
    if value is None or value == "":
        value = "-"
    return Paragraph(str(value), style)


def make_table(headers, rows, widths=None):
    styles = make_styles()

    table_data = [
        [cell(value, styles["TableHeaderText"]) for value in headers]
    ]

    for row in rows:
        table_data.append([
            cell(value, styles["TableText"]) for value in row
        ])

    table = Table(
        table_data,
        colWidths=widths,
        repeatRows=1,
        hAlign="LEFT",
    )

    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
        ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#D5DDE5")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, LIGHT_GREY]),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))

    return table


def add_page_number(canvas, doc):
    canvas.saveState()
    page_width, page_height = doc.pagesize

    canvas.setStrokeColor(colors.HexColor("#D5DDE5"))
    canvas.line(
        15 * mm,
        13 * mm,
        page_width - 15 * mm,
        13 * mm,
    )

    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(DARK_GREY)

    canvas.drawString(
        15 * mm,
        8 * mm,
        "Football Performance Analysis",
    )

    canvas.drawRightString(
        page_width - 15 * mm,
        8 * mm,
        f"Page {doc.page}",
    )

    canvas.restoreState()


def export_analysis_pdf(run):
    report = run.results_snapshot or {}

    analysis = report.get("analysis", {})
    periods = report.get("periods", [])
    teams = report.get("teams", [])
    results = report.get("results", [])
    comparisons = report.get("comparisons", [])
    insights = report.get("insights", [])
    player_analysis = report.get("player_analysis", [])

    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        rightMargin=12 * mm,
        leftMargin=12 * mm,
        topMargin=15 * mm,
        bottomMargin=19 * mm,
        title=analysis.get("name", run.analysis.name),
        author="Football Performance Analysis",
    )

    styles = make_styles()
    story = []

    # TITLE
    story.append(Paragraph(
        "FOOTBALL PERFORMANCE ANALYSIS",
        styles["ReportTitle"],
    ))

    story.append(Paragraph(
        analysis.get("name", run.analysis.name),
        styles["Heading1"],
    ))

    generated = (
        run.generated_at.strftime("%d %B %Y, %H:%M")
        if run.generated_at else "-"
    )

    story.append(Paragraph(
        f"<b>Generated:</b> {generated} &nbsp;&nbsp; "
        f"<b>Analysis Type:</b> "
        f"{analysis.get('analysis_type', '-')}",
        styles["SmallText"],
    ))

    story.append(Spacer(1, 5 * mm))

    # ANALYSIS OVERVIEW
    story.append(Paragraph("Analysis Overview", styles["SectionHeading"]))

    overview_rows = [
        ["Selected Teams", ", ".join(
            team.get("name", "") for team in teams
        ) or "-"],
        ["Number of Teams", len(teams)],
        ["Number of Periods", len(periods)],
        ["Generated By", str(run.generated_by) if run.generated_by else "-"],
    ]

    story.append(make_table(["Item", "Details"], overview_rows))
    story.append(Spacer(1, 4 * mm))

    # PERIODS
    story.append(Paragraph("Reporting Periods", styles["SectionHeading"]))

    period_rows = [
        [
            period.get("name"),
            period.get("start_date"),
            period.get("end_date"),
        ]
        for period in periods
    ]

    if period_rows:
        story.append(make_table(
            ["Period", "Start Date", "End Date"],
            period_rows,
            [100 * mm, 45 * mm, 45 * mm],
        ))
    else:
        story.append(Paragraph(
            "No reporting periods available.",
            styles["SmallText"],
        ))

    # TEAM PERFORMANCE
    story.append(Paragraph("Team Performance", styles["SectionHeading"]))

    performance_headers = [
        "Period", "Team", "Played", "W", "D", "L",
        "GF", "GA", "GD", "Pts", "Win %",
        "Players", "Minutes",
    ]

    performance_rows = []

    for item in results:
        performance_rows.append([
            item.get("period_name", "-"),
            item.get("team_name", "-"),
            item.get("played", 0),
            item.get("won", 0),
            item.get("drawn", 0),
            item.get("lost", 0),
            item.get("goals_for", 0),
            item.get("goals_against", 0),
            item.get("goal_difference", 0),
            item.get("points", 0),
            item.get("win_percentage", 0),
            item.get("players_used", 0),
            item.get("total_player_minutes", 0),
        ])

    if performance_rows:
        story.append(make_table(
            performance_headers,
            performance_rows,
        ))
    else:
        story.append(Paragraph(
            "No team performance results available.",
            styles["SmallText"],
        ))

    story.append(Spacer(1, 4 * mm))

    # SHOOTING AND PASSING
    story.append(Paragraph(
        "Shooting and Passing Performance",
        styles["SectionHeading"],
    ))

    technical_headers = [
        "Period", "Team", "Shots", "On Target",
        "Shooting Accuracy %", "Passes", "Completed",
        "Passing Accuracy %",
    ]

    technical_rows = []

    for item in results:
        technical_rows.append([
            item.get("period_name", "-"),
            item.get("team_name", "-"),
            item.get("shots", 0),
            item.get("shots_on_target", 0),
            item.get("shooting_accuracy", 0),
            item.get("passes_attempted", 0),
            item.get("passes_completed", 0),
            item.get("pass_accuracy", 0),
        ])

    if technical_rows:
        story.append(make_table(technical_headers, technical_rows))
    else:
        story.append(Paragraph(
            "No shooting or passing data available.",
            styles["SmallText"],
        ))

    # PERIOD COMPARISONS
    story.append(PageBreak())
    story.append(Paragraph("Period Comparisons", styles["SectionHeading"]))

    comparison_rows = []

    for item in comparisons:
        changes = item.get("changes") or {}

        for metric, change in changes.items():
            if change is None:
                continue

            comparison_rows.append([
                item.get("team_name", "-"),
                item.get("period_name", "-"),
                item.get("previous_period_name") or "-",
                metric.replace("_", " ").title(),
                change,
                "Percentage points"
                if metric in item.get("percentage_metrics", [])
                else "Value",
            ])

    if comparison_rows:
        story.append(make_table(
            ["Team", "Current Period", "Previous Period",
             "Metric", "Change", "Unit"],
            comparison_rows,
        ))
    else:
        story.append(Paragraph(
            "No period comparisons available.",
            styles["SmallText"],
        ))

    # PERFORMANCE INSIGHTS
    story.append(Paragraph("Performance Insights", styles["SectionHeading"]))

    insight_count = 0

    for item in insights:
        for insight in item.get("insights", []):
            insight_count += 1

            block = [
                Paragraph(
                    f"<b>{item.get('team_name', '-')} — "
                    f"{item.get('period_name', '-')}</b>",
                    styles["SmallText"],
                ),
                Paragraph(
                    f"<b>{insight.get('category', 'General')} | "
                    f"{insight.get('metric', '-')} | "
                    f"{insight.get('status', '-')}</b>",
                    styles["SmallText"],
                ),
                Paragraph(
                    str(insight.get("message", "")),
                    styles["InsightText"],
                ),
            ]

            story.append(KeepTogether(block))

    if not insight_count:
        story.append(Paragraph(
            "No performance insights available.",
            styles["SmallText"],
        ))

    # PLAYER MINUTES
    story.append(Paragraph("Player Minutes", styles["SectionHeading"]))

    player_rows = []

    for item in results:
        for player in item.get("player_details", []):
            player_rows.append([
                item.get("period_name", "-"),
                item.get("team_name", "-"),
                player.get("player_name", "-"),
                player.get("appearances", 0),
                player.get("minutes", 0),
            ])

    if player_rows:
        story.append(make_table(
            ["Period", "Team", "Player", "Appearances", "Minutes"],
            player_rows,
        ))
    else:
        story.append(Paragraph(
            "No player appearance or minute data available.",
            styles["SmallText"],
        ))

    # PLAYER PERFORMANCE
    story.append(PageBreak())
    story.append(Paragraph(
        "Individual Player Performance",
        styles["SectionHeading"],
    ))

    player_headers = [
        "Player", "Apps", "Starts", "Sub Apps",
        "Minutes", "Avg Min", "Goals", "Assists",
        "Pre-Assists", "Contributions", "Shots", "On Target",
    ]

    player_count = 0

    for period in player_analysis:
        period_name = period.get("period_name", "-")

        for team in period.get("teams", []):
            players = team.get("players", [])

            if not players:
                continue

            story.append(Paragraph(
                f"<b>{period_name} — {team.get('team_name', '-')}</b>",
                styles["SmallText"],
            ))
            story.append(Spacer(1, 2 * mm))

            player_rows = []

            for player in players:
                player_rows.append([
                    player.get("player_name", "-"),
                    player.get("appearances", 0),
                    player.get("starts", 0),
                    player.get("substitute_appearances", 0),
                    player.get("minutes", 0),
                    player.get("average_minutes_per_appearance", 0),
                    player.get("goals", 0),
                    player.get("assists", 0),
                    player.get("pre_assists", 0),
                    player.get("goal_contributions", 0),
                    player.get("shots", 0),
                    player.get("shots_on_target", 0),
                ])

            player_count += len(player_rows)

            story.append(make_table(
                player_headers,
                player_rows,
                [
                    39 * mm, 12 * mm, 12 * mm, 15 * mm,
                    15 * mm, 16 * mm, 12 * mm, 13 * mm,
                    17 * mm, 19 * mm, 12 * mm, 15 * mm,
                ],
            ))

            story.append(Spacer(1, 4 * mm))

    if not player_count:
        story.append(Paragraph(
            "No individual player performance data available.",
            styles["SmallText"],
        ))

    doc.build(
        story,
        onFirstPage=add_page_number,
        onLaterPages=add_page_number,
    )

    buffer.seek(0)

    filename = f"performance_analysis_{run.id}.pdf"

    response = HttpResponse(
        buffer.getvalue(),
        content_type="application/pdf",
    )
    response["Content-Disposition"] = (
        f'attachment; filename="{filename}"'
    )

    return response
