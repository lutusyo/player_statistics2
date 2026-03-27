from django.shortcuts import render, get_object_or_404
from version1.teams_app.models import Team
from version1.matches_app.models import Match
from version1.tagging_app.services.summary_key_statistics import get_match_summary


def summary_key_statistics_view(request, match_id, return_context=False):
    match = get_object_or_404(Match, id=match_id)
    summary_key_statistics = get_match_summary(match, match.home_team, match.away_team)

    context = {
        "match": match,
        "summary_key_statistics": summary_key_statistics,
    }

    if return_context:
        return context

    return render(request, 'reports_app/match_report_templates/3_match_summary_key_statistics/match_summary_key_statistics.html', context)
