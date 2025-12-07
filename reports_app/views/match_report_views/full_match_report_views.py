from django.shortcuts import render, get_object_or_404
from matches_app.models import Match
# Get all sections’ contexts just like in full_match_report_view
from reports_app.views.match_report_views.post_match_summary_views import full_match_context_view as post_match_summary
from reports_app.views.match_report_views.summary_key_statistics_views import summary_key_statistics_view
from reports_app.views.match_report_views.in_possession_views import attempt_to_goal_dashboard, pass_network_dashboard
from reports_app.views.match_report_views.goalkeeping_view import goalkeeping_view
from reports_app.views.match_report_views.set_plays_views import setplays_dashboard
from reports_app.views.match_report_views.match_summary_team_view import match_lineup_report

from django.http import HttpResponse
from django.template.loader import get_template
from weasyprint import HTML
from io import BytesIO

def full_match_report_view(request, match_id, our_team_id):
    match = get_object_or_404(Match, id=match_id)

    # 1️⃣ Post-match summary
    post_summary_context = post_match_summary(request, match_id, our_team_id, return_context=True)

    # 2 match summary team
    match_summary_team_context = match_lineup_report(request, match_id, return_context=True)

    # 3 Match Summary Key Statistics (no our_team_id here)
    match_summary_key_statistics_context = summary_key_statistics_view(request, match_id, return_context=True)

    # 4 Attempt-to-goal dashboard
    attempt_context = attempt_to_goal_dashboard(request, match_id, return_context=True)

    # Pass network
    pass_context = pass_network_dashboard(request, match_id, return_context=True)

    # 4️⃣ Goalkeeping
    goalkeeping_context = goalkeeping_view(request, match_id, our_team_id, return_context=True)

    # 5️⃣ Set Plays
    setplays_context = setplays_dashboard(request, match_id, our_team_id, return_context=True)

    # 🧩 Merge all contexts into one
    full_context = {
        'match': match,
        'our_team_id': our_team_id,
        **post_summary_context,
        **match_summary_team_context, 
        **match_summary_key_statistics_context,
        **attempt_context,
        **goalkeeping_context,
        **setplays_context,

    }

    return render(
        request,
        'reports_app/match_report_templates/full_match_report/full_match_report.html',
        full_context,
    )




def download_full_report_pdf(request, match_id, our_team_id):
    # ✅ Reuse your context builder
    match = get_object_or_404(Match, id=match_id)



    # Collect contexts
    post_summary_context = post_match_summary(request, match_id, our_team_id, return_context=True)
    match_summary_context = summary_key_statistics_view(request, match_id, return_context=True)
    attempt_context = attempt_to_goal_dashboard(request, match_id, return_context=True)
    goalkeeping_context = goalkeeping_view(request, match_id, our_team_id, return_context=True)
    setplays_context = setplays_dashboard(request, match_id, our_team_id, return_context=True)

    full_context = {
        'match': match,
        'our_team_id': our_team_id,
        **post_summary_context,
        **match_summary_context,
        **attempt_context,
        **goalkeeping_context,
        **setplays_context,
    }

    # ✅ Load template
    template = get_template('reports_app/match_report_templates/full_match_report/full_match_report.html')
    html_content = template.render(full_context)

    # ✅ Generate PDF
    pdf_file = BytesIO()
    HTML(string=html_content, base_url=request.build_absolute_uri()).write_pdf(pdf_file)
    pdf_file.seek(0)

    # ✅ Return as downloadable file
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Match_Report_{match_id}.pdf"'
    return response
