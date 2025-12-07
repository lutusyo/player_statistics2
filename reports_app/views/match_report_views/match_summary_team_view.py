from django.shortcuts import render, get_object_or_404
from matches_app.models import Match
from lineup_app.models import MatchLineup

def match_lineup_report(request, match_id, return_context=False):
    match = get_object_or_404(Match, id=match_id)

    # HOME TEAM
    home_starting = MatchLineup.objects.filter(match=match, team=match.home_team, is_starting=True).order_by("order")
    home_subs = MatchLineup.objects.filter(match=match, team=match.home_team, is_starting=False).order_by("order")

    # AWAY TEAM
    away_starting = MatchLineup.objects.filter(match=match, team=match.away_team, is_starting=True).order_by("order")
    away_subs = MatchLineup.objects.filter(match=match, team=match.away_team, is_starting=False).order_by("order")

    context = {

        "match": match,
        "home_starting": home_starting,
        "home_subs": home_subs,
        "away_starting": away_starting,
        "away_subs": away_subs,
    }

    if return_context:
        return context

    return render(request, "reports_app/match_report_templates/2_match_summary_team/match_summary_team.html", context)
