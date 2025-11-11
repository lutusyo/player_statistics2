import io
import pandas as pd
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from reports_app.models import IndividualActionPlan
from reports_app.forms import ReportFilterForm
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from teams_app.models import Team


def iap_reports(request, team_id):
    team = get_object_or_404(Team, id=team_id)
    form = ReportFilterForm(request.GET or None)
    queryset = IndividualActionPlan.objects.filter(squad_id=team_id).select_related('name', 'squad')

    if form.is_valid():
        team = form.cleaned_data.get('team')
        if team:
            queryset = queryset.filter(squad=team)

    context = {
        'form': form,
        'team': team,
        'records': queryset,
        'team_id': team_id,  # 👈 so you can reuse in template links
    }

    return render(request, 'reports_app/daily_report_templates/6iap/iap_reports.html', context)


def export_iap_excel(request, team_id):
    queryset = IndividualActionPlan.objects.filter(squad_id=team_id).select_related('name', 'squad')
    df = pd.DataFrame(list(queryset.values(
        'date', 'name__name', 'category', 'responsibility', 'action', 'status', 'squad__name'
    )))
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='IAP Reports')
    buffer.seek(0)
    response = HttpResponse(
        buffer,
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="iap_reports_team_{team_id}.xlsx"'
    return response


def export_iap_pdf(request, team_id):
    queryset = IndividualActionPlan.objects.filter(squad_id=team_id).select_related('name', 'squad')
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    y = 780
    p.setFont("Helvetica-Bold", 14)
    p.drawString(180, y, f"Individual Action Plan Reports - Team {team_id}")
    y -= 40
    p.setFont("Helvetica", 10)

    for r in queryset:
        if y < 100:
            p.showPage()
            y = 780
            p.setFont("Helvetica", 10)
        p.drawString(50, y, f"{r.date} | {r.name.name} | {r.category} | {r.status}")
        y -= 20

    p.save()
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="iap_reports_team_{team_id}.pdf"'
    return response
