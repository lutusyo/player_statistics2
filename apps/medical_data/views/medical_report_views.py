from io import BytesIO

from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.http import HttpResponse
from django.shortcuts import render
from django.utils import timezone

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    Paragraph,
    PageBreak,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from apps.core.choices import AvailabilityStatus
from apps.medical_data.forms.medical_filter_form import MedicalFilterForm
from apps.medical_data.models.medical_follow_up import MedicalFollowUp
from apps.medical_data.models.medical_recovery_plan import (
    MedicalRecoveryPlan,
    RecoveryPlanStatus,
)
from apps.medical_data.models.medical_visit import MedicalVisit
from version1.reports_app.models.previous_models import TrainingAbsence


# ============================================================
# FILTERS
# ============================================================

def get_filtered_medical_visits(request):
    queryset = (
        MedicalVisit.objects
        .select_related("team", "player", "created_by")
        .order_by("-date")
    )

    form = MedicalFilterForm(request.GET or None)

    if form.is_valid():
        fields = [
            "start_date",
            "end_date",
            "team",
            "player",
            "visit_type",
            "main_complaint",
            "availability_status",
        ]

        filters = {
            f"date__{'gte' if field == 'start_date' else 'lte' if field == 'end_date' else 'exact'}":
            form.cleaned_data.get(field)
            for field in fields
        }

        filters = {
            key: value
            for key, value in filters.items()
            if value not in (None, "")
        }

        queryset = queryset.filter(**filters)

    return queryset, form


def apply_common_filters(queryset, form, date_field, team_field, player_field):
    if not form.is_valid():
        return queryset

    start_date = form.cleaned_data.get("start_date")
    end_date = form.cleaned_data.get("end_date")
    team = form.cleaned_data.get("team")
    player = form.cleaned_data.get("player")

    filters = {}

    if start_date:
        filters[f"{date_field}__gte"] = start_date

    if end_date:
        filters[f"{date_field}__lte"] = end_date

    if team:
        filters[team_field] = team

    if player:
        filters[player_field] = player

    return queryset.filter(**filters)


# ============================================================
# REPORT DATA
# ============================================================

