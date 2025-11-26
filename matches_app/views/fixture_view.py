from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.db.models import Q
from datetime import date

from teams_app.models import Team, AgeGroup
from lineup_app.models import MatchLineup
from matches_app.models import Match
from matches_app.views.get_match_goals import get_match_goals
from tagging_app.utils.attempt_to_goal_utils import get_match_full_context


@login_required
def fixtures_view(request, team):
    # TEAM (Age Group)
    age_group = AgeGroup.objects.get(code=team)
    our_teams = Team.objects.filter(age_group=age_group)

    # --- NEW: COMPETITION FILTER ---
    competition = request.GET.get("competition", "all")

    # Base Query
    upcoming_matches = Match.objects.filter(
        Q(home_team__in=our_teams) | Q(away_team__in=our_teams),
        date__gte=date.today()
    )

    # Apply filter only if NOT “all”
    if competition != "all":
        upcoming_matches = upcoming_matches.filter(competition_type=competition)

    upcoming_matches = upcoming_matches.order_by("date")

    # Process each match
    for match in upcoming_matches:
        match.home_goals, match.away_goals = get_match_goals(match)
        match.has_lineup = MatchLineup.objects.filter(match=match, team__in=our_teams).exists()

        our_team = match.home_team if match.home_team in our_teams else match.away_team
        match.our_team_id = our_team.id if our_team else None

        context_data = get_match_full_context(match.id, our_team.id)
        match.our_team_goals = context_data["our_team"]["aggregate"]["attempts"]["total_goals"]
        match.opponent_goals = context_data["opponent_team"]["aggregate"]["attempts"]["total_goals"]

    # --- SEND COMPETITION LIST FOR DROPDOWN ---
    competition_choices = [c[0] for c in Match._meta.get_field("competition_type").choices]

    context = {
        "team": team,
        "team_selected": team,
        "upcoming_matches": upcoming_matches,
        "competition_selected": competition,
        "competition_choices": competition_choices,
        "active_tab": "fixtures",
    }
    return render(request, "matches_app/fixtures.html", context)


from django.shortcuts import render
from matches_app.models import Match

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


