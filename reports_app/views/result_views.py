import io
import pandas as pd
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from reports_app.models import Result
from reports_app.forms import ReportFilterForm
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from teams_app.models import Team

# ---- Display result reports ----
def result_reports(request, team_id):
    team = get_object_or_404(Team, id=team_id)
    form = ReportFilterForm(request.GET or None)
    queryset = Result.objects.filter(our_team_id=team_id).select_related('home_team', 'away_team', 'our_team')

    if form.is_valid():
        team = form.cleaned_data.get('team')
        if team:
            queryset = queryset.filter(our_team=team)

    return render(request, 'reports_app/8results/result_reports.html', {
        'form': form,
        'team': team,
        'records': queryset,
        'team_id': team_id,
    })


# ---- Export to Excel ----
def export_result_excel(request, team_id):
    queryset = Result.objects.filter(our_team_id=team_id).select_related('home_team', 'away_team', 'our_team')
    df = pd.DataFrame(list(queryset.values(
        'date', 'venue', 'competition', 'home_team__name', 'home_score',
        'away_score', 'away_team__name', 'result', 'goal_scorers',
        'our_team__name', 'notes'
    )))
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Results')
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="results.xlsx"'
    return response


# ---- Export to PDF ----
def export_result_pdf(request, team_id):
    queryset = Result.objects.filter(our_team_id=team_id).select_related('home_team', 'away_team', 'our_team')
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    y = 780
    p.setFont("Helvetica-Bold", 14)
    p.drawString(200, y, "Match Results")
    y -= 40
    p.setFont("Helvetica", 10)
    for r in queryset:
        if y < 100:
            p.showPage()
            y = 780
            p.setFont("Helvetica", 10)
        p.drawString(50, y, f"{r.date} | {r.home_team.name} {r.home_score}-{r.away_score} {r.away_team.name} | {r.result}")
        y -= 20
    p.save()
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="results.pdf"'
    return response