def get_medical_report_data(request):
    medical_visits, filter_form = get_filtered_medical_visits(request)
    today = timezone.localdate()

    start_date = end_date = selected_team = selected_player = None

    if filter_form.is_valid():
        start_date = filter_form.cleaned_data.get("start_date")
        end_date = filter_form.cleaned_data.get("end_date")
        selected_team = filter_form.cleaned_data.get("team")
        selected_player = filter_form.cleaned_data.get("player")

    # Medical summary
    total_records = medical_visits.count()
    new_injuries = medical_visits.filter(visit_type="new_injury").count()
    regular_checkups = medical_visits.filter(
        visit_type="regular_checkup"
    ).count()

    available_players = (
        medical_visits
        .filter(availability_status=AvailabilityStatus.AVAILABLE)
        .values("player")
        .distinct()
        .count()
    )

    restricted_players = (
        medical_visits
        .filter(availability_status=AvailabilityStatus.RESTRICTED)
        .values("player")
        .distinct()
        .count()
    )

    unavailable_players = (
        medical_visits
        .filter(availability_status=AvailabilityStatus.NOT_AVAILABLE)
        .values("player")
        .distinct()
        .count()
    )

    # Complaint analysis
    complaint_data = (
        medical_visits
        .values("main_complaint")
        .annotate(total=Count("id"))
        .order_by("-total")
    )

    # Team analysis
    team_data = (
        medical_visits
        .values("team__name")
        .annotate(total=Count("id"))
        .order_by("-total")
    )

    team_labels = [item["team__name"] for item in team_data]
    team_values = [item["total"] for item in team_data]

    # Training absences
    absence_queryset = TrainingAbsence.objects.select_related(
        "player",
        "training_session",
        "training_session__team",
    )

    absence_queryset = apply_common_filters(
        absence_queryset,
        filter_form,
        "training_session__date",
        "training_session__team",
        "player",
    )

    total_training_absences = absence_queryset.count()

    injured_absences = absence_queryset.filter(reason="INJURED").count()
    sick_absences = absence_queryset.filter(reason="SICK").count()
    personal_absences = absence_queryset.filter(reason="PERSONAL").count()
    unexcused_absences = absence_queryset.filter(reason="UNEXCUSED").count()

    training_absence_by_player = (
        absence_queryset
        .values("player", "training_session__team__name")
        .annotate(
            total_missed=Count("id"),
            injured=Count("id", filter=Q(reason="INJURED")),
            sick=Count("id", filter=Q(reason="SICK")),
            personal=Count("id", filter=Q(reason="PERSONAL")),
            unexcused=Count("id", filter=Q(reason="UNEXCUSED")),
        )
        .order_by("-total_missed")
    )

    # Follow-ups
    followup_queryset = MedicalFollowUp.objects.select_related(
        "visit",
        "visit__player",
        "visit__team",
    )

    followup_queryset = apply_common_filters(
        followup_queryset,
        filter_form,
        "visit__date",
        "visit__team",
        "visit__player",
    )

    overdue_followups = (
        followup_queryset
        .filter(status=False, review_date__lt=today)
        .order_by("review_date")
    )

    upcoming_followups = (
        followup_queryset
        .filter(status=False, review_date__gte=today)
        .order_by("review_date")
    )

    # Recovery plans
    recovery_queryset = MedicalRecoveryPlan.objects.select_related(
        "visit",
        "visit__player",
        "visit__team",
    )

    recovery_queryset = apply_common_filters(
        recovery_queryset,
        filter_form,
        "start_date",
        "visit__team",
        "visit__player",
    )

    active_recovery_plans = recovery_queryset.filter(
        status=RecoveryPlanStatus.ACTIVE
    ).count()

    completed_recovery_plans = recovery_queryset.filter(
        status=RecoveryPlanStatus.COMPLETED
    ).count()

    cancelled_recovery_plans = recovery_queryset.filter(
        status=RecoveryPlanStatus.CANCELLED
    ).count()

    # Expected returns
    upcoming_returns = (
        medical_visits
        .filter(
            expected_return_date__isnull=False,
            expected_return_date__gte=today,
        )
        .order_by("expected_return_date")
    )

    return {
        "page_title": "Medical Report",
        "filter_form": filter_form,
        "medical_visits": medical_visits,
        "total_records": total_records,
        "new_injuries": new_injuries,
        "regular_checkups": regular_checkups,
        "available_players": available_players,
        "restricted_players": restricted_players,
        "unavailable_players": unavailable_players,
        "complaint_data": complaint_data,
        "team_labels": team_labels,
        "team_values": team_values,
        "team_data": team_data,
        "total_training_absences": total_training_absences,
        "injured_absences": injured_absences,
        "sick_absences": sick_absences,
        "personal_absences": personal_absences,
        "unexcused_absences": unexcused_absences,
        "training_absence_by_player": training_absence_by_player,
        "active_recovery_plans": active_recovery_plans,
        "completed_recovery_plans": completed_recovery_plans,
        "cancelled_recovery_plans": cancelled_recovery_plans,
        "overdue_followups": overdue_followups,
        "upcoming_followups": upcoming_followups,
        "upcoming_returns": upcoming_returns,
        "recent_visits": medical_visits[:10],
    }


# ============================================================
# MEDICAL REPORT PAGE
# ============================================================

@login_required
def medical_report(request):
    return render(
        request,
        "medical_data/medical_report.html",
        get_medical_report_data(request),
    )


# ============================================================
# EXCEL REPORT
# ============================================================

