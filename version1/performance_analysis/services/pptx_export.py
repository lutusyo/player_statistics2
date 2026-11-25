
from io import BytesIO

from django.http import HttpResponse

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.dml import MSO_THEME_COLOR


NAVY = RGBColor(23, 54, 93)
BLUE = RGBColor(68, 114, 196)
LIGHT_BLUE = RGBColor(217, 234, 247)
WHITE = RGBColor(255, 255, 255)
DARK = RGBColor(45, 45, 45)
GREY = RGBColor(110, 110, 110)
LIGHT_GREY = RGBColor(243, 245, 247)
GREEN = RGBColor(39, 128, 75)
RED = RGBColor(190, 55, 55)


def add_background(slide, color=WHITE):
    fill = slide.background.fill
    fill.solid()
    fill.fore_color.rgb = color


def add_text(slide, text, x, y, w, h, size=16,
             color=DARK, bold=False, align=PP_ALIGN.LEFT):
    box = slide.shapes.add_textbox(
        Inches(x), Inches(y), Inches(w), Inches(h)
    )

    frame = box.text_frame
    frame.clear()
    frame.word_wrap = True
    frame.margin_left = Inches(0.05)
    frame.margin_right = Inches(0.05)

    paragraph = frame.paragraphs[0]
    paragraph.alignment = align

    run = paragraph.add_run()
    run.text = str(text if text is not None else "-")
    run.font.name = "Arial"
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color

    return box


def add_header(slide, title, subtitle=None):
    shape = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE,
        0, 0,
        Inches(13.333), Inches(0.85)
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = NAVY
    shape.line.fill.background()

    add_text(
        slide, title,
        0.55, 0.15, 12.2, 0.35,
        size=22, color=WHITE, bold=True
    )

    if subtitle:
        add_text(
            slide, subtitle,
            0.58, 0.53, 12, 0.2,
            size=9, color=LIGHT_BLUE
        )


def add_footer(slide, page):
    add_text(
        slide,
        f"Football Performance Analysis  |  {page}",
        0.55, 7.18, 12.2, 0.2,
        size=8, color=GREY,
    )


def add_table(slide, headers, rows, x=0.55, y=1.35,
              w=12.2, row_height=0.38, font_size=9):
    if not headers:
        return

    row_count = max(len(rows), 1) + 1
    table = slide.shapes.add_table(
        row_count,
        len(headers),
        Inches(x), Inches(y),
        Inches(w), Inches(row_height * row_count),
    ).table

    table_width = w / len(headers)

    for column in table.columns:
        column.width = Inches(table_width)

    for col, header in enumerate(headers):
        cell = table.cell(0, col)
        cell.text = str(header)
        cell.fill.solid()
        cell.fill.fore_color.rgb = NAVY
        cell.vertical_anchor = MSO_ANCHOR.MIDDLE

        for paragraph in cell.text_frame.paragraphs:
            paragraph.alignment = PP_ALIGN.CENTER
            for run in paragraph.runs:
                run.font.name = "Arial"
                run.font.size = Pt(font_size)
                run.font.bold = True
                run.font.color.rgb = WHITE

    for row_index, row in enumerate(rows, start=1):
        for col_index, value in enumerate(row):
            cell = table.cell(row_index, col_index)
            cell.text = str(value if value is not None else "-")
            cell.fill.solid()
            cell.fill.fore_color.rgb = (
                WHITE if row_index % 2 else LIGHT_GREY
            )
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE

            for paragraph in cell.text_frame.paragraphs:
                paragraph.alignment = PP_ALIGN.CENTER
                for run in paragraph.runs:
                    run.font.name = "Arial"
                    run.font.size = Pt(font_size)
                    run.font.color.rgb = DARK

    return table


def add_section_title(slide, title, y=1.1):
    add_text(
        slide, title,
        0.6, y, 12, 0.35,
        size=17, color=NAVY, bold=True
    )


