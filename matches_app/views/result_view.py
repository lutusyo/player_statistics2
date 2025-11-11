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
    #our_teams = Team.objects.filter(age_group=age_group, team_type="OUR_TEAM")

    past_matches = Match.objects.filter(
        Q(home_team__in=our_teams) | Q(away_team__in=our_teams),
        date__lt=date.today()
    ).order_by("-date")

    past_matches = [m for m in past_matches if m.home_team in our_teams or m.away_team in our_teams]

    for match in past_matches:
        match.has_lineup = MatchLineup.objects.filter(match=match).exists()
        match.has_gps_data = GPSRecord.objects.filter(match=match).exists()

        if match.home_team in our_teams:
            our_team = match.home_team
        else:
            our_team = match.away_team

        match.our_team_id = our_team.id

    
        # Use the updated detail context
        detail_context = get_match_detail_context(match)
        match.our_team_goals = detail_context["home_team_goals"] if our_team == match.home_team else detail_context["away_team_goals"]
        match.opponent_goals = detail_context["away_team_goals"] if our_team == match.home_team else detail_context["home_team_goals"]

    for match in past_matches:
        match.home_lineup_exists = MatchLineup.objects.filter(match=match, team=match.home_team).exists()
        match.away_lineup_exists = MatchLineup.objects.filter(match=match, team=match.away_team).exists()


    context = {
        "team": team,
        "team_selected": team,
        "past_matches": past_matches,
        "active_tab": "results",
        
    }
    return render(request, "matches_app/match_results.html", context)




