
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


def get_team_label(item):
    team_name = item.get("team_name", "-")
    age_group = item.get("age_group")

    return (
        f"{team_name} ({age_group})"
        if age_group else team_name
    )


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

def make_table(headers, rows, widths=None, row_colors=None):
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

    table_style = [
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
        ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#D5DDE5")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, LIGHT_GREY]),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]

    for row_number, color in enumerate(row_colors or [], start=1):
        if color:
            table_style.append(
                ("BACKGROUND", (0, row_number), (-1, row_number), color)
            )

    table.setStyle(TableStyle(table_style))

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
    technical_analysis = report.get("technical_analysis", [])

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
            get_team_label(item),
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




    # MATCH RESULTS
    story.append(Paragraph(
        "Team Match Results",
        styles["SectionHeading"],
    ))

    result_rows = []
    result_colors = []

    result_color_map = {
        "success": colors.HexColor("#C6EFCE"),
        "danger": colors.HexColor("#FFC7CE"),
        "warning": colors.HexColor("#FFEB9C"),
    }

    for item in results:
        team_label = get_team_label(item)

        for match in item.get("match_results", []):
            result_rows.append([
                item.get("period_name", "-"),
                match.get("date", "-"),
                team_label,
                match.get("home_team", "-"),
                (
                    f'{match.get("home_score", 0)} - '
                    f'{match.get("away_score", 0)}'
                ),
                match.get("result", "-"),
                match.get("away_team", "-"),
            ])

            result_colors.append(
                result_color_map.get(
                    match.get("result_color"),
                    WHITE,
                )
            )

    if result_rows:
        story.append(make_table(
            [
                "Period",
                "Date",
                "Team",
                "Home Team",
                "Score",
                "Result",
                "Away Team",
            ],
            result_rows,
            [
                35 * mm,
                22 * mm,
                35 * mm,
                43 * mm,
                18 * mm,
                20 * mm,
                43 * mm,
            ],
            row_colors=result_colors,
        ))
    else:
        story.append(Paragraph(
            "No match results available.",
            styles["SmallText"],
        ))

    story.append(Spacer(1, 5 * mm))




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





    # DETAILED TECHNICAL ANALYSIS
    story.append(PageBreak())
    story.append(Paragraph(
        "Detailed Technical Analysis",
        styles["SectionHeading"],
    ))

    shooting_rows = []
    breakdown_rows = []
    goalkeeper_rows = []
    discipline_rows = []

    for period in technical_analysis:
        period_name = period.get("period_name", "-")

        for team in period.get("teams", []):
            team_name = team.get("team_name", "-")

            shooting = team.get("shooting", {})
            goalkeeping = team.get("goalkeeping", {})
            discipline = team.get("discipline", {})

            # SHOOTING
            shooting_rows.append([
                period_name,
                team_name,
                team.get("matches_played", 0),
                shooting.get("shots", 0),
                shooting.get("shots_on_target", 0),
                shooting.get("goals", 0),
                shooting.get("saved", 0),
                shooting.get("blocked", 0),
                shooting.get("off_target", 0),
                shooting.get("player_errors", 0),
                shooting.get("shooting_accuracy", 0),
                shooting.get("conversion_rate", 0),
            ])

            # SHOT BREAKDOWNS
            for category, items in [
                ("Outcome", shooting.get("outcomes", [])),
                ("Delivery Type", shooting.get("delivery_types", [])),
                ("Body Part", shooting.get("body_parts", [])),
                ("Shot Location", shooting.get("locations", [])),
            ]:
                for item in items:
                    breakdown_rows.append([
                        period_name,
                        team_name,
                        category,
                        item.get("name", "-"),
                        item.get("count", 0),
                    ])

            # GOALKEEPER PERFORMANCE
            for player in goalkeeping.get("goalkeepers", []):
                goalkeeper_rows.append([
                    period_name,
                    team_name,
                    player.get("player_name", "-"),
                    player.get("matches_played", 0),
                    player.get("starts", 0),
                    player.get("substitute_appearances", 0),
                    player.get("minutes", 0),
                    player.get("average_minutes", 0),
                    player.get("clean_sheets", 0),
                    player.get("clean_sheet_percentage", 0),
                    player.get("team_goals_conceded", 0),
                    player.get("missing_entry_time", 0),
                    player.get("invalid_time_intervals", 0),
                ])

            # DISCIPLINE
            discipline_rows.append([
                period_name,
                team_name,
                team.get("matches_played", 0),
                discipline.get("fouls_committed", 0),
                discipline.get("fouls_won", 0),
                discipline.get("no_card_fouls", 0),
                discipline.get("yellow_cards", 0),
                discipline.get("red_cards", 0),
                discipline.get("total_cards", 0),
            ])

    # SHOOTING ANALYSIS
    story.append(Paragraph("Shooting Analysis", styles["SectionHeading"]))

    if shooting_rows:
        story.append(make_table(
            [
                "Period", "Team", "Matches", "Shots",
                "On Target", "Goals", "Saved", "Blocked",
                "Off Target", "Player Errors",
                "Accuracy %", "Conversion %",
            ],
            shooting_rows,
            [
                25 * mm, 35 * mm, 18 * mm, 14 * mm,
                18 * mm, 14 * mm, 14 * mm, 14 * mm,
                17 * mm, 18 * mm, 23 * mm, 23 * mm,
            ],
        ))
    else:
        story.append(Paragraph(
            "No shooting analysis available.",
            styles["SmallText"],
        ))

    story.append(Spacer(1, 4 * mm))

    # SHOT BREAKDOWNS
    story.append(Paragraph("Shot Breakdowns", styles["SectionHeading"]))

    if breakdown_rows:
        story.append(make_table(
            ["Period", "Team", "Breakdown Type", "Category", "Count"],
            breakdown_rows,
            [35 * mm, 45 * mm, 45 * mm, 100 * mm, 20 * mm],
        ))
    else:
        story.append(Paragraph(
            "No shot breakdown data available.",
            styles["SmallText"],
        ))

    story.append(Spacer(1, 4 * mm))

    # GOALKEEPER ANALYSIS
    story.append(Paragraph(
        "Goalkeeper Performance",
        styles["SectionHeading"],
    ))

    if goalkeeper_rows:
        story.append(make_table(
            [
                "Period", "Team", "Goalkeeper",
                "Apps", "Starts", "Sub Apps",
                "Minutes", "Avg Min", "Clean Sheets",
                "Clean Sheet %", "Team Goals Conceded",
                "Missing Entry", "Invalid Times",
            ],
            goalkeeper_rows,
            [
                22 * mm, 27 * mm, 33 * mm,
                12 * mm, 12 * mm, 17 * mm,
                15 * mm, 15 * mm, 19 * mm,
                19 * mm, 28 * mm, 18 * mm, 18 * mm,
            ],
        ))

        story.append(Spacer(1, 2 * mm))
        story.append(Paragraph(
            "<b>Note:</b> Team Goals Conceded represents the team's "
            "total goals conceded in matches where the goalkeeper "
            "appeared. It is not individually attributed when multiple "
            "goalkeepers played in the same match.",
            styles["SmallText"],
        ))
    else:
        story.append(Paragraph(
            "No goalkeeper data available.",
            styles["SmallText"],
        ))

    story.append(Spacer(1, 4 * mm))

    # DISCIPLINE ANALYSIS
    story.append(Paragraph("Discipline Analysis", styles["SectionHeading"]))

    if discipline_rows:
        story.append(make_table(
            [
                "Period", "Team", "Matches",
                "Fouls Committed", "Fouls Won",
                "No Card", "Yellow Cards",
                "Red Cards", "Total Cards",
            ],
            discipline_rows,
            [
                27 * mm, 35 * mm, 20 * mm,
                35 * mm, 25 * mm, 25 * mm,
                25 * mm, 22 * mm, 25 * mm,
            ],
        ))
    else:
        story.append(Paragraph(
            "No discipline data available.",
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
