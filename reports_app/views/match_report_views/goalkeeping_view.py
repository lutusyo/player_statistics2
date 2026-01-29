from django.shortcuts import render, get_object_or_404
from matches_app.models import Match
from tagging_app.models import AttemptToGoal
import matplotlib.pyplot as plt
import numpy as np
import base64
from io import BytesIO

def goalkeeping_view(request, match_id, return_context=False):
    match = get_object_or_404(Match, id=match_id)

    team_a = match.home_team
    team_b = match.away_team

    def get_team_stats(team, opponent):
        # Basic attempt counts
        total_attempts = AttemptToGoal.objects.filter(match=match, team=team).count()

        on_target_made = AttemptToGoal.objects.filter(
            match=match, team=team,
            outcome__in=['On Target Saved', 'On Target Goal']
        ).count()

        on_target_goal_made = AttemptToGoal.objects.filter(
            match=match, team=team, outcome='On Target Goal'
        ).count()

        off_target_made = AttemptToGoal.objects.filter(
            match=match, team=team, outcome='Off Target'
        ).count()

        blocked_shot_made = AttemptToGoal.objects.filter(
            match=match, team=team, outcome='Blocked'
        ).count()

        player_error_made = AttemptToGoal.objects.filter(
            match=match, team=team, outcome='Player Error'
        ).count()

        own_goal_made = AttemptToGoal.objects.filter(
            match=match, team=team, outcome='Own Goal'
        ).count()

        # Faced attempts
        total_faced = AttemptToGoal.objects.filter(match=match, team=opponent).count()

        on_target_faced = AttemptToGoal.objects.filter(
            match=match, team=opponent,
            outcome__in=['On Target Saved', 'On Target Goal']
        ).count()

        blocked_shot_faced = AttemptToGoal.objects.filter(
            match=match, team=opponent, outcome='Blocked'
        ).count()

        off_target_faced = AttemptToGoal.objects.filter(
            match=match, team=opponent, outcome='Off Target'
        ).count()

        player_error_faced = AttemptToGoal.objects.filter(
            match=match, team=opponent, outcome='Player Error'
        ).count()

        on_target_saved = AttemptToGoal.objects.filter(
            match=match, team=opponent, outcome='On Target Saved'
        ).count()

        on_target_goal_conceded = AttemptToGoal.objects.filter(
            match=match, team=opponent, outcome='On Target Goal'
        ).count()

        save_percentage = round((on_target_saved / on_target_faced) * 100, 1) if on_target_faced else 0
        clean_sheet = "YES" if on_target_goal_conceded == 0 else "NO"

        return {
            "team": team,
            "total_attempts": total_attempts,
            "on_target_made": on_target_made,
            "on_target_goal_made": on_target_goal_made,
            "off_target_made": off_target_made,
            "blocked_shot_made": blocked_shot_made,
            "player_error_made": player_error_made,
            "own_goal_made": own_goal_made,
            "total_faced": total_faced,
            "on_target_faced": on_target_faced,
            "off_target_faced": off_target_faced,
            "blocked_shot_faced": blocked_shot_faced,
            "player_error_faced": player_error_faced,
            "on_target_saved": on_target_saved,
            "on_target_goal_conceded": on_target_goal_conceded,
            "save_percentage": save_percentage,
            "clean_sheet": clean_sheet,
        }

    team_a_stats = get_team_stats(team_a, team_b)
    team_b_stats = get_team_stats(team_b, team_a)

    # (Bar chart and radar chart generation stays the same)
    ...
        # -----------------------------------
    # BAR CHART (SMALL)
    # -----------------------------------
    def generate_bar_chart():
        labels = ['Saves', 'Goals Conceded', 'On Target Faced']
        t_a = [
            team_a_stats["on_target_saved"],
            team_a_stats["on_target_goal_conceded"],
            team_a_stats["on_target_faced"],
        ]
        t_b = [
            team_b_stats["on_target_saved"],
            team_b_stats["on_target_goal_conceded"],
            team_b_stats["on_target_faced"],
        ]

        x = np.arange(len(labels))
        width = 0.35

        fig, ax = plt.subplots(figsize=(5, 3))   # SMALL GRAPH
        ax.bar(x - width/2, t_a)
        ax.bar(x + width/2, t_b)

        ax.set_xticks(x)
        ax.set_xticklabels(labels, rotation=45)
        ax.set_title("Team Comparison")

        buffer = BytesIO()
        plt.tight_layout()
        fig.savefig(buffer, format='png')
        plt.close(fig)
        return base64.b64encode(buffer.getvalue()).decode()

    bar_chart = generate_bar_chart()

    # -----------------------------------
    # RADAR CHART
    # -----------------------------------
    def generate_radar(team_stats, team_color):
        labels = ["Saves", "On Target Faced", "Clean Sheet", "Save %"]

        values = [
            team_stats["on_target_saved"],
            team_stats["on_target_faced"],
            1 if team_stats["clean_sheet"] == "YES" else 0,
            team_stats["save_percentage"] / 100,
        ]

        values += values[:1]

        angles = np.linspace(0, 2*np.pi, len(labels), endpoint=False).tolist()
        angles += angles[:1]

        fig = plt.figure(figsize=(4,4))
        ax = fig.add_subplot(111, polar=True)

        ax.plot(angles, values)
        ax.fill(angles, values, alpha=0.25)

        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(labels)

        buffer = BytesIO()
        plt.tight_layout()
        fig.savefig(buffer, format='png')
        plt.close(fig)
        return base64.b64encode(buffer.getvalue()).decode()

    radar_a = generate_radar(team_a_stats, "blue")
    radar_b = generate_radar(team_b_stats, "red")

    chart_labels = ['Saves', 'Goals Conceded', 'On Target Faced']

    team_a_values = [
        team_a_stats["on_target_saved"],
        team_a_stats["on_target_goal_conceded"],
        team_a_stats["on_target_faced"],
    ]

    team_b_values = [
        team_b_stats["on_target_saved"],
        team_b_stats["on_target_goal_conceded"],
        team_b_stats["on_target_faced"],
    ]



    context = {
        "match": match,
        "team_a_stats": team_a_stats,
        "team_b_stats": team_b_stats,
        "bar_chart": bar_chart,
        "radar_a": radar_a,
        "radar_b": radar_b,
        "chart_labels": chart_labels,
        "team_a_values": team_a_values,
        "team_b_values": team_b_values,
    }

    if return_context:
        return context

    return render(
        request,
        'reports_app/match_report_templates/6_goalkeeping/goalkeeping.html',
        context
    )
