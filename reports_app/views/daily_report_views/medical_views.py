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

# ---- Export to PDF ----
import datetime
from django.template.loader import render_to_string
from weasyprint import HTML, CSS

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




def export_medical_pdf(request, team_id):

    team = get_object_or_404(Team, id=team_id)
    queryset = Medical.objects.filter(squad_id=team_id).select_related('name', 'squad')

    context = {
        'team': team,                            # Team info (name, category, logo)
        'records': queryset,                     # All medical records for that team
        'generated_on': timezone.now(),          # Current timestamp for the footer
        'title': "Medical Report Summary",       # PDF report title
    }

    # 🔹 Render the HTML template into a string using the provided context
    # This creates the HTML that will be converted into a PDF
    html_string = render_to_string('reports_app/daily_report_templates/1medical/medical_report_pdf.html', context)

    # 🔹 Create an in-memory file buffer to temporarily store the generated PDF
    pdf_file = io.BytesIO()

    # 🔹 Generate the PDF with WeasyPrint
    # `HTML()` takes the rendered HTML string and a base URL for resolving image paths (like logos)
    # `.write_pdf()` converts the HTML into a PDF and applies the given CSS styling
    HTML(string=html_string, base_url=request.build_absolute_uri()).write_pdf(pdf_file, stylesheets=[
        CSS(string="""
            /* ========== PAGE & FONT SETTINGS ========== */
            @page { size: A4; margin: 1.5cm; }
            body { font-family: 'Helvetica', sans-serif; font-size: 11px; color: #222; }

            /* ========== TITLES ========== */
            h1 { text-align: center; font-size: 18px; margin-bottom: 10px; }
            h2 { text-align: center; font-size: 14px; color: #555; margin-top: -10px; }

            /* ========== TABLE STYLE ========== */
            table { width: 100%; border-collapse: collapse; margin-top: 20px; }
            th, td { border: 1px solid #999; padding: 6px; text-align: left; }
            th { background-color: #f0f0f0; font-weight: bold; }
            tr:nth-child(even) { background-color: #f9f9f9; }

            /* ========== FOOTER STYLE ========== */
            footer {
                position: fixed; bottom: 0; left: 0; right: 0;
                text-align: center; font-size: 9px; color: #555;
            }

            /* ========== HEADER LAYOUT ========== */
            .header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 10px;
            }
            .logo { height: 70px; }
            .info { text-align: right; font-size: 12px; }
        """)
    ])

    # 🔹 Move the pointer to the start of the buffer before returning it
    pdf_file.seek(0)

    # 🔹 Create an HTTP response with the PDF content type
    response = HttpResponse(pdf_file, content_type='application/pdf')

    # 🔹 Set filename and force browser to download the file
    response['Content-Disposition'] = f'attachment; filename="medical_report_{team.name}.pdf"'

    # 🔹 Return the generated PDF as the HTTP response
    return response


