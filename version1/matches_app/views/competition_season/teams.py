from django.shortcuts import get_object_or_404, render
from version1.matches_app.models import CompetitionSeason
from datetime import date

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from version1.matches_app.forms import MatchResultForm
from version1.matches_app.models import Match

from django.db.models import Q, Count, Sum
from version1.teams_app.models import StaffMember, TeamSeasonMembership
from version1.matches_app.models import CompetitionTeam, Match



def competition_season_teams(request, competition_season_id):
    competition_season = get_object_or_404(CompetitionSeason, id=competition_season_id, is_active=True,)

    teams = (
        competition_season.participating_teams
        .filter(is_active=True)
        .select_related(
            "team",
            "team__age_group",
            "team__country",
            "team__region",
        )
        .order_by("team__name")
    )

    context = {
        "competition_season": competition_season,
        "teams": teams,
    }

    return render(request, "matches_app/competition_season/competition_season_teams.html", context,)


def competition_season_team_detail(request, competition_season_id, team_id):

    competition_season = get_object_or_404( CompetitionSeason, id=competition_season_id, is_active=True)

    # Make sure this team is registered in this competition season
    competition_team = get_object_or_404( CompetitionTeam.objects.select_related("team"),
        competition_season=competition_season, team_id=team_id, is_active=True
    )

    team = competition_team.team

    # Players registered with this team for the selected season
    players = (
        team.players
        .filter(is_active=True)
        .select_related("age_group")
        .order_by("jersey_number", "name", "second_name", "surname")
    )


    staff_members = (team.staff_members.select_related("age_group").order_by("role", "name"))


    # All matches involving this team in this competition season
    matches = (Match.objects.filter(competition_season=competition_season).filter(
            Q(home_team=team) | Q(away_team=team)
        )
        .select_related("home_team", "away_team", "venue")
        .order_by("date", "time")
    )

    # Calculate statistics using completed matches only
    finished_matches = matches.filter(result_status="FINISHED")

    stats = {
        "played": 0,
        "wins": 0,
        "draws": 0,
        "losses": 0,
        "goals_for": 0,
        "goals_against": 0,
        "goal_difference": 0,
        "points": 0,
    }

    for match in finished_matches:
        if match.home_team_id == team.id:
            goals_for = match.home_score
            goals_against = match.away_score
        else:
            goals_for = match.away_score
            goals_against = match.home_score

        stats["played"] += 1
        stats["goals_for"] += goals_for
        stats["goals_against"] += goals_against

        if goals_for > goals_against:
            stats["wins"] += 1
            stats["points"] += 3
        elif goals_for == goals_against:
            stats["draws"] += 1
            stats["points"] += 1
        else:
            stats["losses"] += 1

    stats["goal_difference"] = (
        stats["goals_for"] - stats["goals_against"]
    )

    # Upcoming and completed matches are available separately
    recent_matches = matches.filter(result_status="FINISHED").order_by("-date", "-time")[:5]
    upcoming_matches = matches.filter( result_status__in=["SCHEDULED", "LIVE", "POSTPONED"]).order_by("date", "time")

    context = {
        "competition_season": competition_season,
        "team": team,
        "players": players,
        "staff_members": staff_members,
        "stats": stats,
        "matches": matches,
        "recent_matches": recent_matches,
        "upcoming_matches": upcoming_matches,
    }

    return render(request, "matches_app/competition_season/team_detail.html", context)