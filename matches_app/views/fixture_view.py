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
    # TEAM (Age Group) – still useful for context/title
    age_group = AgeGroup.objects.get(code=team)
    our_teams = Team.objects.filter(age_group=age_group)

    # Competition filter
    competition = request.GET.get("competition", "all")

    # ✅ ALL upcoming matches (no team restriction)
    upcoming_matches = Match.objects.filter(
        date__gte=date.today()
    )

    # Competition filter
    if competition != "all":
        upcoming_matches = upcoming_matches.filter(
            competition_type=competition
        )

    upcoming_matches = upcoming_matches.order_by("date")

    # Optional: annotate only when our team is involved
    for match in upcoming_matches:
        match.home_goals, match.away_goals = get_match_goals(match)

        # Check if match involves our team
        if match.home_team in our_teams or match.away_team in our_teams:
            our_team = (
                match.home_team
                if match.home_team in our_teams
                else match.away_team
            )

            match.our_team_id = our_team.id
            match.has_lineup = MatchLineup.objects.filter(
                match=match,
                team=our_team
            ).exists()

            context_data = get_match_full_context(match.id, our_team.id)
            match.our_team_goals = context_data["our_team"]["aggregate"]["attempts"]["total_goals"]
            match.opponent_goals = context_data["opponent_team"]["aggregate"]["attempts"]["total_goals"]
        else:
            # Matches not involving us
            match.our_team_id = None
            match.has_lineup = False
            match.our_team_goals = None
            match.opponent_goals = None

    competition_choices = [
        c[0] for c in Match._meta.get_field("competition_type").choices
    ]

    context = {
        "team": team,
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


