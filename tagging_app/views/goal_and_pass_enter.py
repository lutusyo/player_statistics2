from django.shortcuts import render, get_object_or_404
from django.db.models import Count
from lineup_app.models import MatchLineup
from matches_app.models import Match
from players_app.models import Player
from tagging_app.models import AttemptToGoal, DeliveryTypeChoices, OutcomeChoices
from teams_app.models import Team


def tagging_base_view(request, match_id):
    match = get_object_or_404(Match, id=match_id)

    # ----- Passing Network Context -----
    our_team = match.home_team  # Adjust if you have logic to determine viewer's team
    opponent_team = match.away_team

    our_players = MatchLineup.objects.filter(match=match, team=our_team, is_starting=True)
    opponent_players = MatchLineup.objects.filter(match=match, team=opponent_team, is_starting=True)

    # ----- Attempt to Goal Context -----
    lineup = MatchLineup.objects.filter(match=match, is_starting=True).select_related('player')
    players = [entry.player for entry in lineup]

    # Outcome counts per player
    outcome_counts = {}
    for player in players:
        counts = AttemptToGoal.objects.filter(player=player, match=match) \
            .values('outcome') \
            .annotate(count=Count('outcome'))
        outcome_dict = {item['outcome']: item['count'] for item in counts}
        outcome_dict['total'] = sum(outcome_dict.values())
        outcome_counts[player.id] = outcome_dict

    # Total counts for outcomes (all players)
    total_outcome_counts = AttemptToGoal.objects.filter(match=match) \
        .values('outcome') \
        .annotate(count=Count('outcome'))
    total_outcome_dict = {item['outcome']: item['count'] for item in total_outcome_counts}

    context = {
        'match': match,

        # Passing Network
        'our_team': our_team,
        'opponent_team': opponent_team,
        'our_players': our_players,
        'opponent_players': opponent_players,

        # Attempt to Goal
        'lineup': lineup,
        'players': players,
        'delivery_types': DeliveryTypeChoices.choices,
        'outcomes': OutcomeChoices.choices,
        'outcome_counts': outcome_counts,
        'total_outcome_counts': total_outcome_dict,
    }

    return render(request, 'tagging_app/tagging_base.html', context)
