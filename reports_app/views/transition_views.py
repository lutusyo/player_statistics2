import io
import pandas as pd
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from reports_app.models import Transition
from reports_app.forms import ReportFilterForm
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from teams_app.models import Team


def transition_reports(request, team_id):
    team = get_object_or_404(Team, id=team_id)
    form = ReportFilterForm(request.GET or None)
    queryset = Transition.objects.filter(squad_id=team_id).select_related('name', 'squad')

    if form.is_valid():
        team = form.cleaned_data.get('team')
        if team:
            queryset = queryset.filter(squad=team)

    return render(request, 'reports_app/7transition/transition_reports.html', 
                  {'form': form, 'records': queryset, 'team': team, 'team_id': team_id})


def export_transition_excel(request):
    queryset = Transition.objects.all().select_related('name', 'squad')
    df = pd.DataFrame(list(queryset.values('name__name', 'squad__name', 'played_for', 'activity', 'comments', 'date')))
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Transition Reports')
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="transition_reports.xlsx"'
    return response


def export_transition_pdf(request):
    queryset = Transition.objects.all().select_related('name', 'squad')
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    y = 780
    p.setFont("Helvetica-Bold", 14)
    p.drawString(200, y, "Transition Reports")
    y -= 40
    p.setFont("Helvetica", 10)
    for r in queryset:
        if y < 100:
            p.showPage()
            y = 780
            p.setFont("Helvetica", 10)
        p.drawString(50, y, f"{r.name.name} | {r.squad.name} | {r.activity} | {r.played_for}")
        y -= 20
    p.save()
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="transition_reports.pdf"'
    return response
