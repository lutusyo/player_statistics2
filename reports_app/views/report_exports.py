import io
import pandas as pd
from datetime import datetime
from django.http import HttpResponse
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas
from reports_app.models import (
    Medical, Transition, Scouting, Performance,
    IndividualActionPlan, Mesocycle, FitnessPlan
)
from .report_filters import filter_queryset_by_period
from django.utils import timezone
from teams_app.models import Team


SECTION_MAP = {
    'Medical': (Medical.objects.all(), 'date'),
    'Transition': (Transition.objects.all(), 'date'),
    'Scouting': (Scouting.objects.all(), 'date'),
    'Performance': (Performance.objects.all(), 'date'),
    'IAP': (IndividualActionPlan.objects.all(), 'date'),
    'Mesocycle': (Mesocycle.objects.all(), 'start_date'),
    'Fitness': (FitnessPlan.objects.all(), 'date'),
}


def get_filtered_data(request):
    team_id = request.GET.get('team')
    period = request.GET.get('period')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    qs = {}

    for name, (queryset, date_field) in SECTION_MAP.items():
        # Filter by team if applicable
        if team_id:
            team = Team.objects.get(id=team_id)
            if hasattr(queryset.model, 'squad'):
                queryset = queryset.filter(squad=team)
            elif hasattr(queryset.model, 'team'):
                queryset = queryset.filter(team=team)

        # Filter by period
        if period:
            queryset = filter_queryset_by_period(queryset, period, start_date, end_date, date_field)

        qs[name] = queryset

    return qs



# -------------------------------
# 📊 EXPORT INDIVIDUAL SECTION (EXCEL)
# -------------------------------
def export_section_excel(request, section):
    qs = get_filtered_data(request)
    model_data = qs.get(section)
    if not model_data.exists():
        return HttpResponse("No data for this section")

    df = pd.DataFrame(list(model_data.values()))
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name=section)
    buffer.seek(0)

    response = HttpResponse(
        buffer,
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename={section}_Report_{datetime.now().date()}.xlsx'
    return response


# -------------------------------
# 📘 EXPORT COMBINED (EXCEL)
# -------------------------------
def export_combined_excel(request):
    qs = get_filtered_data(request)
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        for name, q in qs.items():
            if q.exists():
                df = pd.DataFrame(list(q.values()))
                df.to_excel(writer, index=False, sheet_name=name)
    buffer.seek(0)

    response = HttpResponse(
        buffer,
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename=All_Sections_Report_{datetime.now().date()}.xlsx'
    return response


# -------------------------------
# 🧾 EXPORT COMBINED (PDF)
# -------------------------------
def export_combined_pdf(request):
    qs = get_filtered_data(request)
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=landscape(A4))
    width, height = landscape(A4)
    y = height - 50

    p.setFont("Helvetica-Bold", 16)
    p.drawString(50, y, "Combined Reports")
    p.setFont("Helvetica", 10)
    y -= 30

    for name, q in qs.items():
        p.setFont("Helvetica-Bold", 12)
        p.drawString(50, y, f"{name} Data")
        y -= 15
        p.setFont("Helvetica", 9)

        if not q.exists():
            p.drawString(70, y, "No records")
            y -= 20
            continue

        df = pd.DataFrame(list(q.values()))
        for col in df.columns[:6]:  # limit columns per page
            p.drawString(70, y, f"{col}")
            y -= 12
            for val in df[col].head(3):  # preview few rows
                p.drawString(90, y, str(val))
                y -= 10
            y -= 8
            if y < 80:
                p.showPage()
                y = height - 50

        y -= 20

    p.save()
    buffer.seek(0)

    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename=Combined_Report_{datetime.now().date()}.pdf'
    return response
