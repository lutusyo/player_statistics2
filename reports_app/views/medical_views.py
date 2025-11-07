import io
import pandas as pd
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.utils import timezone
from reports_app.models import Medical
from reports_app.forms import ReportFilterForm
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from teams_app.models import Team


def medical_reports(request, team_id):
    team = get_object_or_404(Team, id=team_id)
    form = ReportFilterForm(request.GET or None)
    queryset = Medical.objects.filter(squad_id=team_id).select_related('name', 'squad')

    # Filtering logic
    if form.is_valid():
        team = form.cleaned_data.get('team')
        period = form.cleaned_data.get('period')
        start_date = form.cleaned_data.get('start_date')
        end_date = form.cleaned_data.get('end_date')

        if team:
            queryset = queryset.filter(squad=team)
        if start_date and end_date:
            queryset = queryset.filter(date__range=[start_date, end_date])
        elif period and period != 'All':
            now = timezone.now().date()
            if period == 'This Week':
                queryset = queryset.filter(date__week=now.isocalendar()[1])
            elif period == 'This Month':
                queryset = queryset.filter(date__month=now.month)
            elif period == 'This Year':
                queryset = queryset.filter(date__year=now.year)

    context = {
        'form': form,
        'records': queryset,
        'team': team,
        'team_id': team_id,  # 👈 include for navigation links
    }

    return render(request, 'reports_app/daily_report_templates/1medical/medical_reports.html', context)


# ---- Export to Excel ----
def export_medical_excel(request, team_id):
    queryset = Medical.objects.filter(squad_id=team_id).select_related('name', 'squad')
    df = pd.DataFrame(list(queryset.values(
        'name__name', 'squad__name', 'injury_or_illness', 'status', 'comments', 'date'
    )))
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Medical Reports')
    buffer.seek(0)
    response = HttpResponse(
        buffer,
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="medical_reports_team_{team_id}.xlsx"'
    return response


# ---- Export to PDF ----
def export_medical_pdf(request, team_id):
    queryset = Medical.objects.filter(squad_id=team_id).select_related('name', 'squad')

    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    y = height - 50

    p.setFont("Helvetica-Bold", 14)
    p.drawString(180, y, f"Medical Report Summary - Team {team_id}")
    y -= 40

    p.setFont("Helvetica", 10)
    for record in queryset:
        if y < 100:
            p.showPage()
            y = height - 50
            p.setFont("Helvetica", 10)
        p.drawString(
            50, y,
            f"{record.name.name} | {record.squad.name} | {record.injury_or_illness} | {record.status} | {record.date}"
        )
        y -= 20

    p.save()
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="medical_reports_team_{team_id}.pdf"'
    return response
