from datetime import date

from django.db.models import Q

from version1.teams_app.models import Team, AgeGroup
from version1.matches_app.models import Match, Competition
from version1.lineup_app.models import MatchLineup
from version1.gps_app.models import GPSRecord
from version1.matches_app.utils.match_details_utils import get_match_detail_context


def get_results_context(team_code, competition_id="all", date_from=None, date_to=None):
    age_group = AgeGroup.objects.get(code=team_code)
    our_teams = Team.objects.filter(age_group=age_group)

    past_matches = Match.objects.filter(
        Q(home_team__in=our_teams) |
        Q(away_team__in=our_teams),
        date__lt=date.today(),
    )

    # Competition filter
    if competition_id != "all":
        past_matches = past_matches.filter(
            competition_id=competition_id
        )

    # Date filters
    if date_from:
        past_matches = past_matches.filter(date__gte=date_from)

    if date_to:
        past_matches = past_matches.filter(date__lte=date_to)

    past_matches = past_matches.select_related(
        "competition",
        "home_team",
        "away_team",
        "venue",
    ).order_by("-date")

    for match in past_matches:
        match.has_lineup = MatchLineup.objects.filter(
            match=match
        ).exists()

        match.has_gps_data = GPSRecord.objects.filter(
            match=match
        ).exists()

        our_team = (
            match.home_team
            if match.home_team in our_teams
            else match.away_team
        )

        match.our_team_id = our_team.id

        detail_context = get_match_detail_context(match)

        if our_team == match.home_team:
            match.our_team_goals = detail_context["home_team_goals"]
            match.opponent_goals = detail_context["away_team_goals"]
        else:
            match.our_team_goals = detail_context["away_team_goals"]
            match.opponent_goals = detail_context["home_team_goals"]

        match.home_lineup_exists = MatchLineup.objects.filter(
            match=match,
            team=match.home_team,
        ).exists()

        match.away_lineup_exists = MatchLineup.objects.filter(
            match=match,
            team=match.away_team,
        ).exists()

    return {
        "age_group": age_group,
        "our_teams": our_teams,
        "past_matches": past_matches,
    }