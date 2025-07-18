# actions_app/views.py
from django.shortcuts import render, get_object_or_404
from .models import TeamActionStats
from matches_app.models import Match
from .models import PlayerDetailedAction
from players_app.models import Player




def match_action_stats(request, match_id):
    match = get_object_or_404(Match, id=match_id)
    team_stats = TeamActionStats.objects.filter(match=match)
    return render(request, 'actions_app/match_actions_stats.html', {
        'match': match,
        'team_stats': team_stats,  # renamed from team_action_stats
    })

def player_action_stats(request, player_id, match_id):
    action = get_object_or_404(PlayerDetailedAction, player__id=player_id, match__id=match_id)

    return render(request, 'actions_app/player_actions_stats.html', {
        'action': action
    })


def player_detailed_action_list(request, match_id):
    match = get_object_or_404(Match, id=match_id)

    actions = PlayerDetailedAction.objects.select_related('player', 'match').filter(match=match)
    offensive_actions = actions.filter(action_type='offensive')
    defensive_actions = actions.filter(action_type='defensive')

    player_data = {}
    for action in actions:
        player_name = action.player.name
        if player_name not in player_data:
            player_data[player_name] = {
                'duels': action.aerial_duel_won + action.aerial_duel_lost +
                         action.one_v_one_duel_won + action.one_v_one_duel_lost,
                'shots': action.shots_on_target_inside_box +
                         action.shots_on_target_outside_box +
                         action.shots_off_target_inside_box +
                         action.shots_off_target_outside_box,
                'crosses': action.successful_cross + action.unsuccessful_cross,
                'fouls': action.fouls_won + action.fouls_committed,
                'saves': action.saves + action.punches + action.drops + action.catches + action.penalties_saved,
                'touches': action.touches_inside_box,
            }



    offensive_actions = PlayerDetailedAction.objects.filter(match=match, action_type='offensive')
    defensive_actions = PlayerDetailedAction.objects.filter(match=match, action_type='defensive')
    set_piece_actions = PlayerDetailedAction.objects.filter(match=match, action_type='set_piece')
    transition_actions = PlayerDetailedAction.objects.filter(match=match, action_type='transition')
    discipline_actions = PlayerDetailedAction.objects.filter(match=match, action_type='discipline')
    goal_keeping_actions = PlayerDetailedAction.objects.filter(match=match, action_type='goal_keeping')
    general_actions = PlayerDetailedAction.objects.filter(match=match, action_type='general')

    context = {
        'player_data': player_data,
        'match': match,
        'offensive_actions': offensive_actions,
        'defensive_actions': defensive_actions,
        'set_piece_actions': set_piece_actions,
        'transition_actions': transition_actions,
        'discipline_actions': discipline_actions,
        'goal_keeping_actions': goal_keeping_actions,
        'general_actions': general_actions,
    }


    return render(request, 'actions_app/player_actions_stats_list.html', context)



