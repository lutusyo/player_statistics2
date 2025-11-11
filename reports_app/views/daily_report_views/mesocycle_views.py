import io
import pandas as pd
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, FileResponse
from reports_app.models import Mesocycle
from reports_app.forms import ReportFilterForm
from teams_app.models import Team
import zipfile

# ---- View for displaying mesocycle reports ----
def mesocycle_reports(request, team_id):
    team = get_object_or_404(Team, id=team_id)
    form = ReportFilterForm(request.GET or None)
    queryset = Mesocycle.objects.filter(team_id=team_id).select_related('team')

    if form.is_valid():
        selected_team = form.cleaned_data.get('team')
        if selected_team:
            queryset = queryset.filter(team=selected_team)

    # Get the latest mesocycle for the top download button
    latest_mesocycle = queryset.order_by('-uploaded_at').first()

    return render(request, 'reports_app/daily_report_templates/4mesocycle/mesocycle_reports.html', {
        'form': form,
        'team': team,
        'records': queryset,
        'team_id': team_id,
        'latest_mesocycle': latest_mesocycle,  # Pass the latest mesocycle
    })


# ---- Export to Excel ----
def export_mesocycle_excel(request, team_id):
    queryset = Mesocycle.objects.filter(team_id=team_id).select_related('team')
    df = pd.DataFrame(list(queryset.values(
        'title', 'team__name', 'start_date', 'end_date', 'uploaded_at'
    )))
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Mesocycles')
    buffer.seek(0)
    response = HttpResponse(
        buffer, 
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="mesocycle_reports.xlsx"'
    return response


# ---- Export uploaded PDF ----
def export_uploaded_mesocycle_pdf(request, mesocycle_id):
    mesocycle = get_object_or_404(Mesocycle, id=mesocycle_id)
    if mesocycle.pdf:
        response = FileResponse(mesocycle.pdf.open('rb'), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{mesocycle.title}.pdf"'
        return response
    else:
        return HttpResponse("No PDF file uploaded for this mesocycle.", status=404)


# ---- Export all PDFs as ZIP ----
def export_all_mesocycle_pdfs(request, team_id):
    team = get_object_or_404(Team, id=team_id)
    mesocycles = Mesocycle.objects.filter(team=team_id)

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w') as zf:
        for m in mesocycles:
            if m.pdf:
                pdf_file = m.pdf.open('rb')
                filename = f"{m.title.replace(' ', '_')}.pdf"
                zf.writestr(filename, pdf_file.read())
                pdf_file.close()

    zip_buffer.seek(0)
    response = HttpResponse(zip_buffer, content_type='application/zip')
    response['Content-Disposition'] = f'attachment; filename="{team.name}_mesocycles.zip"'
    return response