@login_required
def medical_report_excel(request):
    context = get_medical_report_data(request)
    wb = Workbook()

    header_fill = PatternFill(fill_type="solid", fgColor="1F4E78")
    section_fill = PatternFill(fill_type="solid", fgColor="D9EAF7")

    white_font = Font(color="FFFFFF", bold=True)
    bold_font = Font(bold=True)

    thin_border = Border(
        left=Side(style="thin"),
        right=Side(style="thin"),
        top=Side(style="thin"),
        bottom=Side(style="thin"),
    )

    def style_header(ws, row):
        for cell in ws[row]:
            cell.fill = header_fill
            cell.font = white_font
            cell.alignment = Alignment(
                horizontal="center",
                vertical="center",
            )
            cell.border = thin_border

    def auto_width(ws):
        for column_cells in ws.columns:
            max_length = max(
                (len(str(cell.value or "")) for cell in column_cells),
                default=0,
            )
            column = get_column_letter(column_cells[0].column)
            ws.column_dimensions[column].width = min(
                max(max_length + 2, 12),
                40,
            )

    def add_title(ws, title):
        ws["A1"] = title
        ws["A1"].font = Font(bold=True, size=16)
        ws["A1"].alignment = Alignment(horizontal="center")
        ws.merge_cells("A1:F1")

    def border_rows(ws, start=4):
        for row in ws.iter_rows(min_row=start):
            for cell in row:
                cell.border = thin_border

    # --------------------------------------------------------
    # SHEET 1 — MEDICAL SUMMARY
    # --------------------------------------------------------

    ws = wb.active
    ws.title = "Medical Summary"
    add_title(ws, "Medical Report Summary")

    ws["A3"] = "Report Information"
    ws["A3"].font = bold_font
    ws["A3"].fill = section_fill

    form = context["filter_form"]
    valid = form.is_valid()

    filters = [
        ("Start Date", form.cleaned_data.get("start_date") if valid else ""),
        ("End Date", form.cleaned_data.get("end_date") if valid else ""),
        ("Team", form.cleaned_data.get("team") if valid else ""),
        ("Player", form.cleaned_data.get("player") if valid else ""),
    ]

    for row, (label, value) in enumerate(filters, 4):
        ws.cell(row, 1, label)
        ws.cell(row, 2, value)

    ws["A9"] = "Medical Statistics"
    ws["A9"].font = bold_font
    ws["A9"].fill = section_fill

    summary_data = [
        ("Total Medical Records", context["total_records"]),
        ("New Injuries", context["new_injuries"]),
        ("Regular Checkups", context["regular_checkups"]),
        ("Available Players", context["available_players"]),
        ("Restricted Players", context["restricted_players"]),
        ("Unavailable Players", context["unavailable_players"]),
        ("Active Recovery Plans", context["active_recovery_plans"]),
        ("Completed Recovery Plans", context["completed_recovery_plans"]),
        ("Cancelled Recovery Plans", context["cancelled_recovery_plans"]),
        ("Total Training Absences", context["total_training_absences"]),
        ("Injury-related Absences", context["injured_absences"]),
        ("Sick Absences", context["sick_absences"]),
        ("Personal Absences", context["personal_absences"]),
        ("Unexcused Absences", context["unexcused_absences"]),
    ]

    for row, (label, value) in enumerate(summary_data, 10):
        ws.cell(row, 1, label)
        ws.cell(row, 2, value)
        ws.cell(row, 1).font = bold_font
        ws.cell(row, 1).border = thin_border
        ws.cell(row, 2).border = thin_border

    auto_width(ws)

    # --------------------------------------------------------
    # SHEET 2 — INJURY ANALYSIS
    # --------------------------------------------------------

    ws = wb.create_sheet("Injury Analysis")
    add_title(ws, "Medical Complaint Analysis")
    ws.append([])
    ws.append(["Main Complaint", "Total Records"])
    style_header(ws, 3)

    for item in context["complaint_data"]:
        ws.append([item["main_complaint"], item["total"]])

    border_rows(ws)
    auto_width(ws)

    # --------------------------------------------------------
    # SHEET 3 — TRAINING IMPACT
    # --------------------------------------------------------

    ws = wb.create_sheet("Training Impact")
    add_title(ws, "Training Impact")
    ws.append([])
    ws.append(["Absence Reason", "Training Sessions Missed"])
    style_header(ws, 3)

    training_impact = [
        ("Injured", context["injured_absences"]),
        ("Sick", context["sick_absences"]),
        ("Personal", context["personal_absences"]),
        ("Unexcused", context["unexcused_absences"]),
        ("Total", context["total_training_absences"]),
    ]

    for row in training_impact:
        ws.append(row)

    border_rows(ws)
    auto_width(ws)

    # --------------------------------------------------------
    # SHEET 4 — PLAYER TRAINING IMPACT
    # --------------------------------------------------------

    ws = wb.create_sheet("Player Training Impact")
    add_title(ws, "Training Sessions Missed by Player")
    ws.append([])

    ws.append([
        "Player",
        "Team",
        "Total Missed",
        "Injured",
        "Sick",
        "Personal",
        "Unexcused",
    ])

    style_header(ws, 3)

    for item in context["training_absence_by_player"]:
        ws.append([
            str(item["player"]),
            item["training_session__team__name"],
            item["total_missed"],
            item["injured"],
            item["sick"],
            item["personal"],
            item["unexcused"],
        ])

    border_rows(ws)
    auto_width(ws)

    # --------------------------------------------------------
    # SHEET 5 — RECOVERY & FOLLOW-UPS
    # --------------------------------------------------------

    ws = wb.create_sheet("Recovery & Follow-ups")
    add_title(ws, "Recovery Plans and Follow-ups")

    ws["A3"] = "Recovery Plans"
    ws["A3"].font = bold_font
    ws["A3"].fill = section_fill

    recovery_headers = [
        "Player",
        "Team",
        "Start Date",
        "Expected End Date",
        "Actual Recovery Date",
        "Status",
    ]

    for col, header in enumerate(recovery_headers, 1):
        ws.cell(4, col, header)

    style_header(ws, 4)

    recovery_plans = MedicalRecoveryPlan.objects.select_related(
        "visit",
        "visit__player",
        "visit__team",
    )

    recovery_plans = apply_common_filters(
        recovery_plans,
        form,
        "start_date",
        "visit__team",
        "visit__player",
    )

    row = 5

    for plan in recovery_plans.order_by("-start_date"):
        ws.append([
            str(plan.visit.player),
            str(plan.visit.team),
            plan.start_date,
            plan.expected_end_date,
            plan.actual_recovery_date,
            plan.get_status_display(),
        ])
        row += 1

    followup_start = row + 1

    ws.cell(followup_start, 1, "Follow-ups")
    ws.cell(followup_start, 1).font = bold_font
    ws.cell(followup_start, 1).fill = section_fill

    followup_header_row = followup_start + 1

    followup_headers = [
        "Player",
        "Team",
        "Review Date",
        "Status",
    ]

    for col, header in enumerate(followup_headers, 1):
        ws.cell(followup_header_row, col, header)

    style_header(ws, followup_header_row)

    all_followups = (
        MedicalFollowUp.objects
        .select_related("visit", "visit__player", "visit__team")
        .filter(status=False)
    )

    all_followups = apply_common_filters(
        all_followups,
        form,
        "visit__date",
        "visit__team",
        "visit__player",
    )

    row = followup_header_row + 1

    for followup in all_followups.order_by("review_date"):
        ws.append([
            str(followup.visit.player),
            str(followup.visit.team),
            followup.review_date,
            "Completed" if followup.status else "Pending",
        ])
        row += 1

    auto_width(ws)

    # --------------------------------------------------------
    # SHEET 6 — MEDICAL RECORDS
    # --------------------------------------------------------

    ws = wb.create_sheet("Medical Records")
    add_title(ws, "Detailed Medical Records")

    headers = [
        "Date",
        "Team",
        "Player",
        "Visit Type",
        "Main Complaint",
        "Body Side",
        "Injury Status",
        "Mechanism of Injury",
        "Training Status",
        "Availability",
        "Working Diagnosis",
        "Therapy",
        "Recommendations",
        "Next Review Date",
        "Expected Return Date",
    ]

    ws.append([])
    ws.append(headers)
    style_header(ws, 3)

    for visit in context["medical_visits"]:
        ws.append([
            visit.date,
            str(visit.team),
            str(visit.player),
            visit.get_visit_type_display(),
            visit.get_main_complaint_display(),
            visit.get_body_side_display(),
            visit.get_injury_status_display(),
            visit.get_mechanism_of_injury_display(),
            visit.get_training_session_status_display(),
            visit.get_availability_status_display(),
            visit.working_diagnosis,
            visit.therapy,
            visit.recommendations,
            visit.next_review_date,
            visit.expected_return_date,
        ])

    for row in ws.iter_rows(min_row=4):
        for cell in row:
            cell.border = thin_border
            cell.alignment = Alignment(
                vertical="top",
                wrap_text=True,
            )

    auto_width(ws)

    for sheet in wb.worksheets:
        sheet.freeze_panes = "A4"

    response = HttpResponse(
        content_type=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        )
    )

    response["Content-Disposition"] = (
        'attachment; filename="medical_report.xlsx"'
    )

    wb.save(response)
    return response


