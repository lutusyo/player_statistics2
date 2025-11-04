import io
import pandas as pd
from django.shortcuts import render
from django.http import HttpResponse
from django.utils import timezone
from reports_app.models import Performance
from reports_app.forms import ReportFilterForm
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


def performance_reports(request):
    form = ReportFilterForm(request.GET or None)
    queryset = Performance.objects.all().select_related('squad')

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

    return render(request, 'reports_app/3performance/performance_reports.html', {'form': form, 'records': queryset})


def export_performance_excel(request):
    queryset = Performance.objects.all().select_related('squad')
    df = pd.DataFrame(list(queryset.values('date', 'squad__name', 'activity', 'comments')))
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Performance')
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="performance_reports.xlsx"'
    return response


def export_performance_pdf(request):
    queryset = Performance.objects.all().select_related('squad')
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    y = height - 50
    p.setFont("Helvetica-Bold", 14)
    p.drawString(200, y, "Performance Reports")
    y -= 40
    p.setFont("Helvetica", 10)
    for r in queryset:
        if y < 100:
            p.showPage()
            y = height - 50
            p.setFont("Helvetica", 10)
        p.drawString(50, y, f"{r.date} | {r.squad.name} | {r.activity} | {r.comments}")
        y -= 20
    p.save()
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="performance_reports.pdf"'
    return response
