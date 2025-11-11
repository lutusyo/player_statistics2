from django.shortcuts import render, get_object_or_404
from teams_app.models import Team
from matches_app.models import Match
from tagging_app.services.summary_key_statistics import get_match_summary


def summary_key_statistics_view(request, match_id, return_context=False):
    match = get_object_or_404(Match, id=match_id)
    summary = get_match_summary(match, match.home_team, match.away_team)

    context = {
        "match": match,
        "summary": summary,
    }

    if return_context:
        return context


    return render(request, "tagging_app/output/summary_key_statistics.html", context)