# PDF REPORT
@login_required
def medical_report_pdf(request):
    context = get_medical_report_data(request)
    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        rightMargin=12 * mm,
        leftMargin=12 * mm,
        topMargin=15 * mm,
        bottomMargin=15 * mm,
        title="Medical Report",
        author="Azam FC Academy",
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "MedicalTitle",
        parent=styles["Title"],
        fontSize=18,
        leading=22,
        alignment=TA_CENTER,
        spaceAfter=8,
    )

    subtitle_style = ParagraphStyle(
        "MedicalSubtitle",
        parent=styles["Normal"],
        fontSize=9,
        leading=12,
        alignment=TA_CENTER,
        textColor=colors.grey,
        spaceAfter=12,
    )

    section_style = ParagraphStyle(
        "SectionTitle",
        parent=styles["Heading2"],
        fontSize=12,
        leading=15,
        spaceBefore=8,
        spaceAfter=6,
    )

    story = []

    def display_value(value):
        return "-" if value in (None, "") else str(value)

    def make_table(data, widths):
        table = Table(
            data,
            colWidths=widths,
            repeatRows=1,
        )

        table.setStyle(
            TableStyle([
                ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1F4E78")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ])
        )

        return table

    # --------------------------------------------------------
    # TITLE
    # --------------------------------------------------------

    story.extend([
        Paragraph("AZAM FC ACADEMY", title_style),
        Paragraph("MEDICAL REPORT", title_style),
        Paragraph(
            f"Generated on {timezone.localdate().strftime('%d %B %Y')}",
            subtitle_style,
        ),
    ])

    # --------------------------------------------------------
    # FILTERS
    # --------------------------------------------------------

    story.append(Paragraph("Report Filters", section_style))

    form = context["filter_form"]
    valid = form.is_valid()

    start_date = form.cleaned_data.get("start_date") if valid else None
    end_date = form.cleaned_data.get("end_date") if valid else None
    team = form.cleaned_data.get("team") if valid else None
    player = form.cleaned_data.get("player") if valid else None

    filter_data = [
        ["Filter", "Selected Value"],
        ["Start Date", display_value(start_date)],
        ["End Date", display_value(end_date)],
        ["Team", display_value(team)],
        ["Player", display_value(player)],
    ]

    story.append(
        make_table(
            filter_data,
            [45 * mm, 130 * mm],
        )
    )

    story.append(Spacer(1, 8))

    # --------------------------------------------------------
    # MEDICAL SUMMARY
    # --------------------------------------------------------

    story.append(Paragraph("Medical Summary", section_style))

    summary_data = [
        ["Indicator", "Total"],
        ["Total Medical Records", context["total_records"]],
        ["New Injuries", context["new_injuries"]],
        ["Regular Checkups", context["regular_checkups"]],
        ["Available Players", context["available_players"]],
        ["Restricted Players", context["restricted_players"]],
        ["Unavailable Players", context["unavailable_players"]],
        ["Active Recovery Plans", context["active_recovery_plans"]],
        ["Completed Recovery Plans", context["completed_recovery_plans"]],
        ["Cancelled Recovery Plans", context["cancelled_recovery_plans"]],
    ]

    story.append(
        make_table(
            summary_data,
            [130 * mm, 45 * mm],
        )
    )

    # --------------------------------------------------------
    # TRAINING IMPACT
    # --------------------------------------------------------

    story.append(Paragraph("Training Impact", section_style))

    training_data = [
        ["Absence Reason", "Sessions Missed"],
        ["Injured", context["injured_absences"]],
        ["Sick", context["sick_absences"]],
        ["Personal", context["personal_absences"]],
        ["Unexcused", context["unexcused_absences"]],
        ["TOTAL", context["total_training_absences"]],
    ]

    story.append(
        make_table(
            training_data,
            [130 * mm, 45 * mm],
        )
    )

    # --------------------------------------------------------
    # COMPLAINT ANALYSIS
    # --------------------------------------------------------

    story.append(
        Paragraph("Medical Complaint Analysis", section_style)
    )

    complaint_data = [["Main Complaint", "Total Records"]]

    complaint_data += [
        [
            display_value(item["main_complaint"]),
            item["total"],
        ]
        for item in context["complaint_data"]
    ]

    if len(complaint_data) == 1:
        complaint_data.append(["No records", 0])

    story.append(
        make_table(
            complaint_data,
            [130 * mm, 45 * mm],
        )
    )

    # --------------------------------------------------------
    # TEAM ANALYSIS
    # --------------------------------------------------------

    story.append(Paragraph("Team Analysis", section_style))

    team_data = [["Team", "Medical Records"]]

    team_data += [
        [
            display_value(item["team__name"]),
            item["total"],
        ]
        for item in context["team_data"]
    ]

    if len(team_data) == 1:
        team_data.append(["No records", 0])

    story.append(
        make_table(
            team_data,
            [130 * mm, 45 * mm],
        )
    )

    story.append(PageBreak())

    # --------------------------------------------------------
    # PLAYER TRAINING ABSENCES
    # --------------------------------------------------------

    story.append(
        Paragraph(
            "Training Sessions Missed by Player",
            section_style,
        )
    )

    player_absence_data = [[
        "Player",
        "Team",
        "Total",
        "Injured",
        "Sick",
        "Personal",
        "Unexcused",
    ]]

    player_absence_data += [
        [
            display_value(item["player"]),
            display_value(item["training_session__team__name"]),
            item["total_missed"],
            item["injured"],
            item["sick"],
            item["personal"],
            item["unexcused"],
        ]
        for item in context["training_absence_by_player"]
    ]

    if len(player_absence_data) == 1:
        player_absence_data.append([
            "No records",
            "-",
            0,
            0,
            0,
            0,
            0,
        ])

    story.append(
        make_table(
            player_absence_data,
            [
                38 * mm,
                30 * mm,
                18 * mm,
                18 * mm,
                18 * mm,
                20 * mm,
                23 * mm,
            ],
        )
    )

    # --------------------------------------------------------
    # RECOVERY PLANS
    # --------------------------------------------------------

    story.append(Paragraph("Recovery Plans", section_style))

    recovery_queryset = MedicalRecoveryPlan.objects.select_related(
        "visit",
        "visit__player",
        "visit__team",
    )

    recovery_queryset = apply_common_filters(
        recovery_queryset,
        form,
        "start_date",
        "visit__team",
        "visit__player",
    )

    recovery_data = [[
        "Player",
        "Team",
        "Start",
        "Expected End",
        "Actual Recovery",
        "Status",
    ]]

    recovery_data += [
        [
            display_value(plan.visit.player),
            display_value(plan.visit.team),
            display_value(plan.start_date),
            display_value(plan.expected_end_date),
            display_value(plan.actual_recovery_date),
            display_value(plan.get_status_display()),
        ]
        for plan in recovery_queryset.order_by("-start_date")
    ]

    if len(recovery_data) == 1:
        recovery_data.append([
            "No recovery plans",
            "-",
            "-",
            "-",
            "-",
            "-",
        ])

    story.append(
        make_table(
            recovery_data,
            [
                35 * mm,
                30 * mm,
                25 * mm,
                30 * mm,
                30 * mm,
                25 * mm,
            ],
        )
    )

    # --------------------------------------------------------
    # FOLLOW-UPS
    # --------------------------------------------------------

    story.append(Paragraph("Pending Follow-ups", section_style))

    followup_queryset = (
        MedicalFollowUp.objects
        .select_related("visit", "visit__player", "visit__team")
        .filter(status=False)
    )

    followup_queryset = apply_common_filters(
        followup_queryset,
        form,
        "visit__date",
        "visit__team",
        "visit__player",
    )

    followup_data = [
        ["Player", "Team", "Review Date", "Status"]
    ]

    followup_data += [
        [
            display_value(followup.visit.player),
            display_value(followup.visit.team),
            display_value(followup.review_date),
            "Pending",
        ]
        for followup in followup_queryset.order_by("review_date")
    ]

    if len(followup_data) == 1:
        followup_data.append([
            "No pending follow-ups",
            "-",
            "-",
            "-",
        ])

    story.append(
        make_table(
            followup_data,
            [
                55 * mm,
                45 * mm,
                40 * mm,
                35 * mm,
            ],
        )
    )

    # --------------------------------------------------------
    # EXPECTED RETURNS
    # --------------------------------------------------------

    story.append(
        Paragraph("Expected Player Returns", section_style)
    )

    return_data = [
        ["Player", "Team", "Expected Return", "Availability"]
    ]

    return_data += [
        [
            display_value(visit.player),
            display_value(visit.team),
            display_value(visit.expected_return_date),
            visit.get_availability_status_display(),
        ]
        for visit in context["upcoming_returns"]
    ]

    if len(return_data) == 1:
        return_data.append([
            "No upcoming returns",
            "-",
            "-",
            "-",
        ])

    story.append(
        make_table(
            return_data,
            [
                55 * mm,
                45 * mm,
                40 * mm,
                35 * mm,
            ],
        )
    )

    story.append(PageBreak())

    # --------------------------------------------------------
    # DETAILED MEDICAL RECORDS
    # --------------------------------------------------------

    story.append(
        Paragraph("Detailed Medical Records", section_style)
    )

    medical_data = [[
        "Date",
        "Team",
        "Player",
        "Visit",
        "Complaint",
        "Status",
        "Training",
        "Availability",
    ]]

    medical_data += [
        [
            display_value(visit.date),
            display_value(visit.team),
            display_value(visit.player),
            display_value(visit.get_visit_type_display()),
            display_value(visit.get_main_complaint_display()),
            display_value(visit.get_injury_status_display()),
            display_value(
                visit.get_training_session_status_display()
            ),
            display_value(
                visit.get_availability_status_display()
            ),
        ]
        for visit in context["medical_visits"]
    ]

    if len(medical_data) == 1:
        medical_data.append([
            "No medical records",
            "-",
            "-",
            "-",
            "-",
            "-",
            "-",
            "-",
        ])

    detail_table = Table(
        medical_data,
        colWidths=[
            18 * mm,
            25 * mm,
            32 * mm,
            25 * mm,
            30 * mm,
            22 * mm,
            28 * mm,
            28 * mm,
        ],
        repeatRows=1,
    )

    detail_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1F4E78")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 6),
            ("GRID", (0, 0), (-1, -1), 0.3, colors.grey),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 3),
            ("RIGHTPADDING", (0, 0), (-1, -1), 3),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ])
    )

    story.append(detail_table)

    # --------------------------------------------------------
    # BUILD PDF
    # --------------------------------------------------------

    doc.build(story)

    pdf = buffer.getvalue()
    buffer.close()

    response = HttpResponse(
        pdf,
        content_type="application/pdf",
    )

    response["Content-Disposition"] = (
        'attachment; filename="medical_report.pdf"'
    )

    return response