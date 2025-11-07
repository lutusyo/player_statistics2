from django.shortcuts import render, get_object_or_404
from matches_app.models import Match
from reports_app.views.match_report_views.post_match_summary_views import full_match_context_view as post_match_summary
from reports_app.views.match_report_views.in_possession_views import attempt_to_goal_dashboard
from reports_app.views.match_report_views.goalkeeping_view import goalkeeping_view
from reports_app.views.match_report_views.set_plays_views import setplays_dashboard

def full_match_report_view(request, match_id, our_team_id):
    match = get_object_or_404(Match, id=match_id)

    # 1️⃣ Post-match summary
    post_summary_context = post_match_summary(request, match_id, our_team_id, return_context=True)

    # 2️⃣ Attempt-to-goal dashboard
    attempt_context = attempt_to_goal_dashboard(request, match_id, return_context=True)

    # 3️⃣ Goalkeeping
    goalkeeping_context = goalkeeping_view(request, match_id, our_team_id, return_context=True)

    # 4️⃣ Set Plays
    setplays_context = setplays_dashboard(request, match_id, our_team_id, return_context=True)

    # Merge all contexts into one
    full_context = {
        'match': match,
        **post_summary_context,
        **attempt_context,
        **goalkeeping_context,
        **setplays_context,
    }

    return render(request, 'reports_app/match_report_templates/full_match_report/full_match_report.html', full_context)
