from django.shortcuts import render, get_object_or_404
from lineup_app.models import Match, MatchLineup, Substitution
from players_app.models import Player

def match_summary_view(request, match_id):
    match = get_object_or_404(Match, id=match_id)

    # Get all lineups for this match
    lineups = MatchLineup.objects.filter(match=match).select_related("player", "team")

    def group_team(team_obj):
        team_lineups = lineups.filter(team=team_obj)

        # Currently on pitch: starting or subbed in but not out
        on_field = team_lineups.filter(time_out__isnull=True).filter(
            Q(is_starting=True) | Q(time_in__isnull=False)
        )

        # Bench players: not starting, not yet subbed in
        on_bench = team_lineups.filter(is_starting=False, time_in__isnull=True)

        # Players already subbed out
        subbed_out = team_lineups.filter(time_out__isnull=False)

        # Players not in lineup at all
        selected_player_ids = team_lineups.values_list("player_id", flat=True)
        not_selected = Player.objects.filter(team=team_obj).exclude(id__in=selected_player_ids)

        return {
            "on_field": on_field,
            "on_bench": on_bench,
            "subbed_out": subbed_out,
            "not_selected": not_selected,
        }

    home_data = group_team(match.home_team)
    away_data = group_team(match.away_team)

    # Substitutions
    substitutions = Substitution.objects.filter(match=match).select_related(
        "player_out__player", "player_in__player"
    ).order_by("minute")

    # Optional: calculate simple scores if needed
    home_score = sum(getattr(p.player, "goals", 0) for p in home_data["on_field"])
    away_score = sum(getattr(p.player, "goals", 0) for p in away_data["on_field"])

    context = {
        "match": match,
        "home_starting": home_data["on_field"],  # includes both starters and subs on field
        "away_starting": away_data["on_field"],
        "home_subs": home_data["on_bench"],
        "away_subs": away_data["on_bench"],
        "home_subbed_out": home_data["subbed_out"],
        "away_subbed_out": away_data["subbed_out"],
        "home_not_selected": home_data["not_selected"],
        "away_not_selected": away_data["not_selected"],
        "substitutions": substitutions,
    }


    return render(request, "reports_app/match_summary.html", context)
