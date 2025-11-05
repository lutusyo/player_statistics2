import io
import pandas as pd
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from reports_app.models import FitnessPlan
from reports_app.forms import ReportFilterForm
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from teams_app.models import Team


def fitness_reports(request, team_id):
    team = get_object_or_404(Team, id=team_id)
    form = ReportFilterForm(request.GET or None)
    queryset = FitnessPlan.objects.filter(team_id=team_id).select_related('team')

    if form.is_valid():
        team = form.cleaned_data.get('team')
        if team:
            queryset = queryset.filter(team=team)

    return render(request, 'reports_app/5fitness/fitness_reports.html', {
        'form': form,
        'team': team,
        'records': queryset,
        'team_id': team_id,
    })


def export_fitness_excel(request, team_id):
    queryset = FitnessPlan.objects.filter(team_id=team_id).select_related('team')
    df = pd.DataFrame(list(queryset.values('date', 'team__name', 'focus_area', 'objective', 'week_number', 'comments')))
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Fitness Plan')
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="fitness_team_{team_id}.xlsx"'
    return response


def export_fitness_pdf(request, team_id):
    queryset = FitnessPlan.objects.filter(team_id=team_id).select_related('team')
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    y = 780
    p.setFont("Helvetica-Bold", 14)
    p.drawString(200, y, f"Fitness Plan Reports - Team {team_id}")
    y -= 40
    p.setFont("Helvetica", 10)
    for r in queryset:
        if y < 100:
            p.showPage()
            y = 780
            p.setFont("Helvetica", 10)
        p.drawString(50, y, f"{r.date} | {r.team.name} | {r.focus_area} | Week {r.week_number}")
        y -= 20
    p.save()
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="fitness_team_{team_id}.pdf"'
    return response

