import io
import pandas as pd
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.utils import timezone
from reports_app.models import Scouting
from reports_app.forms import ReportFilterForm
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from teams_app.models import Team


# ---- Display scouting reports ----
def scouting_reports(request, team_id):
    team = get_object_or_404(Team, id=team_id)
    form = ReportFilterForm(request.GET or None)
    queryset = Scouting.objects.filter(squad_id=team_id).select_related('squad')

    # Filtering
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

    return render(request, 'reports_app/2scouting/scouting_reports.html', {
        'form': form,
        'team': team,
        'records': queryset,
        'team_id': team_id,
    })


# ---- Export scouting reports to Excel ----
def export_scouting_excel(request, team_id):
    queryset = Scouting.objects.filter(squad_id=team_id).select_related('squad')
    df = pd.DataFrame(list(queryset.values(
        'name', 'pos', 'dob', 'squad__name', 'agreement', 'comments', 'date'
    )))
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Scouting Reports')
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="scouting_reports.xlsx"'
    return response


# ---- Export scouting reports to PDF ----
def export_scouting_pdf(request, team_id):
    queryset = Scouting.objects.filter(squad_id=team_id).select_related('squad')
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    y = height - 50

    p.setFont("Helvetica-Bold", 14)
    p.drawString(200, y, "Scouting Report Summary")
    y -= 40
    p.setFont("Helvetica", 10)

    for record in queryset:
        if y < 100:
            p.showPage()
            y = height - 50
            p.setFont("Helvetica", 10)
        p.drawString(50, y, f"{record.name} | {record.pos} | {record.squad.name} | {record.agreement} | {record.date}")
        y -= 20

    p.save()
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="scouting_reports.pdf"'
    return response
