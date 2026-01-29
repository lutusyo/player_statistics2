from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.db import transaction
from django.utils import timezone
from players_app.models import Player
from matches_app.models import Match
from teams_app.models import Team
from lineup_app.models import MatchLineup, Formation, POSITION_COORDS
import json


def create_lineup_view(request, match_id, team_id):
    match = get_object_or_404(Match, id=match_id)
    team = get_object_or_404(Team, id=team_id)

    # Players for selected team only
    players_qs = Player.objects.filter(team=team).order_by('name')

    if request.method == "POST":
        starters = request.POST.getlist('starters[]')
        formation = request.POST.get('formation')

        if not formation:
            return JsonResponse({'error': 'Formation is required.'}, status=400)

        if formation not in dict(Formation.choices):
            return JsonResponse({'error': 'Invalid formation.'}, status=400)

        if len(starters) != 11:
            return JsonResponse({'error': 'You must select exactly 11 starters.'}, status=400)

        with transaction.atomic():
            # 🔥 Clear ONLY previous starting XI
            MatchLineup.objects.filter(
                match=match,
                team=team,
                is_starting=True
            ).delete()

            # 🔥 Create starting XI (ORDER DRIVES POSITION)
            for order, pid in enumerate(starters, start=1):
                player = get_object_or_404(Player, id=pid, team=team)

                MatchLineup.objects.create(
                    match=match,
                    team=team,
                    player=player,
                    formation=formation,
                    is_starting=True,
                    order=order,
                    time_in=0
                )
                # ✅ position auto-assigned in model.save()

            # Set match start time once
            if not match.start_time:
                match.start_time = timezone.now()
                match.save()

        return JsonResponse({'success': True})

    # ---------- GET REQUEST ----------
    formation_coords_json = json.dumps(POSITION_COORDS)

    return render(request, 'lineup_app/create_lineup.html', {
        'match': match,
        'team': team,
        'players': players_qs,
        'formations': dict(Formation.choices),
        'formation_coords_json': formation_coords_json,
    })
