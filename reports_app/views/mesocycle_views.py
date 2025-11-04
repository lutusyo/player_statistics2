import io
import pandas as pd
from django.shortcuts import render
from django.http import HttpResponse
from django.utils import timezone
from reports_app.models import Mesocycle
from reports_app.forms import ReportFilterForm
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


def mesocycle_reports(request):
    form = ReportFilterForm(request.GET or None)
    queryset = Mesocycle.objects.all().select_related('team')

    if form.is_valid():
        team = form.cleaned_data.get('team')
        if team:
            queryset = queryset.filter(team=team)

    return render(request, 'reports_app/4mesocycle/mesocycle_reports.html', {'form': form, 'records': queryset})


def export_mesocycle_excel(request):
    queryset = Mesocycle.objects.all().select_related('team')
    df = pd.DataFrame(list(queryset.values('title', 'team__name', 'start_date', 'end_date', 'uploaded_at')))
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Mesocycles')
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="mesocycle_reports.xlsx"'
    return response


def export_mesocycle_pdf(request):
    queryset = Mesocycle.objects.all().select_related('team')
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    y = 780
    p.setFont("Helvetica-Bold", 14)
    p.drawString(200, y, "Mesocycle Reports")
    y -= 40
    p.setFont("Helvetica", 10)
    for r in queryset:
        if y < 100:
            p.showPage()
            y = 780
            p.setFont("Helvetica", 10)
        p.drawString(50, y, f"{r.title} | {r.team.name} | {r.start_date} → {r.end_date}")
        y -= 20
    p.save()
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="mesocycle_reports.pdf"'
    return response
