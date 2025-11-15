import io
from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML, CSS
from django.shortcuts import get_object_or_404
from gps_app.models import GPSRecord
from matches_app.models import Match

def export_gps_dashboard_pdf(request, match_id):
    match = get_object_or_404(Match, id=match_id)
    gps_records = GPSRecord.objects.filter(match=match)

    # Optional: pre-generate chart images (from frontend, sent via POST or stored)
    # For now, assume charts are skipped or replaced with static placeholders

    html_string = render_to_string('gps_dashboard_pdf.html', {
        'match': match,
        'gps_records': gps_records,

    })

    html = HTML(string=html_string, base_url=request.build_absolute_uri())
    pdf_file = html.write_pdf(stylesheets=[CSS(string='body { font-family: Arial;}')])

    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="GPS_Dashboard_{match}.pdf"'
    return response

