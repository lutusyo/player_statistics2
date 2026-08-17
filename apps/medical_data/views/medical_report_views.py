from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.http import HttpResponse
from django.shortcuts import render
from django.utils import timezone
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment
from openpyxl.utils import get_column_letter
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from apps.medical_data.forms.medical_filter_form import MedicalFilterForm
from apps.medical_data.models.medical_visit import MedicalVisit


def get_filtered_medical_visits(request):
    queryset = MedicalVisit.objects.select_related("team", "player", "created_by")
    form = MedicalFilterForm(request.GET or None)

    if form.is_valid():
        filters = {
            "date__gte": form.cleaned_data.get("start_date"),
            "date__lte": form.cleaned_data.get("end_date"),
            "team": form.cleaned_data.get("team"),
            "player": form.cleaned_data.get("player"),
            "visit_type": form.cleaned_data.get("visit_type"),
            "main_complaint": form.cleaned_data.get("main_complaint"),
            "availability_status": form.cleaned_data.get("availability_status"),
        }
        queryset = queryset.filter(**{k: v for k, v in filters.items() if v})

    return queryset, form


@login_required
def medical_report(request):
    queryset, form = get_filtered_medical_visits(request)

    context = {
        "page_title": "Medical Report",
        "medical_visits": queryset,
        "filter_form": form,
        "total_records": queryset.count(),
        "new_injuries": queryset.filter(visit_type="new_injury").count(),
        "regular_checkups": queryset.filter(visit_type="regular_checkup").count(),
        "complaint_data": queryset.values("main_complaint").annotate(
            total=Count("id")
        ).order_by("-total"),
    }

    return render(request, "medical_data/medical_report.html", context)


@login_required
def medical_report_excel(request):
    queryset, _ = get_filtered_medical_visits(request)

    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = "Medical Report"

    worksheet["A1"] = "ACADEMY MEDICAL REPORT"
    worksheet["A1"].font = Font(bold=True, size=16)
    worksheet.merge_cells("A1:N1")

    worksheet["A2"] = (f"Generated: {timezone.localtime().strftime('%d %B %Y %H:%M')}")
    worksheet.merge_cells("A2:N2")

    headers = [
        "Date", "Team", "Player", "Visit Type", "Main Complaint",
        "Body Side", "Injury Status", "Mechanism", "History of Injury",
        "Physical Examination", "Working Diagnosis", "Therapy",
        "Training Status", "Availability",
    ]

    worksheet.append([])
    worksheet.append(headers)

    for cell in worksheet[4]:
        cell.font = Font(bold=True)
        cell.alignment = Alignment(horizontal="center")

    for visit in queryset:
        worksheet.append([
            visit.date.strftime("%d/%m/%Y"),
            str(visit.team),
            str(visit.player),
            visit.get_visit_type_display(),
            visit.get_main_complaint_display(),
            visit.get_body_side_display(),
            visit.get_injury_status_display(),
            visit.get_mechanism_of_injury_display(),
            visit.history_of_injury,
            visit.physical_examination,
            visit.working_diagnosis,
            visit.therapy,
            visit.get_training_session_status_display(),
            visit.get_availability_status_display(),
        ])

    widths = [14, 18, 25, 20, 20, 14, 16, 18, 35, 35, 35, 35, 20, 20]

    for column, width in enumerate(widths, 1):
        worksheet.column_dimensions[get_column_letter(column)].width = width

    for row in worksheet.iter_rows():
        for cell in row:
            cell.alignment = Alignment(vertical="top", wrap_text=True)

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response["Content-Disposition"] = 'attachment; filename="medical_report.xlsx"'
    workbook.save(response)

    return response


@login_required
def medical_report_pdf(request):
    queryset, _ = get_filtered_medical_visits(request)

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="medical_report.pdf"'

    document = SimpleDocTemplate(
        response,
        pagesize=landscape(A4),
        rightMargin=10 * mm,
        leftMargin=10 * mm,
        topMargin=10 * mm,
        bottomMargin=10 * mm,
    )

    styles = getSampleStyleSheet()
    elements = [
        Paragraph("<b>ACADEMY MEDICAL REPORT</b>", styles["Title"]),
        Spacer(1, 8),
        Paragraph(
            f"Generated: {timezone.localtime().strftime('%d %B %Y %H:%M')}",
            styles["Normal"],
        ),
        Spacer(1, 12),
    ]

    headers = [
        "Date", "Player", "Team", "Visit", "Complaint",
        "Side", "Diagnosis", "Therapy", "Training", "Availability",
    ]

    data = [headers]

    for visit in queryset:
        data.append([
            visit.date.strftime("%d/%m/%Y"),
            str(visit.player),
            str(visit.team),
            visit.get_visit_type_display(),
            visit.get_main_complaint_display(),
            visit.get_body_side_display(),
            visit.working_diagnosis or "-",
            visit.therapy or "-",
            visit.get_training_session_status_display(),
            visit.get_availability_status_display(),
        ])

    table = Table(
        data,
        repeatRows=1,
        colWidths=[
            20 * mm, 30 * mm, 25 * mm, 25 * mm, 28 * mm,
            20 * mm, 45 * mm, 40 * mm, 30 * mm, 30 * mm,
        ],
    )

    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#212529")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 7),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [
            colors.white,
            colors.HexColor("#f8f9fa"),
        ]),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))

    elements.append(table)
    document.build(elements)

    return response