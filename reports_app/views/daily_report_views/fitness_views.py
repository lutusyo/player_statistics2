import io
import pandas as pd
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from reports_app.models import FitnessPlan
from reports_app.forms import ReportFilterForm
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from teams_app.models import Team

import zipfile
from django.http import  FileResponse




def fitness_reports(request, team_id):
    team = get_object_or_404(Team, id=team_id)
    form = ReportFilterForm(request.GET or None)

    queryset = FitnessPlan.objects.filter(team_id=team_id).select_related('team')

    if form.is_valid():
        selected_team = form.cleaned_data.get('team')
        if selected_team:
            queryset = queryset.filter(team=selected_team)

    latest_fitness_plan = queryset.order_by('-uploaded_at').first()

    return render(
        request,
        'reports_app/daily_report_templates/5fitness/fitness_reports.html',
        {
            'form': form,
            'team': team,
            'records': queryset,
            'team_id': team_id,
            'latest_fitness_plan': latest_fitness_plan,
        }
    )



def export_fitness_excel(request, team_id):
    queryset = FitnessPlan.objects.filter(team_id=team_id).select_related('team')

    df = pd.DataFrame(
        list(
            queryset.values(
                'title',
                'team__name',
                'start_date',
                'end_date',
                'uploaded_at'
            )
        )
    )

    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Fitness Plans')

    buffer.seek(0)
    response = HttpResponse(
        buffer,
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="fitness_plans.xlsx"'
    return response



def export_fitness_pdf(request, fitness_id):
    fitness = get_object_or_404(FitnessPlan, id=fitness_id)

    if fitness.pdf:
        response = FileResponse(
            fitness.pdf.open('rb'),
            content_type='application/pdf'
        )
        response['Content-Disposition'] = (
            f'attachment; filename="{fitness.title}.pdf"'
        )
        return response

    return HttpResponse(
        "No PDF file uploaded for this fitness plan.",
        status=404
    )

def export_all_fitness_pdfs(request, team_id):
    team = get_object_or_404(Team, id=team_id)
    fitness_plans = FitnessPlan.objects.filter(team=team_id)

    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, 'w') as zf:
        for f in fitness_plans:
            if f.pdf:
                pdf_file = f.pdf.open('rb')
                filename = f"{f.title.replace(' ', '_')}.pdf"
                zf.writestr(filename, pdf_file.read())
                pdf_file.close()

    zip_buffer.seek(0)
    response = HttpResponse(zip_buffer, content_type='application/zip')
    response['Content-Disposition'] = (
        f'attachment; filename="{team.name}_fitness_plans.zip"'
    )
    return response




