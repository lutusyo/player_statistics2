from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.db.models import Q
from datetime import date

from teams_app.models import Team, AgeGroup
from lineup_app.models import MatchLineup
from gps_app.models import GPSRecord
from matches_app.models import Match
from matches_app.views.get_match_goals import get_match_goals
from tagging_app.utils.attempt_to_goal_utils import get_match_full_context

from matches_app.utils.match_details_utils import get_match_detail_context

from matches_app.models import Competition


# adjust import path to wherever you saved it


@login_required
def results_view(request, team):
    age_group = AgeGroup.objects.get(code=team)
    our_teams = Team.objects.filter(age_group=age_group)

    # Competition filter
    competition_id = request.GET.get("competition", "all")

    past_matches = Match.objects.filter(
        Q(home_team__in=our_teams) | Q(away_team__in=our_teams),
        date__lt=date.today()
    )

    if competition_id != "all":
        past_matches = past_matches.filter(
            competition_id=competition_id
        )

    past_matches = past_matches.select_related(
        "competition", "home_team", "away_team", "venue"
    ).order_by("-date")

    for match in past_matches:
        match.has_lineup = MatchLineup.objects.filter(match=match).exists()
        match.has_gps_data = GPSRecord.objects.filter(match=match).exists()

        our_team = match.home_team if match.home_team in our_teams else match.away_team
        match.our_team_id = our_team.id

        detail_context = get_match_detail_context(match)
        match.our_team_goals = (
            detail_context["home_team_goals"]
            if our_team == match.home_team
            else detail_context["away_team_goals"]
        )
        match.opponent_goals = (
            detail_context["away_team_goals"]
            if our_team == match.home_team
            else detail_context["home_team_goals"]
        )

        match.home_lineup_exists = MatchLineup.objects.filter(
            match=match, team=match.home_team
        ).exists()
        match.away_lineup_exists = MatchLineup.objects.filter(
            match=match, team=match.away_team
        ).exists()

    competition_choices = Competition.objects.all()

    context = {
        "team": team,
        "team_selected": team,
        "past_matches": past_matches,
        "competition_selected": competition_id,
        "competition_choices": competition_choices,
        "active_tab": "results",
    }

    return render(request, "matches_app/match_results.html", context)







