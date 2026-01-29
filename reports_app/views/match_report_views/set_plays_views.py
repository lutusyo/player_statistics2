from django.shortcuts import render, get_object_or_404
from django.db.models import Count
from matches_app.models import Match
from teams_app.models import Team
from lineup_app.models import MatchLineup
from tagging_app.models import AttemptToGoal, DeliveryTypeChoices, OutcomeChoices
import matplotlib.pyplot as plt
import io
import base64

def setplays_dashboard(request, match_id, return_context=False):
    match = get_object_or_404(Match, id=match_id)

    teams = [match.home_team, match.away_team]
    all_team_contexts = {}

    for team in teams:
        # Match Lineup
        lineup = MatchLineup.objects.filter(match=match, team=team).select_related("player").order_by("order", "player__name")
        players = [entry.player for entry in lineup]

        # Set Play Attempts
        our_attempts = AttemptToGoal.objects.filter(match=match, team=team, is_opponent=False)
        corners = our_attempts.filter(delivery_type=DeliveryTypeChoices.CORNER)
        free_kicks = our_attempts.filter(delivery_type=DeliveryTypeChoices.FREE_KICK)
        penalties = our_attempts.filter(location_tag__iexact='Penalty Spot')
        setplays = corners | free_kicks | penalties

        summary = {
            "total_corners": corners.count(),
            "total_free_kicks": free_kicks.count(),
            "total_penalties": penalties.count(),
            "total_setplays": setplays.count(),
            "goals_from_setplays": setplays.filter(outcome=OutcomeChoices.ON_TARGET_GOAL).count(),
        }

        # Matplotlib Chart
        labels = ['Corners', 'Free Kicks', 'Penalties', 'Goals (Set Plays)']
        values = [summary['total_corners'], summary['total_free_kicks'], summary['total_penalties'], summary['goals_from_setplays']]
        colors = ['#0d6efd', '#198754', '#dc3545', '#ffc107']

        fig, ax = plt.subplots(figsize=(6,4))
        ax.bar(labels, values, color=colors)
        ax.set_ylabel("Number of Events")
        ax.set_title(f"Set Plays Breakdown ({team.name})")
        plt.tight_layout()

        buffer = io.BytesIO()
        fig.savefig(buffer, format='png')
        buffer.seek(0)
        chart_png = base64.b64encode(buffer.getvalue()).decode('utf-8')
        buffer.close()
        plt.close(fig)

        player_summary = setplays.values("player__name", "delivery_type").annotate(total=Count("id")).order_by("player__name", "delivery_type")

        all_team_contexts[team.id] = {
            "team": team,
            "players": players,
            "corners": corners,
            "free_kicks": free_kicks,
            "penalties": penalties,
            "summary": summary,
            "player_summary": player_summary,
            "chart": chart_png,
        }

    context = {
        "match": match,
        "home_team": match.home_team,
        "away_team": match.away_team,
        **all_team_contexts,  # Each team keyed by ID
        "company": "Azam FC Analyst",
    }

    if return_context:
        return context

    return render(request, "reports_app/match_report_templates/7_set_plays/set_plays.html", context)

