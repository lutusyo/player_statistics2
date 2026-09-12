from django.shortcuts import get_object_or_404, render
from version1.matches_app.models import CompetitionSeason
from datetime import date

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from version1.matches_app.forms import MatchResultForm
from version1.matches_app.models import Match

def competition_season_dashboard(request, competition_season_id):
    competition_season = get_object_or_404(CompetitionSeason, id=competition_season_id, is_active=True,)
    participating_teams = (competition_season.participating_teams.filter(is_active=True).select_related("team", "team__age_group"))

    upcoming_matches = (competition_season.matches
        .filter(date__gte=date.today())
        .select_related("home_team","away_team","venue",)
        .order_by("date", "time")[:5]
    )

    recent_matches = (competition_season.matches
        .filter(date__lt=date.today())
        .select_related("home_team","away_team","venue",)
        .order_by("-date", "-time")[:5]
    )

    context = {
        "competition_season": competition_season,
        "participating_teams": participating_teams,
        "upcoming_matches": upcoming_matches,
        "recent_matches": recent_matches,
    }

    return render(request, "matches_app/competition_season_dashboard.html", context,)




def competition_season_standings(request, competition_season_id):
    competition_season = get_object_or_404(CompetitionSeason, id=competition_season_id, is_active=True,)

    competition_teams = (competition_season.participating_teams
        .filter(is_active=True)
        .select_related("team")
    )

    finished_matches = (competition_season.matches
        .filter(result_status="FINISHED")
        .select_related("home_team", "away_team")
    )

    standings = []

    for entry in competition_teams:
        team = entry.team

        played = 0
        wins = 0
        draws = 0
        losses = 0
        goals_for = 0
        goals_against = 0
        points = 0

        for match in finished_matches:

            # Team played at home
            if match.home_team_id == team.id:

                played += 1
                goals_for += match.home_score
                goals_against += match.away_score

                if match.home_score > match.away_score:
                    wins += 1
                    points += 3

                elif match.home_score == match.away_score:
                    draws += 1
                    points += 1

                else:
                    losses += 1

            # Team played away
            elif match.away_team_id == team.id:

                played += 1
                goals_for += match.away_score
                goals_against += match.home_score

                if match.away_score > match.home_score:
                    wins += 1
                    points += 3

                elif match.away_score == match.home_score:
                    draws += 1
                    points += 1

                else:
                    losses += 1

        goal_difference = goals_for - goals_against

        standings.append({
            "team": team,
            "played": played,
            "wins": wins,
            "draws": draws,
            "losses": losses,
            "goals_for": goals_for,
            "goals_against": goals_against,
            "goal_difference": goal_difference,
            "points": points,
        })

    # Sort:
    # 1. Points
    # 2. Goal difference
    # 3. Goals scored
    # 4. Team name
    standings.sort(
        key=lambda x: (
            -x["points"],
            -x["goal_difference"],
            -x["goals_for"],
            x["team"].name.lower(),
        )
    )

    # Add league position
    for position, row in enumerate(standings, start=1):
        row["position"] = position

    context = {
        "competition_season": competition_season,
        "standings": standings,
    }

    return render(request, "matches_app/competition_season_standings.html",context,)



def match_result_update(request, match_id):

    match = get_object_or_404(Match.objects.select_related("home_team", "away_team","competition_season",),id=match_id,)
    if request.method == "POST":

        form = MatchResultForm(request.POST,instance=match,)
        if form.is_valid():
            updated_match = form.save()

            messages.success(request,"Match result updated successfully.")
            if updated_match.competition_season_id:
                return redirect("matches_app:competition_season_standings",
                    competition_season_id=updated_match.competition_season_id,
                )

            return redirect(
                "matches_app:competition_season_dashboard",
                competition_season_id=updated_match.competition_season_id,
            )

    else:

        form = MatchResultForm(instance=match)

    context = {
        "match": match,
        "form": form,
    }

    return render(request, "matches_app/match_result_update.html", context,)







def competition_season_fixtures(request, competition_season_id):
    competition_season = get_object_or_404(
        CompetitionSeason,
        id=competition_season_id,
        is_active=True,
    )

    fixtures = (competition_season.matches
        .filter(result_status__in=["SCHEDULED", "LIVE"],
        )
        .select_related(
            "home_team",
            "away_team",
            "venue",
        )
        .order_by("date", "time")
    )

    context = {
        "competition_season": competition_season,
        "fixtures": fixtures,
    }

    return render(request, "matches_app/competition_season_fixtures.html", context,)


def competition_season_results(request, competition_season_id):
    competition_season = get_object_or_404(CompetitionSeason,
        id=competition_season_id,
        is_active=True,
    )

    results = (competition_season.matches.filter(result_status="FINISHED")
        .select_related("home_team", "away_team", "venue",)
        .order_by("-date", "-time")
    )

    context = {
        "competition_season": competition_season,
        "results": results,
    }

    return render(request, "matches_app/competition_season_results.html", context,)