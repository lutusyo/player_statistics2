from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.db.models import Q
from datetime import date

from version1.teams_app.models import Team, AgeGroup
from version1.lineup_app.models import MatchLineup
from version1.matches_app.models import Match, Competition
from version1.matches_app.views.get_match_goals import get_match_goals
from version1.tagging_app.utils.attempt_to_goal_utils import get_match_full_context


@login_required
def fixtures_view(request, team):

    # Age group + teams
    age_group = AgeGroup.objects.get(code=team)
    our_teams = Team.objects.filter(age_group=age_group)

    # Competition filter
    competition_selected = request.GET.get("competition", "all")

    # ONLY upcoming matches for this age group
    upcoming_matches = Match.objects.filter(
        Q(home_team__in=our_teams) |
        Q(away_team__in=our_teams),
        date__gte=date.today()
    )

    # Competition filtering
    if competition_selected != "all":
        upcoming_matches = upcoming_matches.filter(
            competition_id=competition_selected
        )

    # Related objects
    upcoming_matches = upcoming_matches.select_related(
        "competition",
        "home_team",
        "away_team",
        "venue"
    ).order_by("date", "time")

    # Match processing
    for match in upcoming_matches:

        match.home_goals, match.away_goals = get_match_goals(match)

        # Detect our team
        our_team_obj = (
            match.home_team
            if match.home_team in our_teams
            else match.away_team
        )

        match.our_team_id = our_team_obj.id

        match.has_lineup = MatchLineup.objects.filter(
            match=match,
            team=our_team_obj
        ).exists()

        context_data = get_match_full_context(
            match.id,
            our_team_obj.id
        )

        match.our_team_goals = context_data[
            "our_team"
        ]["aggregate"]["attempts"]["total_goals"]

        match.opponent_goals = context_data[
            "opponent_team"
        ]["aggregate"]["attempts"]["total_goals"]

    # Competition choices
    competition_choices = Competition.objects.all()

    context = {
        "team": team,
        "team_selected": team,
        "upcoming_matches": upcoming_matches,
        "competition_selected": competition_selected,
        "competition_choices": competition_choices,
        "active_tab": "fixtures",
    }

    return render(
        request,
        "matches_app/fixtures.html",
        context
    )


# Optional: your fixtures_by_competition view (if needed)
def fixtures_by_competition(request, team, competition):
    fixtures = Match.objects.filter(
        team__name=team,
        competition_type=competition,
        match_type="fixture"
    ).order_by("date")

    context = {
        "team": team,
        "competition": competition,
        "fixtures": fixtures,
    }
    return render(request, "matches_app/fixtures_by_competition.html", context)
