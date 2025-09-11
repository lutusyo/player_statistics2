from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.db import transaction
from django.utils import timezone   # ✅ import timezone
from players_app.models import Player
from lineup_app.models import Match, MatchLineup, PositionChoices

def match_lineup_view(request, match_id):
    match = get_object_or_404(Match, id=match_id)
    
    players_qs = Player.objects.filter(team__in=[match.home_team, match.away_team]).order_by('name')

    if request.method == "POST":
        starters = request.POST.getlist('starters[]')
        bench = request.POST.getlist('bench[]')

        if not starters or len(starters) != 11:
            return JsonResponse({'error': 'You must select exactly 11 starters.'}, status=400)

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
                    time_in=0,  # ✅ starting players always at minute 0
                )

            # Create MatchLineup for bench players
            for pid in bench:
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
                    time_in=None,  # ✅ bench players not yet entered
                )

            # ✅ Start the match clock once the lineup is confirmed
            if not match.start_time:
                match.start_time = timezone.now()
                match.save()

        return JsonResponse({'success': True})

    return render(request, 'lineup_app/create_lineup.html', {
        'match': match,
        'players': players_qs,
    })
