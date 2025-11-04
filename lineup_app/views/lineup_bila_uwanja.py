from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.db import transaction
from django.utils import timezone
from players_app.models import Player
from matches_app.models import Match
from teams_app.models import Team
from lineup_app.models import MatchLineup, PositionChoices, Formation, POSITION_COORDS
import json

def create_lineup_view(request, match_id, team_id):
    match = get_object_or_404(Match, id=match_id)
    team = get_object_or_404(Team, id=team_id)

    # Fetch players **for the selected team only**
    players_qs = Player.objects.filter(team=team).order_by('name')

    if request.method == "POST":
        starters = request.POST.getlist('starters[]')

        if not starters or len(starters) != 11:
            return JsonResponse({'error': 'You must select exactly 11 starters.'}, status=400)

        with transaction.atomic():
            MatchLineup.objects.filter(match=match, team=team).delete()

            for pid in starters:
                position = request.POST.get(f'position_{pid}')
                pod_number = request.POST.get(f'gps_{pid}') or None

                player_obj = get_object_or_404(Player, id=pid)
                MatchLineup.objects.create(
                    match=match,
                    player=player_obj,
                    team=team,
                    is_starting=True,
                    position=position,
                    pod_number=pod_number,
                    time_in=0,
                )

            if not match.start_time:
                match.start_time = timezone.now()
                match.save()

        return JsonResponse({'success': True})

    # Send formations and position coords to template
    formation_coords_json = json.dumps(POSITION_COORDS)

    return render(request, 'lineup_app/create_lineup.html', {
        'match': match,
        'team': team,
        'players': players_qs,
        'formations': dict(Formation.choices),
        'formation_coords_json': formation_coords_json,
    })
