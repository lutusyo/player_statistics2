from django.shortcuts import render, get_object_or_404
from lineup_app.models import MatchLineup, PositionChoices
from matches_app.models import Match
from django.http import JsonResponse
from django.db import transaction
from players_app.models import Player


# Map position codes to pitch coordinates (% from top, % from left)
POSITION_COORDS = {
    "GK":  {"top": 5,  "left": 45},
    "RB":  {"top": 25, "left": 80},
    "RCB": {"top": 25, "left": 60},
    "LCB": {"top": 25, "left": 40},
    "LB":  {"top": 25, "left": 20},
    "RM":  {"top": 50, "left": 75},
    "CM":  {"top": 50, "left": 55},
    "LM":  {"top": 50, "left": 35},
    "RW":  {"top": 75, "left": 70},
    "LW":  {"top": 75, "left": 30},
    "ST":  {"top": 75, "left": 50},
}


def match_lineup_view(request, match_id):
    match = get_object_or_404(Match, id=match_id)
    
    players_qs = Player.objects.filter(team__in=[match.home_team, match.away_team]).order_by('name')

    if request.method == "POST":
        # Expect two lists from your form:
        # starters[] = list of 11 player ids who start
        # bench[] = list of bench player ids available for substitution

        starters = request.POST.getlist('starters[]')
        bench = request.POST.getlist('bench[]')

        if not starters or len(starters) != 11:
            return JsonResponse({'error': 'You must select exactly 11 starters.'}, status=400)

        # bench can be empty or any number (like 7, 9, etc)

        with transaction.atomic():
            # Delete existing lineup for this match
            MatchLineup.objects.filter(match=match).delete()

            # Create MatchLineup for starters
            for pid in starters:
                position = request.POST.get(f'position_{pid}')
                pod_number = request.POST.get(f'gps_{pid}') or None

                if position not in PositionChoices.values:
                    return JsonResponse({'error': f'Invalid position for player {pid}: {position}'}, status=400)

                try:
                    player_obj = Player.objects.get(id=pid)
                except Player.DoesNotExist:
                    return JsonResponse({'error': f'Player id {pid} not found.'}, status=400)

                MatchLineup.objects.create(
                    match=match,
                    player=player_obj,
                    team=player_obj.team,
                    is_starting=True,
                    position=position,
                    pod_number=pod_number,
                    time_in=0,
                )

            # Create MatchLineup for bench players (subs not started)
            for pid in bench:
                # Bench players usually don't have a position assigned because they start off pitch,
                # but you can allow or require position if you want
                position = request.POST.get(f'position_{pid}') or ""
                pod_number = request.POST.get(f'gps_{pid}') or None

                try:
                    player_obj = Player.objects.get(id=pid)
                except Player.DoesNotExist:
                    return JsonResponse({'error': f'Player id {pid} not found.'}, status=400)

                MatchLineup.objects.create(
                    match=match,
                    player=player_obj,
                    team=player_obj.team,
                    is_starting=False,
                    position=position,
                    pod_number=pod_number,
                    time_in=None,  # Not yet played
                )

        return JsonResponse({'success': True})

    return render(request, 'lineup_app/create_lineup.html', {
        'match': match,
        'players': players_qs,
    })