def add_metric_card(slide, x, y, title, value, color=BLUE):
    shape = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE,
        Inches(x), Inches(y),
        Inches(2.8), Inches(1.15),
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = LIGHT_BLUE
    shape.line.color.rgb = LIGHT_BLUE

    add_text(
        slide, title,
        x + 0.12, y + 0.15, 2.55, 0.25,
        size=10, color=GREY, bold=True,
        align=PP_ALIGN.CENTER,
    )

    add_text(
        slide, value,
        x + 0.12, y + 0.48, 2.55, 0.42,
        size=22, color=color, bold=True,
        align=PP_ALIGN.CENTER,
    )


def add_empty_message(slide, message, y=2.0):
    add_text(
        slide, message,
        0.8, y, 11.7, 0.6,
        size=13, color=GREY,
        align=PP_ALIGN.CENTER,
    )


def export_analysis_pptx(run):
    report = run.results_snapshot or {}

    analysis = report.get("analysis", {})
    periods = report.get("periods", [])
    teams = report.get("teams", [])
    results = report.get("results", [])
    comparisons = report.get("comparisons", [])
    insights = report.get("insights", [])

    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    blank = prs.slide_layouts[6]

    # 1. COVER SLIDE
    slide = prs.slides.add_slide(blank)
    add_background(slide, NAVY)

    add_text(
        slide, "AZAM FC",
        0.8, 1.15, 11.7, 0.5,
        size=20, color=LIGHT_BLUE, bold=True,
        align=PP_ALIGN.CENTER,
    )

    add_text(
        slide, "FOOTBALL PERFORMANCE",
        0.8, 2.2, 11.7, 0.65,
        size=30, color=WHITE, bold=True,
        align=PP_ALIGN.CENTER,
    )

    add_text(
        slide, "ANALYSIS REPORT",
        0.8, 2.95, 11.7, 0.55,
        size=26, color=LIGHT_BLUE, bold=True,
        align=PP_ALIGN.CENTER,
    )

    add_text(
        slide,
        analysis.get("name", run.analysis.name),
        1.0, 4.05, 11.3, 0.55,
        size=19, color=WHITE,
        align=PP_ALIGN.CENTER,
    )

    generated = (
        run.generated_at.strftime("%d %B %Y")
        if run.generated_at else "-"
    )

    add_text(
        slide, f"Generated: {generated}",
        1.0, 5.05, 11.3, 0.3,
        size=12, color=LIGHT_BLUE,
        align=PP_ALIGN.CENTER,
    )

    # 2. EXECUTIVE SUMMARY
    slide = prs.slides.add_slide(blank)
    add_background(slide)
    add_header(slide, "Executive Summary", analysis.get("name"))

    total_played = sum(item.get("played", 0) for item in results)
    total_wins = sum(item.get("won", 0) for item in results)
    total_goals = sum(item.get("goals_for", 0) for item in results)
    total_points = sum(item.get("points", 0) for item in results)

    metrics = [
        ("Teams", len(teams), BLUE),
        ("Periods", len(periods), BLUE),
        ("Match Entries", total_played, BLUE),
        ("Wins", total_wins, GREEN),
        ("Goals Scored", total_goals, BLUE),
        ("Points", total_points, BLUE),
    ]

    for index, (title, value, color) in enumerate(metrics):
        x = 0.65 + (index % 3) * 4.2
        y = 1.45 + (index // 3) * 1.65
        add_metric_card(slide, x, y, title, str(value), color)

    add_text(
        slide, "Selected Teams",
        0.7, 5.15, 3, 0.3,
        size=13, color=NAVY, bold=True,
    )

    add_text(
        slide,
        ", ".join(team.get("name", "") for team in teams) or "No teams selected",
        0.7, 5.55, 11.8, 0.55,
        size=12, color=DARK,
    )

    add_footer(slide, 2)

    # 3. TEAM PERFORMANCE
    slide = prs.slides.add_slide(blank)
    add_background(slide)
    add_header(slide, "Team Performance")

    performance_rows = [
        [
            item.get("period_name"),
            item.get("team_name"),
            item.get("played", 0),
            item.get("won", 0),
            item.get("drawn", 0),
            item.get("lost", 0),
            item.get("goals_for", 0),
            item.get("goals_against", 0),
            item.get("goal_difference", 0),
            item.get("points", 0),
            f"{item.get('win_percentage', 0)}%",
        ]
        for item in results
    ]

    if performance_rows:
        add_table(
            slide,
            ["Period", "Team", "P", "W", "D", "L",
             "GF", "GA", "GD", "Pts", "Win %"],
            performance_rows,
            y=1.4,
            row_height=0.43,
            font_size=9,
        )
    else:
        add_empty_message(slide, "No team performance data available.")

    add_footer(slide, 3)

    # 4. SHOOTING AND PASSING
    slide = prs.slides.add_slide(blank)
    add_background(slide)
    add_header(slide, "Shooting and Passing Performance")

    technical_rows = [
        [
            item.get("period_name"),
            item.get("team_name"),
            item.get("shots", 0),
            item.get("shots_on_target", 0),
            f"{item.get('shooting_accuracy', 0)}%",
            item.get("passes_attempted", 0),
            item.get("passes_completed", 0),
            f"{item.get('pass_accuracy', 0)}%",
        ]
        for item in results
    ]

    if technical_rows:
        add_table(
            slide,
            ["Period", "Team", "Shots", "On Target",
             "Shooting %", "Passes", "Completed", "Passing %"],
            technical_rows,
            y=1.5,
            row_height=0.43,
            font_size=9,
        )
    else:
        add_empty_message(slide, "No shooting or passing data available.")

    add_footer(slide, 4)

    # 5. PERIOD COMPARISON
    slide = prs.slides.add_slide(blank)
    add_background(slide)
    add_header(slide, "Period Comparison")

    comparison_rows = []

    for item in comparisons:
        changes = item.get("changes") or {}

        for metric, change in changes.items():
            if change is None:
                continue

            comparison_rows.append([
                item.get("team_name"),
                item.get("period_name"),
                metric.replace("_", " ").title(),
                change,
            ])

    # Split long comparisons over multiple slides.
    chunks = [
        comparison_rows[i:i + 10]
        for i in range(0, len(comparison_rows), 10)
    ]

    if chunks:
        for index, chunk in enumerate(chunks):
            if index:
                slide = prs.slides.add_slide(blank)
                add_background(slide)
                add_header(slide, "Period Comparison (Continued)")

            add_table(
                slide,
                ["Team", "Period", "Metric", "Change"],
                chunk,
                y=1.45,
                row_height=0.43,
                font_size=9,
            )
            add_footer(slide, len(prs.slides))
    else:
        add_empty_message(slide, "No period comparisons available.")
        add_footer(slide, len(prs.slides))

    # 6. PERFORMANCE INSIGHTS
    slide = prs.slides.add_slide(blank)
    add_background(slide)
    add_header(slide, "Performance Insights")

    insight_rows = []

    for item in insights:
        for insight in item.get("insights", []):
            insight_rows.append([
                item.get("team_name"),
                item.get("period_name"),
                insight.get("category"),
                insight.get("metric"),
                insight.get("status"),
                insight.get("message"),
            ])

    insight_chunks = [
        insight_rows[i:i + 7]
        for i in range(0, len(insight_rows), 7)
    ]

    if insight_chunks:
        for index, chunk in enumerate(insight_chunks):
            if index:
                slide = prs.slides.add_slide(blank)
                add_background(slide)
                add_header(slide, "Performance Insights (Continued)")

            add_table(
                slide,
                ["Team", "Period", "Category", "Metric", "Status", "Observation"],
                chunk,
                y=1.35,
                row_height=0.65,
                font_size=8,
            )
            add_footer(slide, len(prs.slides))
    else:
        add_empty_message(slide, "No performance insights available.")
        add_footer(slide, len(prs.slides))

    # 7. PLAYER MINUTES
    player_rows = []

    for item in results:
        for player in item.get("player_details", []):
            player_rows.append([
                item.get("period_name"),
                item.get("team_name"),
                player.get("player_name"),
                player.get("appearances", 0),
                player.get("minutes", 0),
            ])

    player_chunks = [
        player_rows[i:i + 10]
        for i in range(0, len(player_rows), 10)
    ]

    if player_chunks:
        for index, chunk in enumerate(player_chunks):
            slide = prs.slides.add_slide(blank)
            add_background(slide)
            title = "Player Minutes" if index == 0 else "Player Minutes (Continued)"
            add_header(slide, title)

            add_table(
                slide,
                ["Period", "Team", "Player", "Appearances", "Minutes"],
                chunk,
                y=1.45,
                row_height=0.43,
                font_size=9,
            )
            add_footer(slide, len(prs.slides))
    else:
        slide = prs.slides.add_slide(blank)
        add_background(slide)
        add_header(slide, "Player Minutes")
        add_empty_message(slide, "No player appearance data available.")
        add_footer(slide, len(prs.slides))








    # 8. INDIVIDUAL PLAYER PERFORMANCE
    player_analysis = report.get("player_analysis", [])

    player_slide_count = 0

    for period in player_analysis:
        period_name = period.get("period_name", "-")

        for team in period.get("teams", []):
            team_name = team.get("team_name", "-")
            players = team.get("players", [])

            if not players:
                continue

            # Split players into groups of 8 per slide.
            player_chunks = [
                players[i:i + 8]
                for i in range(0, len(players), 8)
            ]

            for chunk_index, chunk in enumerate(player_chunks):
                slide = prs.slides.add_slide(blank)
                add_background(slide)

                player_slide_count += 1

                title = (
                    "Individual Player Performance"
                    if chunk_index == 0
                    else "Individual Player Performance (Continued)"
                )

                add_header(
                    slide,
                    title,
                    f"{period_name} | {team_name}",
                )

                player_rows = []

                for player in chunk:
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

                add_table(
                    slide,
                    [
                        "Player",
                        "Apps",
                        "Starts",
                        "Sub Apps",
                        "Minutes",
                        "Avg Min",
                        "Goals",
                        "Assists",
                        "Pre-Assists",
                        "Contributions",
                        "Shots",
                        "On Target",
                    ],
                    player_rows,
                    x=0.45,
                    y=1.5,
                    w=12.4,
                    row_height=0.48,
                    font_size=7,
                )

                add_footer(slide, len(prs.slides))

    if player_slide_count == 0:
        slide = prs.slides.add_slide(blank)
        add_background(slide)
        add_header(slide, "Individual Player Performance")

        add_empty_message(
            slide,
            "No individual player performance data available.",
        )

        add_footer(slide, len(prs.slides))







    # 9. DETAILED TECHNICAL ANALYSIS
    technical_analysis = report.get("technical_analysis", [])

    def add_technical_slides(
        title, period_name, team_name,
        headers, rows, chunk_size=8, font_size=8,
    ):
        subtitle = f"{period_name} | {team_name}"

        chunks = [
            rows[i:i + chunk_size]
            for i in range(0, len(rows), chunk_size)
        ]

        if not chunks:
            chunks = [[]]

        for index, chunk in enumerate(chunks):
            slide = prs.slides.add_slide(blank)
            add_background(slide)

            slide_title = (
                title if index == 0
                else f"{title} (Continued)"
            )

            add_header(slide, slide_title, subtitle)

            if chunk:
                add_table(
                    slide,
                    headers,
                    chunk,
                    x=0.45,
                    y=1.5,
                    w=12.4,
                    row_height=0.45,
                    font_size=font_size,
                )
            else:
                add_empty_message(
                    slide,
                    f"No {title.lower()} data available.",
                )

            add_footer(slide, len(prs.slides))

    for period in technical_analysis:
        period_name = period.get("period_name", "-")

        for team in period.get("teams", []):
            team_name = team.get("team_name", "-")

            shooting = team.get("shooting", {})
            goalkeeping = team.get("goalkeeping", {})
            discipline = team.get("discipline", {})

            # SHOOTING ANALYSIS
            shooting_rows = [[
                shooting.get("shots", 0),
                shooting.get("shots_on_target", 0),
                shooting.get("goals", 0),
                shooting.get("saved", 0),
                shooting.get("blocked", 0),
                shooting.get("off_target", 0),
                shooting.get("player_errors", 0),
                shooting.get("shooting_accuracy", 0),
                shooting.get("conversion_rate", 0),
            ]]

            add_technical_slides(
                "Shooting Analysis",
                period_name,
                team_name,
                [
                    "Shots", "On Target", "Goals",
                    "Saved", "Blocked", "Off Target",
                    "Player Errors", "Accuracy %",
                    "Conversion %",
                ],
                shooting_rows,
                chunk_size=8,
                font_size=8,
            )

            # SHOT BREAKDOWNS
            breakdown_rows = []

            for category, items in [
                ("Outcome", shooting.get("outcomes", [])),
                ("Delivery Type", shooting.get("delivery_types", [])),
                ("Body Part", shooting.get("body_parts", [])),
                ("Shot Location", shooting.get("locations", [])),
            ]:
                for item in items:
                    breakdown_rows.append([
                        category,
                        item.get("name", "-"),
                        item.get("count", 0),
                    ])

            add_technical_slides(
                "Shot Breakdowns",
                period_name,
                team_name,
                ["Breakdown Type", "Category", "Count"],
                breakdown_rows,
                chunk_size=12,
                font_size=9,
            )

            # GOALKEEPER ANALYSIS
            goalkeeper_rows = []

            for player in goalkeeping.get("goalkeepers", []):
                goalkeeper_rows.append([
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

            add_technical_slides(
                "Goalkeeper Performance",
                period_name,
                team_name,
                [
                    "Goalkeeper", "Apps", "Starts", "Sub Apps",
                    "Minutes", "Avg Min", "Clean Sheets",
                    "Clean Sheet %", "Team Goals Conceded",
                    "Missing Entry", "Invalid Times",
                ],
                goalkeeper_rows,
                chunk_size=7,
                font_size=7,
            )

            # DISCIPLINE ANALYSIS
            discipline_rows = [[
                discipline.get("fouls_committed", 0),
                discipline.get("fouls_won", 0),
                discipline.get("no_card_fouls", 0),
                discipline.get("yellow_cards", 0),
                discipline.get("red_cards", 0),
                discipline.get("total_cards", 0),
            ]]

            add_technical_slides(
                "Discipline Analysis",
                period_name,
                team_name,
                [
                    "Fouls Committed", "Fouls Won",
                    "No Card Fouls", "Yellow Cards",
                    "Red Cards", "Total Cards",
                ],
                discipline_rows,
                chunk_size=8,
                font_size=9,
            )

            # GOALKEEPER DATA NOTE
            slide = prs.slides.add_slide(blank)
            add_background(slide)
            add_header(
                slide,
                "Goalkeeper Data Note",
                f"{period_name} | {team_name}",
            )

            add_text(
                slide,
                "Team Goals Conceded represents the team's total "
                "goals conceded in matches where the goalkeeper "
                "appeared. It is not individually attributed when "
                "multiple goalkeepers played in the same match.",
                0.9, 2.0, 11.5, 1.2,
                size=17, color=DARK,
                align=PP_ALIGN.CENTER,
            )

            add_footer(slide, len(prs.slides))







    # SAVE PRESENTATION
    buffer = BytesIO()
    prs.save(buffer)
    buffer.seek(0)

    filename = f"performance_analysis_{run.id}.pptx"

    response = HttpResponse(
        buffer.getvalue(),
        content_type=(
            "application/vnd.openxmlformats-officedocument."
            "presentationml.presentation"
        ),
    )
    response["Content-Disposition"] = (
        f'attachment; filename="{filename}"'
    )

    return response
