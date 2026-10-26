from collections import defaultdict
from datetime import date, timedelta
from io import BytesIO
from xml.sax.saxutils import escape

from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import render

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    Image as PDFImage,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.platypus.tableofcontents import TableOfContents

from version1.teams_app.models import AgeGroup, Team
from apps.individual_data.models.data_collection import (
    TrainingSession,
    PlayerParticipation,
    PlayerIntervention,
    PlayerInterventionCoachingPoint,
)


class WeeklyReportDocument(SimpleDocTemplate):
    """PDF document that creates clickable bookmarks and a table of contents."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._toc_counter = 0

    def beforeDocument(self):
        # multiBuild() runs the document several times. Reset this counter
        # on every pass so the same headings get the same bookmark keys.
        self._toc_counter = 0

    def afterFlowable(self, flowable):
        if not isinstance(flowable, Paragraph):
            return

        style_name = flowable.style.name
        if style_name not in ("TOCLevel1", "TOCLevel2"):
            return

        level = 0 if style_name == "TOCLevel1" else 1
        title = flowable.getPlainText()
        self._toc_counter += 1
        key = f"weekly-report-heading-{self._toc_counter}"

        self.canv.bookmarkPage(key)
        try:
            self.canv.addOutlineEntry(title, key, level=level, closed=False)
        except (ValueError, KeyError):
            # Keep PDF generation working even if a PDF viewer rejects an outline level.
            pass

        self.notify("TOCEntry", (level, title, self.page, key))


def _report_dates(request):
    """Return default or requested report dates and whether they are valid."""
    today = date.today()
    default_start = today - timedelta(days=today.weekday())
    default_end = default_start + timedelta(days=6)

    start_value = request.GET.get("week_start", default_start.isoformat())
    end_value = request.GET.get("week_end", default_end.isoformat())

    try:
        week_start = date.fromisoformat(start_value)
        week_end = date.fromisoformat(end_value)
        if week_end < week_start:
            raise ValueError("End date precedes start date")
        return week_start, week_end, True
    except (TypeError, ValueError):
        return default_start, default_end, False


def _report_queryset(age_group, week_start, week_end, selected_team=None):
    """Build the shared session queryset for one age group or all groups."""
    sessions = TrainingSession.objects.filter(
        date__range=(week_start, week_end),
    )

    if age_group is not None:
        sessions = sessions.filter(age_group=age_group)

    if selected_team:
        sessions = sessions.filter(team=selected_team)

    return (
        sessions.select_related("age_group", "team", "coach")
        .prefetch_related(
            "session_topics__topic",
            "session_topics__objective",
            "player_participations__player",
            "player_participations__interventions__session_topic__topic",
            "player_participations__interventions__session_topic__objective",
            "player_participations__interventions__coaching_points__coaching_point",
        )
        .order_by("date", "pk")
    )


def _report_statistics(sessions):
    participations = PlayerParticipation.objects.filter(session__in=sessions)
    interventions = PlayerIntervention.objects.filter(
        player_participation__session__in=sessions
    )
    coaching_selections = PlayerInterventionCoachingPoint.objects.filter(
        intervention__in=interventions
    )

    statistics = {
        "sessions": sessions.count(),
        "players": participations.values("player_id").distinct().count(),
        "interventions": interventions.count(),
        "coaching_points": coaching_selections.count(),
        "achieved": coaching_selections.filter(achieved=True).count(),
        "player_minutes": (
            participations.aggregate(total=Sum("minutes"))["total"] or 0
        ),
    }
    return participations, interventions, coaching_selections, statistics


def weekly_report(request):
    age_groups = AgeGroup.objects.all().order_by("name")
    age_group_id = request.GET.get("age_group", "").strip()
    selected_age_group = age_groups.filter(pk=age_group_id).first() if age_group_id else None
    all_groups_selected = not age_group_id

    week_start, week_end, dates_valid = _report_dates(request)
    teams = (
        Team.objects.filter(age_group=selected_age_group).order_by("name")
        if selected_age_group
        else Team.objects.all().order_by("name")
    )

    team_id = request.GET.get("team", "").strip()
    selected_team = teams.filter(pk=team_id).first() if team_id else None

    if age_group_id and not selected_age_group:
        sessions = TrainingSession.objects.none()
    else:
        sessions = _report_queryset(
            selected_age_group, week_start, week_end, selected_team
        )
    participations, interventions, coaching_selections, statistics = (
        _report_statistics(sessions)
    )

    context = {
        "age_groups": age_groups,
        "selected_age_group": selected_age_group,
        "all_groups_selected": all_groups_selected,
        "teams": teams,
        "selected_team": selected_team,
        "week_start": week_start,
        "week_end": week_end,
        "dates_valid": dates_valid,
        "sessions": sessions,
        "statistics": statistics,
    }
    return render(request, "individual_data/weekly_report.html", context)


def _safe(value):
    """Escape model text before inserting it into a ReportLab Paragraph."""
    if value is None or value == "":
        return "—"
    text = str(value).replace("\r\n", "\n").replace("\r", "\n")
    return escape(text).replace("\n", "<br/>")


def _team_logo(team, max_width=24 * mm, max_height=24 * mm):
    """Return a PDF image for a local team logo, or None when unavailable."""
    if not team or not team.logo:
        return None

    try:
        logo_path = team.logo.path
        image = PDFImage(logo_path)
        image_width, image_height = image.imageWidth, image.imageHeight
        if not image_width or not image_height:
            return None
        scale = min(max_width / image_width, max_height / image_height)
        image.drawWidth = image_width * scale
        image.drawHeight = image_height * scale
        image.hAlign = "LEFT"
        return image
    except (AttributeError, OSError, ValueError, NotImplementedError):
        # Storage backends without a local .path need a storage-specific solution.
        return None


def weekly_report_pdf(request):
    age_groups = AgeGroup.objects.all().order_by("name")
    age_group_id = request.GET.get("age_group", "").strip()
    selected_age_group = age_groups.filter(pk=age_group_id).first() if age_group_id else None

    week_start, week_end, dates_valid = _report_dates(request)
    if not dates_valid:
        return HttpResponse(
            "Invalid reporting dates. Please select a valid date range.",
            status=400,
        )

    if age_group_id and not selected_age_group:
        return HttpResponse("Please select a valid age group.", status=400)

    teams = (
        Team.objects.filter(age_group=selected_age_group).order_by("name")
        if selected_age_group
        else Team.objects.all().order_by("name")
    )
    team_id = request.GET.get("team", "").strip()
    selected_team = teams.filter(pk=team_id).first() if team_id else None

    if team_id and not selected_team:
        return HttpResponse(
            "The selected team does not match the selected age-group filter.",
            status=400,
        )

    sessions = _report_queryset(
        selected_age_group, week_start, week_end, selected_team
    )
    participations, interventions, coaching_selections, statistics = (
        _report_statistics(sessions)
    )

    # Aggregate every player's participation minutes across all matching sessions.
    player_totals = defaultdict(
        lambda: {"name": "", "minutes": 0, "teams": set()}
    )
    for participation in participations.select_related(
        "player", "session__team"
    ):
        player = participation.player
        entry = player_totals[player.pk]
        entry["name"] = getattr(player, "full_name", None) or str(player)
        entry["minutes"] += participation.minutes or 0
        if participation.session.team:
            entry["teams"].add(participation.session.team.name)

    ordered_players = sorted(
        player_totals.values(),
        key=lambda item: item["name"].casefold(),
    )

    buffer = BytesIO()
    doc = WeeklyReportDocument(
        buffer,
        pagesize=landscape(A4),
        rightMargin=12 * mm,
        leftMargin=12 * mm,
        topMargin=17 * mm,
        bottomMargin=15 * mm,
        title="Weekly Individual Training Performance Report",
        author="Individual Training Department",
    )

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name="ReportTitle",
        parent=styles["Title"],
        fontSize=20,
        leading=24,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#17365D"),
        spaceAfter=10,
    ))
    styles.add(ParagraphStyle(
        name="TOCTitle",
        parent=styles["Heading1"],
        fontSize=16,
        leading=20,
        textColor=colors.HexColor("#17365D"),
        spaceAfter=12,
    ))
    styles.add(ParagraphStyle(
        name="TOCLevel1",
        parent=styles["Heading1"],
        fontSize=12,
        leading=15,
        textColor=colors.HexColor("#17365D"),
        spaceBefore=10,
        spaceAfter=5,
        keepWithNext=True,
    ))
    styles.add(ParagraphStyle(
        name="TOCLevel2",
        parent=styles["Heading2"],
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#285A84"),
        spaceBefore=6,
        spaceAfter=3,
        keepWithNext=True,
    ))
    styles.add(ParagraphStyle(
        name="SmallCell",
        parent=styles["BodyText"],
        fontSize=7,
        leading=9,
        spaceAfter=1,
        wordWrap="CJK",
    ))
    styles.add(ParagraphStyle(
        name="SmallHeader",
        parent=styles["BodyText"],
        fontSize=7,
        leading=9,
        textColor=colors.white,
    ))
    styles.add(ParagraphStyle(
        name="CoverText",
        parent=styles["Normal"],
        fontSize=10,
        leading=15,
        alignment=TA_CENTER,
    ))

    story = []

    def cell(value):
        if isinstance(value, Paragraph):
            return value
        return Paragraph(_safe(value), styles["SmallCell"])

    def heading(value, level=1):
        style = styles["TOCLevel1"] if level == 1 else styles["TOCLevel2"]
        story.append(Paragraph(_safe(value), style))

    def make_table(rows, widths, repeat_rows=1):
        table = Table(
            rows,
            colWidths=widths,
            repeatRows=repeat_rows,
            hAlign="LEFT",
        )
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#17365D")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#D0D7DE")),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 4),
            ("RIGHTPADDING", (0, 0), (-1, -1), 4),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1),
             [colors.white, colors.HexColor("#F3F6FA")]),
        ]))
        story.append(table)
        story.append(Spacer(1, 4 * mm))

    # Cover page: use the selected team's logo where available.
    logo = _team_logo(selected_team)
    if logo:
        logo_table = Table([[logo]], colWidths=[doc.width])
        logo_table.setStyle(TableStyle([
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ("TOPPADDING", (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ]))
        story.append(logo_table)

    story.append(Spacer(1, 10 * mm))
    story.append(Paragraph(
        "WEEKLY INDIVIDUAL TRAINING<br/>PERFORMANCE REPORT",
        styles["ReportTitle"],
    ))
    report_scope = selected_team.name if selected_team else "All Teams"
    age_group_scope = selected_age_group.name if selected_age_group else "All Age Groups"
    story.append(Paragraph(
        f"<b>Age Group:</b> {_safe(age_group_scope)}<br/>"
        f"<b>Team:</b> {_safe(report_scope)}<br/>"
        f"<b>Reporting Period:</b> {week_start.strftime('%d %b %Y')} "
        f"to {week_end.strftime('%d %b %Y')}<br/>"
        f"<b>Generated:</b> {date.today().strftime('%d %b %Y')}",
        styles["CoverText"],
    ))
    story.append(PageBreak())

    # Table of contents is populated over multiple build passes.
    story.append(Paragraph("TABLE OF CONTENTS", styles["TOCTitle"]))
    toc = TableOfContents()
    toc.levelStyles = [
        ParagraphStyle(
            name="TOCEntryLevel0",
            fontName="Helvetica-Bold",
            fontSize=9,
            leading=14,
            leftIndent=0,
            firstLineIndent=0,
            spaceBefore=4,
        ),
        ParagraphStyle(
            name="TOCEntryLevel1",
            fontName="Helvetica",
            fontSize=8,
            leading=11,
            leftIndent=16,
            firstLineIndent=0,
        ),
    ]
    toc.dotsMinLevel = 0
    story.append(toc)
    story.append(PageBreak())

    # 1. Summary.
    heading("1. REPORT SUMMARY")
    summary_rows = [[
        cell("Sessions"), cell("Players"), cell("Interventions"),
        cell("Coaching Points"), cell("Achieved"), cell("Player-Minutes"),
    ], [
        cell(statistics["sessions"]),
        cell(statistics["players"]),
        cell(statistics["interventions"]),
        cell(statistics["coaching_points"]),
        cell(statistics["achieved"]),
        cell(statistics["player_minutes"]),
    ]]
    make_table(
        summary_rows,
        [38 * mm, 32 * mm, 40 * mm, 42 * mm, 30 * mm, 40 * mm],
    )

    # 2. Teams included. For all-teams reports, list team names and logos.
    heading("2. REPORTING PERIOD AND TEAM COVERAGE")
    story.append(Paragraph(
        f"Age group: <b>{_safe(age_group_scope)}</b><br/>"
        f"Dates: <b>{week_start.strftime('%d %b %Y')} - "
        f"{week_end.strftime('%d %b %Y')}</b><br/>"
        f"Scope: <b>{_safe(report_scope)}</b>",
        styles["Normal"],
    ))
    story.append(Spacer(1, 3 * mm))

    if selected_team:
        coverage_teams = [selected_team]
    else:
        coverage_teams = list(
            Team.objects.filter(
                pk__in=sessions.exclude(team__isnull=True)
                .values_list("team_id", flat=True).distinct()
            ).order_by("name")
        )

    if coverage_teams:
        coverage_rows = [[cell("Logo"), cell("Team")]]
        for team in coverage_teams:
            team_logo = _team_logo(team, 12 * mm, 12 * mm)
            coverage_rows.append([
                team_logo if team_logo else cell("—"),
                cell(team.name),
            ])
        make_table(coverage_rows, [25 * mm, 200 * mm])
    else:
        story.append(Paragraph(
            "No teams have training sessions in this reporting period.",
            styles["Normal"],
        ))
        story.append(Spacer(1, 4 * mm))

    if not sessions.exists():
        story.append(Paragraph(
            "No training sessions were found for the selected age group, "
            "team, and reporting period.",
            styles["Normal"],
        ))

    # 3. Training overview.
    heading("3. TRAINING OVERVIEW")
    overview_rows = [[
        cell("Date"), cell("Age Group"), cell("Team"), cell("Training Type"),
        cell("Coach"), cell("Duration"),
    ]]
    for session in sessions:
        overview_rows.append([
            cell(session.date.strftime("%d %b %Y")),
            cell(session.age_group.name if session.age_group else "—"),
            cell(session.team.name if session.team else "—"),
            cell(session.get_training_type_display()),
            cell(session.coach if session.coach else "—"),
            cell(
                f"{session.duration_minutes} minutes"
                if session.duration_minutes else "—"
            ),
        ])
    if len(overview_rows) == 1:
        overview_rows.append([
            cell("—"), cell("—"), cell("No sessions"), cell("—"), cell("—"), cell("—")
        ])
    make_table(overview_rows, [27 * mm, 35 * mm, 45 * mm, 45 * mm, 50 * mm, 30 * mm])

    # 4. Aggregate minutes per player for the entire selected date range.
    heading("4. PLAYER PERFORMANCE — AGGREGATE MINUTES")
    story.append(Paragraph(
        "Each player's minutes are summed across all matching training "
        "sessions in the selected date range. In an all-teams report, a "
        "player is listed once, with their associated team names.",
        styles["Normal"],
    ))
    story.append(Spacer(1, 3 * mm))
    player_rows = [[
        cell("No."), cell("Player Name"), cell("Team(s)"), cell("Total Minutes")
    ]]
    for index, player in enumerate(ordered_players, start=1):
        player_rows.append([
            cell(index),
            cell(player["name"]),
            cell(", ".join(sorted(player["teams"])) or "—"),
            cell(player["minutes"]),
        ])
    if not ordered_players:
        player_rows.append([
            cell("—"), cell("No players recorded"), cell("—"), cell("0")
        ])
    player_rows.append([
        cell(""),
        cell("TOTAL PLAYER-MINUTES"),
        cell(""),
        cell(statistics["player_minutes"]),
    ])
    make_table(player_rows, [18 * mm, 95 * mm, 100 * mm, 40 * mm])

    # 5. Session topics and objectives.
    heading("5. TRAINING SESSIONS, TOPICS AND OBJECTIVES")
    for session in sessions:
        heading(
            f"{session.date.strftime('%d %b %Y')} — "
            f"{session.age_group.name if session.age_group else 'Age group not specified'} — "
            f"{session.team.name if session.team else 'Team not specified'}",
            level=2,
        )
        details = [[
            cell("Training Type"), cell("Coach"), cell("Duration")
        ], [
            cell(session.get_training_type_display()),
            cell(session.coach if session.coach else "—"),
            cell(
                f"{session.duration_minutes} minutes"
                if session.duration_minutes else "—"
            ),
        ]]
        make_table(details, [80 * mm, 90 * mm, 55 * mm])

        topic_rows = [[cell("Topic"), cell("Objective")]]
        for item in session.session_topics.all():
            topic_rows.append([
                cell(item.topic.name if item.topic else "—"),
                cell(item.objective.name if item.objective else "—"),
            ])
        if len(topic_rows) == 1:
            topic_rows.append([cell("No topics recorded"), cell("—")])
        make_table(topic_rows, [100 * mm, 125 * mm])

    # 6. Player interventions and coaching points.
    heading("6. INTERVENTIONS AND COACHING POINTS")
    for session in sessions:
        heading(
            f"{session.date.strftime('%d %b %Y')} — "
            f"{session.age_group.name if session.age_group else 'Age group not specified'} — "
            f"{session.team.name if session.team else 'Team not specified'}",
            level=2,
        )
        player_rows = [[
            cell("Player"), cell("Minutes"), cell("Performance"),
            cell("Intervention / Objective / Observation"), cell("Result"),
            cell("Coaching Points"), cell("Next Action"),
        ]]

        for participation in session.player_participations.all():
            player = participation.player
            player_interventions = list(participation.interventions.all())

            if not player_interventions:
                player_rows.append([
                    cell(getattr(player, "full_name", None) or str(player)),
                    cell(participation.minutes),
                    cell(participation.get_performance_display()),
                    cell("No intervention recorded"),
                    cell("—"), cell("—"), cell("—"),
                ])
                continue

            for intervention in player_interventions:
                session_topic = intervention.session_topic
                topic = (
                    session_topic.topic.name
                    if session_topic and session_topic.topic else "—"
                )
                objective = (
                    session_topic.objective.name
                    if session_topic and session_topic.objective else "—"
                )
                details_text = (
                    f"<b>{_safe(topic)}</b><br/>"
                    f"Objective: {_safe(objective)}<br/>"
                    f"Observation: {_safe(intervention.observation)}"
                )

                point_text = []
                for selection in intervention.coaching_points.all():
                    point_name = (
                        selection.coaching_point.name
                        if selection.coaching_point else "—"
                    )
                    result = "Achieved" if selection.achieved else "Not achieved"
                    point_text.append(f"{_safe(point_name)} — {result}")

                player_rows.append([
                    cell(getattr(player, "full_name", None) or str(player)),
                    cell(participation.minutes),
                    cell(participation.get_performance_display()),
                    Paragraph(details_text, styles["SmallCell"]),
                    cell(intervention.get_result_display()),
                    Paragraph("<br/>".join(point_text) or "—", styles["SmallCell"]),
                    cell(intervention.next_action),
                ])

        if len(player_rows) == 1:
            player_rows.append([
                cell("No player participation recorded"),
                cell("—"), cell("—"), cell("—"), cell("—"), cell("—"), cell("—")
            ])

        make_table(
            player_rows,
            [34 * mm, 17 * mm, 28 * mm, 58 * mm, 25 * mm, 48 * mm, 34 * mm],
        )

    # 7. Session evaluations.
    heading("7. SESSION EVALUATIONS AND NEXT ACTIONS")
    for session in sessions:
        heading(
            f"{session.date.strftime('%d %b %Y')} — "
            f"{session.age_group.name if session.age_group else 'Age group not specified'} — "
            f"{session.team.name if session.team else 'Team not specified'}",
            level=2,
        )
        evaluation = getattr(session, "evaluation", None)
        if not evaluation:
            story.append(Paragraph(
                "No session evaluation recorded.",
                styles["Normal"],
            ))
            story.append(Spacer(1, 3 * mm))
            continue

        evaluation_rows = [
            [cell("Evaluation Item"), cell("Details")],
            [cell("Objective Status"), cell(evaluation.get_objective_status_display())],
            [cell("Training Quality"), cell(evaluation.get_training_quality_display())],
            [cell("What Went Well"), cell(evaluation.what_went_well)],
            [cell("Challenges"), cell(evaluation.challenges)],
            [cell("Coach Comment"), cell(evaluation.coach_comment)],
            [cell("Next Action"), cell(evaluation.next_action)],
        ]
        make_table(evaluation_rows, [55 * mm, 195 * mm])

    # Signature section.
    heading("8. REVIEW AND APPROVAL")
    signature_rows = [
        [cell("Coach Name / Signature"), cell("Technical Director Name / Signature")],
        [cell(""), cell("")],
        [cell("Date: __________________________"), cell("Date: __________________________")],
    ]
    make_table(signature_rows, [125 * mm, 125 * mm])

    def add_page_number(canvas, document):
        canvas.saveState()
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(colors.HexColor("#666666"))
        canvas.drawString(12 * mm, 8 * mm, "Weekly Individual Training Report")
        canvas.drawRightString(
            landscape(A4)[0] - 12 * mm,
            8 * mm,
            f"Page {document.page}",
        )
        canvas.restoreState()

    doc.multiBuild(
        story,
        onFirstPage=add_page_number,
        onLaterPages=add_page_number,
    )

    pdf = buffer.getvalue()
    buffer.close()

    group_slug = f"age_group_{selected_age_group.pk}" if selected_age_group else "all_age_groups"
    scope_slug = "all_teams" if not selected_team else f"team_{selected_team.pk}"
    filename = (
        f"weekly_training_report_{group_slug}_{scope_slug}_"
        f"{week_start.isoformat()}_{week_end.isoformat()}.pdf"
    )
    response = HttpResponse(pdf, content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response
