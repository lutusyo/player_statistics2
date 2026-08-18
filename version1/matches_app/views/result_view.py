from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from version1.matches_app.models import Competition

from version1.matches_app.utils.results_utils import get_results_context


@login_required
def results_view(request, team):
    competition_id = request.GET.get("competition", "all")

    date_from = request.GET.get("date_from") or None
    date_to = request.GET.get("date_to") or None

    results = get_results_context(
        team_code=team,
        competition_id=competition_id,
        date_from=date_from,
        date_to=date_to,
    )

    competition_choices = Competition.objects.all()

    context = {
        "team": team,
        "team_selected": team,
        "past_matches": results["past_matches"],

        "competition_selected": competition_id,
        "competition_choices": competition_choices,

        "date_from": date_from,
        "date_to": date_to,

        "active_tab": "results",
    }

    return render(
        request,
        "matches_app/match_results.html",
        context,
    )