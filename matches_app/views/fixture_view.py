from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.db.models import Q
from datetime import date

from teams_app.models import Team, AgeGroup
from lineup_app.models import MatchLineup
from matches_app.models import Match, Competition
from matches_app.views.get_match_goals import get_match_goals
from tagging_app.utils.attempt_to_goal_utils import get_match_full_context


@login_required
def fixtures_view(request, team):
    # Get AgeGroup and our teams
    age_group = AgeGroup.objects.get(code=team)
    our_teams = Team.objects.filter(age_group=age_group)

    # Competition filter from GET
    competition_selected = request.GET.get("competition", "all")

    upcoming_matches = Match.objects.filter(date__gte=date.today())

    if competition_selected != "all":
        try:
            competition_id = int(competition_selected)
            upcoming_matches = upcoming_matches.filter(competition_id=competition_id)
        except ValueError:
            # If invalid competition ID, return empty queryset
            upcoming_matches = Match.objects.none()

    # Prefetch related fields
    upcoming_matches = upcoming_matches.select_related(
        "competition", "home_team", "away_team", "venue"
    ).order_by("date")

    # Process each match
    for match in upcoming_matches:
        # Get match goals
        match.home_goals, match.away_goals = get_match_goals(match)

        # Determine "our team" for this match
        our_team_obj = None
        if match.home_team in our_teams:
            our_team_obj = match.home_team
        elif match.away_team in our_teams:
            our_team_obj = match.away_team

        if our_team_obj:
            match.our_team_id = our_team_obj.id
            match.has_lineup = MatchLineup.objects.filter(
                match=match, team=our_team_obj
            ).exists()

            # Get detailed context for FULL REPORT
            context_data = get_match_full_context(match.id, our_team_obj.id)
            match.our_team_goals = context_data["our_team"]["aggregate"]["attempts"]["total_goals"]
            match.opponent_goals = context_data["opponent_team"]["aggregate"]["attempts"]["total_goals"]
        else:
            # No team belongs to our age group
            match.our_team_id = None
            match.has_lineup = False
            match.our_team_goals = None
            match.opponent_goals = None

    # Competition dropdown options
    competition_choices = Competition.objects.all()

    context = {
        "team": team,
        "upcoming_matches": upcoming_matches,
        "competition_selected": competition_selected,  # string, matches GET param
        "competition_choices": competition_choices,
        "active_tab": "fixtures",
    }

    return render(request, "matches_app/fixtures.html", context)


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
