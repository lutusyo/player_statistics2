from django.shortcuts import render, get_object_or_404
from players_app.models import Player
from matches_app.models import Match, MatchLineup
from django.utils import timezone
from django.http import JsonResponse, HttpResponse, FileResponse
from django.views.decorators.csrf import csrf_exempt
import json
from collections import defaultdict
from django.db.models import Count
from tagging_app.models import AttemptToGoal, BodyPartChoices, DeliveryTypeChoices, OutcomeChoices
import traceback

from tagging_app.models import PassEvent, GoalkeeperDistributionEvent
from teams_app.models import Team

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import io
import csv

from collections import Counter
from django.views.decorators.http import require_GET


def enter_attempt_to_goal(request, match_id):
    match = get_object_or_404(Match, id=match_id)
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
        'lineup': lineup,
        'players': players,
        'body_parts': BodyPartChoices.choices,
        'delivery_types': DeliveryTypeChoices.choices,
        'outcomes': OutcomeChoices.choices,
        'outcome_counts': outcome_counts,
        'total_outcome_counts': total_outcome_dict,
    }

    return render(request, 'tagging_app/attempt_to_goal_enter_data.html', context)



@csrf_exempt
def save_attempt_to_goal(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            match = get_object_or_404(Match, id=data['match_id'])
            player = get_object_or_404(Player, id=data['player_id'])

            lineup_entry = MatchLineup.objects.filter(match=match, player=player).first()
            if not lineup_entry:
                return JsonResponse({"status": "error", "message": "Player not found in match lineup"}, status=400)

            tag = AttemptToGoal.objects.create(
                match=match,
                player=player,
                team=lineup_entry.team,
                minute=data['minute'],
                second=data['second'],
                outcome=data['outcome'],
                body_part=data['body_part'],
                delivery_type=data['delivery_type'],
                assist_by_id=data.get('assist_by_id'),
                pre_assist_by_id=data.get('pre_assist_by_id'),
                timestamp=data['timestamp']
            )

            # Live outcome counts update
            outcome_counts = AttemptToGoal.objects.filter(player=player, match=match) \
                .values('outcome') \
                .annotate(count=Count('outcome'))
            outcome_dict = {item['outcome']: item['count'] for item in outcome_counts}
            outcome_dict['total'] = sum(outcome_dict.values())

            return JsonResponse({
                "status": "ok",
                "updated_counts": outcome_dict,
                "player_id": player.id,
                "player_name": player.name,
                "event_time": f"{data['minute']:02}:{data['second']:02}"
            })

        except Exception as e:
            traceback.print_exc()
            return JsonResponse({"status": "error", "message": str(e)}, status=400)

    return JsonResponse({"status": "error", "message": "Invalid request method"}, status=405)



@require_GET
def get_live_tagging_state(request, match_id):
    match = get_object_or_404(Match, id=match_id)
    attempts = AttemptToGoal.objects.filter(match=match).order_by('-timestamp')[:20]
    data = [{
        'player_name': a.player.name,
        'outcome': a.outcome,
        'body_part': a.body_part,
        'delivery_type': a.delivery_type,
        'minute': a.minute,
        'second': a.second
    } for a in reversed(attempts)]  # oldest first
    return JsonResponse({
        'timer': 0,  # You can later add a MatchTimer model here
        'events': data
    })



def export_attempt_to_goal_csv(request, match_id):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="attempt_to_goal_{match_id}.csv"'
    writer = csv.writer(response)
    writer.writerow(['Player', 'Body Part', 'Delivery Type', 'Zone X', 'Zone Y'])

    attempts = AttemptToGoal.objects.filter(match_id=match_id)
    for a in attempts:
        writer.writerow([
            a.player.name if a.player else 'N/A',
            a.body_part,
            a.delivery_type,
            a.x,
            a.y
        ])
    return response


def export_attempt_to_goal_pdf(request, match_id):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    c.drawString(100, 800, f"Attempt to Goal Report for Match {match_id}")

    attempts = AttemptToGoal.objects.filter(match_id=match_id)
    y = 750
    for a in attempts:
        c.drawString(100, y, f"{a.player.name} | Zone: {a.x}, {a.y}")
        y -= 15
        if y < 50:
            c.showPage()
            y = 800

    c.save()
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename='attempt_to_goal.pdf')
