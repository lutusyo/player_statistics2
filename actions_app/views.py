# actions_app/views.py
from django.shortcuts import render, get_object_or_404, redirect
from .models import TeamActionStats, PlayerDetailedAction
from matches_app.models import Match, PlayerMatchStats
from players_app.models import Player
from django.contrib.auth.decorators import login_required
import json
from django.db.models import Sum
from django.http import HttpResponseForbidden

#def match_action_stats(request, match_id):
#   match = get_object_or_404(Match, id=match_id)
#   team_stats = TeamActionStats.objects.filter(match=match)
#   return render(request, 'actions_app/match_actions_stats.html', {
#       'match': match,
#       'team_stats': team_stats,  # renamed from team_action_stats
#   })

def player_action_stats(request, player_id, match_id):
    action = get_object_or_404(PlayerDetailedAction, player__id=player_id, match__id=match_id)

    return render(request, 'actions_app/player_actions_stats.html', {
        'action': action
    })



@login_required
def player_detailed_action_list(request, match_id):

    if request.user.username != 'Azam2':
        return HttpResponseForbidden("Access Denied")
    
    match = get_object_or_404(Match, id=match_id)
    actions = PlayerDetailedAction.objects.select_related('player').filter(match=match)

    # List all actions you track
    action_fields = [
        'shots_on_target_inside_box', 'shots_on_target_outside_box',
        'shots_off_target_inside_box', 'shots_off_target_outside_box',
        'successful_cross', 'unsuccessful_cross',
        'missed_chance', 'bad_pass', 'touches_inside_box',
        'blocked_shots', 'aerial_duel_won', 'aerial_duel_lost',
        'one_v_one_duel_won', 'one_v_one_duel_lost',
        'ball_lost', 'corners', 'offsides',
        'fouls_committed', 'fouls_won', 'mistakes'
    ]

    # Calculate total for each action field
    total_action_counts = {}
    for field in action_fields:
        total = actions.aggregate(total=Sum(field))['total'] or 0
        total_action_counts[field] = total

    # Build player-wise data dictionary: {player_id: {action: count, ...}}
    player_data = {}
    for action_obj in actions:
        player = action_obj.player
        if player.id not in player_data:
            player_data[player.id] = {
                'name': player.name,
                'actions': {}
            }
        for field in action_fields:
            player_data[player.id]['actions'][field] = getattr(action_obj, field, 0)

    context = {
        'match': match,
        'total_action_counts': total_action_counts,
        'player_data': player_data,
        'action_fields': action_fields,
    }

    return render(request, 'actions_app/player_actions_stats_list.html', context)



@login_required
def tagging_panel_view(request, match_id):
    match = get_object_or_404(Match, id=match_id)
    all_players = Player.objects.all()
    lineup_players = Player.objects.filter(playermatchstats__match=match)

    actions = [
        'shots_on_target_inside_box', 'shots_on_target_outside_box',
        'shots_off_target_inside_box', 'shots_off_target_outside_box',
        'successful_cross', 'unsuccessful_cross',
        'missed_chance', 'bad_pass', 'touches_inside_box',
        'blocked_shots', 'aerial_duel_won', 'aerial_duel_lost',
        'one_v_one_duel_won', 'one_v_one_duel_lost', 'ball_lost',
        'corners', 'offsides', 'fouls_committed', 'fouls_won', 'mistakes'
    ]

    if request.method == 'POST':
        data = json.loads(request.POST.get('data'))

        for player_id, action_counts in data.items():
            player = Player.objects.get(id=player_id)

            obj, created = PlayerDetailedAction.objects.get_or_create(
                player=player,
                match=match,
                defaults={'is_our_team': True}
            )

            for action, value in action_counts.items():
                if hasattr(obj, action):
                    setattr(obj, action, value)

            obj.save()

        return redirect('matches_app:match_detail', match_id=match.id)
    

    # 👉 Load existing saved actions
    existing_actions = PlayerDetailedAction.objects.filter(match=match)
    action_data = {}

    for action_obj in existing_actions:
        player_id = action_obj.player.id
        action_data[player_id] = {}
        for action in actions:
            action_data[player_id][action] = getattr(action_obj, action, 0)

    return render(request, 'actions_app/tagging_panel.html', {
        'all_players': all_players,
        'lineup_players': lineup_players,
        'match': match,
        'actions': actions,
        'action_data': json.dumps(action_data), # Pass to JS
    })


