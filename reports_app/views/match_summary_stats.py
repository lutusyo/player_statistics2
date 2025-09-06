from django.shortcuts import render, get_object_or_404
from matches_app.models import Match
from teams_app.models import Team
from tagging_app.utils.attempt_to_goal_utils import get_match_full_context  # 👈 move utility here (or keep in tagging_app.utils)

def match_summary_stats_view(request, match_id, our_team_id):
    match = get_object_or_404(Match, id=match_id)
    context_data = get_match_full_context(match_id, our_team_id)

    # Extract
    our_team_data = context_data["our_team"]["aggregate"]
    opponent_team_data = context_data["opponent_team"]["aggregate"]

    home_team = match.home_team
    away_team = match.away_team

    # Decide who is "home" in this view context
    if home_team.id == our_team_id:
        home_stats = our_team_data
        away_stats = opponent_team_data
    else:
        home_stats = opponent_team_data
        away_stats = our_team_data

    # Scores = total goals
    home_score = home_stats["attempts"]["total_goals"]
    away_score = away_stats["attempts"]["total_goals"]

    # Possession proxy = passes completed (you can later improve with real tracking)
    total_passes = home_stats["passes"]["total_passes"] + away_stats["passes"]["total_passes"]
    if total_passes > 0:
        possession_home_pct = round((home_stats["passes"]["total_passes"] / total_passes) * 100, 1)
        possession_away_pct = round((away_stats["passes"]["total_passes"] / total_passes) * 100, 1)
    else:
        possession_home_pct, possession_away_pct = 50, 50

    context = {
        "match": match,
        "home": home_team,
        "away": away_team,
        "home_score": home_score,
        "away_score": away_score,
        "possession_home_pct": possession_home_pct,
        "possession_away_pct": possession_away_pct,
        "home_stats": home_stats,
        "away_stats": away_stats,
        "company": "Azam Fc Analyst",
        "competition": match.competition_type,
        "venue": match.venue,
        "date": match.date,
        "kickoff_time": match.time,
        "season": match.season,
        "match_number": getattr(match, "match_number", None),
        "result": f"{home_score} - {away_score}",
    }

    return render(request, "reports_app/contents_pages/match_summary_stats.html", context)
