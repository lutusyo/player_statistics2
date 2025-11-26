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

# adjust import path to wherever you saved it

@login_required
def results_view(request, team):
    age_group = AgeGroup.objects.get(code=team)
    our_teams = Team.objects.filter(age_group=age_group)

    # --- NEW: COMPETITION FILTER ---
    competition = request.GET.get("competition", "all")

    # Base Query
    past_matches = Match.objects.filter(
        Q(home_team__in=our_teams) | Q(away_team__in=our_teams),
        date__lt=date.today()
    )

    # Apply competition filter
    if competition != "all":
        past_matches = past_matches.filter(competition_type=competition)

    past_matches = past_matches.order_by("-date")

    # Process matches
    for match in past_matches:
        match.has_lineup = MatchLineup.objects.filter(match=match).exists()
        match.has_gps_data = GPSRecord.objects.filter(match=match).exists()

        our_team = match.home_team if match.home_team in our_teams else match.away_team
        match.our_team_id = our_team.id

        detail_context = get_match_detail_context(match)
        match.our_team_goals = (
            detail_context["home_team_goals"] if our_team == match.home_team 
            else detail_context["away_team_goals"]
        )
        match.opponent_goals = (
            detail_context["away_team_goals"] if our_team == match.home_team 
            else detail_context["home_team_goals"]
        )

        match.home_lineup_exists = MatchLineup.objects.filter(match=match, team=match.home_team).exists()
        match.away_lineup_exists = MatchLineup.objects.filter(match=match, team=match.away_team).exists()

    # --- SEND COMPETITION LIST FOR DROPDOWN ---
    competition_choices = [c[0] for c in Match._meta.get_field("competition_type").choices]

    context = {
        "team": team,
        "team_selected": team,
        "past_matches": past_matches,
        "competition_selected": competition,
        "competition_choices": competition_choices,
        "active_tab": "results",
    }
    return render(request, "matches_app/match_results.html", context)


@login_required
def results_by_competition(request, team, competition):
    age_group = AgeGroup.objects.get(code=team)
    our_teams = Team.objects.filter(age_group=age_group)

    # Filter by competition type
    past_matches = Match.objects.filter(
        Q(home_team__in=our_teams) | Q(away_team__in=our_teams),
        date__lt=date.today(),
        competition_type=competition
    ).order_by("-date")

    for match in past_matches:
        match.has_lineup = MatchLineup.objects.filter(match=match).exists()
        match.has_gps_data = GPSRecord.objects.filter(match=match).exists()

        # Determine our team
        our_team = match.home_team if match.home_team in our_teams else match.away_team
        match.our_team_id = our_team.id

        # Goals (uses your existing function)
        detail_context = get_match_detail_context(match)
        match.our_team_goals = (
            detail_context["home_team_goals"] if our_team == match.home_team 
            else detail_context["away_team_goals"]
        )
        match.opponent_goals = (
            detail_context["away_team_goals"] if our_team == match.home_team 
            else detail_context["home_team_goals"]
        )

        # Lineups
        match.home_lineup_exists = MatchLineup.objects.filter(match=match, team=match.home_team).exists()
        match.away_lineup_exists = MatchLineup.objects.filter(match=match, team=match.away_team).exists()

    context = {
        "team": team,
        "team_selected": team,
        "past_matches": past_matches,
        "competition": competition,
        "active_tab": "results",
    }

    return render(request, "matches_app/match_results.html", context)





