from django.shortcuts import render, get_object_or_404
from matches_app.models import Match

def table_of_contents_view(request, match_id, our_team_id):
    match = get_object_or_404(Match, id=match_id)

    context = {
        "match": match,
        "company": "Azam Fc Analyst",
        "competition": match.competition_type,
        "venue": match.venue,
        "date": match.date,
        "kickoff_time": match.time,
        "season": match.season,
        "match_number": getattr(match, 'match_number', None),
    }
    return render(request, "tagging_app/reports/table_of_contents.html", context)
