from version1.tagging_app.models import AttemptToGoal
from django.shortcuts import get_object_or_404, render
from version1.matches_app.models import CompetitionSeason
from datetime import date

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from version1.matches_app.forms import MatchResultForm
from version1.matches_app.models import Match


def competition_match_data(request, match_id):

    match = get_object_or_404(Match.objects.select_related("home_team", "away_team", "venue", "competition_season",),id=match_id,)
    attempts = (AttemptToGoal.objects
        .filter(match=match)
        .select_related("player","team", "assist_by", "pre_assist_by", "own_goal_for",)
        .order_by("minute", "second")
    )
    goals = attempts.filter(outcome="On Target Goal")

    context = {
        "match": match,
        "attempts": attempts,
        "goals": goals,
    }

    return render(request, "matches_app/competition_season/match_data.html", context,)