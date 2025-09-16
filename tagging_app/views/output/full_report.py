from django.shortcuts import render, get_object_or_404
from matches_app.models import Match
from lineup_app.models import MatchLineup, POSITION_COORDS
from tagging_app.utils.attempt_to_goal_utils import get_match_full_context
from gps_app.utils.gps_match_detail import get_gps_context
from reports_app.utils.stats import get_match_stats
from tagging_app.utils.pass_network_utils import get_pass_network_context
from matches_app.utils.match_details_utils import get_match_detail_context
from tagging_app.services.summary_key_statistics import get_match_summary


def full_report_view(request, match_id, our_team_id):
    match = get_object_or_404(Match, id=match_id)

    # ======================
    # SCORE CALCULATION
    # ======================
    full_context = get_match_full_context(match.id, our_team_id)
    our_goals = full_context["our_team"]["aggregate"]["attempts"]["total_goals"]
    opponent_goals = full_context["opponent_team"]["aggregate"]["attempts"]["total_goals"]

    if match.home_team.id == our_team_id:
        home_score, away_score = our_goals, opponent_goals
    else:
        home_score, away_score = opponent_goals, our_goals

    result = f"{home_score} - {away_score}"

    # ======================
    # SUMMARY KEY STATISTICS
    # ======================
    summary_stats = get_match_summary(match, match.home_team, match.away_team)

    # ======================
    # LINEUP (STARTING XI + SUBS)
    # ======================
    lineup_qs = MatchLineup.objects.filter(match=match, team_id=our_team_id).select_related("player")
    lineup = []
    substitutes = []

    for l in lineup_qs:
        player_data = {
            "id": l.id,
            "name": l.player.name,
            "number": l.player.jersey_number,
            "position": l.position,
            "minutes_played": l.minutes_played,
            **POSITION_COORDS.get(l.position, {"top": 50, "left": 50})
        }
        if l.is_starting:
            lineup.append(player_data)
        else:
            if l.minutes_played > 0:
                substitutes.append(player_data)

    # Optional: other lists for JS/template
    currently_on_pitch = [p for p in lineup_qs if p.time_in is not None and p.time_out is None]
    already_played_out = [p for p in lineup_qs if p.time_out is not None]
    subs_this_match = [p for p in lineup_qs if not p.is_starting and p.time_in is not None]
    subs_not_played = [p for p in lineup_qs if not p.is_starting and p.time_in is None]

    # ======================
    # OTHER CONTEXT
    # ======================
    per_player_attempts = full_context['our_team']['per_player']['attempts']

    context = {
        'match': match,
        'home_team': match.home_team,
        'away_team': match.away_team,
        'home_score': home_score,
        'away_score': away_score,
        'result': result,
        'competition': match.competition_type,
        'venue': match.venue,
        'date': match.date,
        'kickoff_time': match.time,
        'season': match.season,
        'match_number': getattr(match, 'match_number', None),
        'title': 'Full Match Report',
        'company': 'Azam Fc Analyst',

        # Teams
        'our_team': full_context['our_team'],
        'opponent_team': full_context['opponent_team'],

        # Players & lineup
        'lineup': lineup,
        'substitutes': substitutes,
        'currently_on_pitch': currently_on_pitch,
        'already_played_out': already_played_out,
        'subs_this_match': subs_this_match,
        'subs_not_played': subs_not_played,

        # For template filters
        'outcomes_matrix': per_player_attempts,
        'players': full_context['our_team']['per_player'].keys(),

        # Summary key stats
        'summary': summary_stats,
    }

    # Add other contexts
    context.update(get_match_stats(match))
    context.update(get_gps_context(match))
    context.update(get_pass_network_context(match_id))
    context.update(get_match_detail_context(match))

    return render(request, 'tagging_app/output/full_report.html', context)
