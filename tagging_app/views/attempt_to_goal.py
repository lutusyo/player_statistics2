from django.shortcuts import render, get_object_or_404
from players_app.models import Player
from matches_app.models import Match, MatchLineup
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from collections import defaultdict
from django.db.models import Count
from tagging_app.models import AttemptToGoal, BodyPartChoices, DeliveryTypeChoices, OutcomeChoices
import traceback

from tagging_app.models import PassEvent, GoalkeeperDistributionEvent
from teams_app.models import Team

from django.http import FileResponse
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

import csv
from django.http import HttpResponse
import io



def enter_attempt_to_goal(request, match_id):
    match = get_object_or_404(Match, id=match_id)
    lineup = MatchLineup.objects.filter(match=match, is_starting=True).select_related('player')
    players = [entry.player for entry in lineup]

    outcome_counts = {}
    for player in players:
        counts = AttemptToGoal.objects.filter(player=player, match=match).values('outcome').annotate(count=Count('outcome'))
        outcome_counts[player.id] = {item['outcome']: item['count'] for item in counts}

    context = {
        'match': match,
        'lineup': lineup,
        'players': players,
        'body_parts': BodyPartChoices.choices,
        'delivery_types': DeliveryTypeChoices.choices,
        'outcomes': OutcomeChoices.choices,
        'outcome_counts': outcome_counts,
    }

    return render(request, 'tagging_app/attempt_to_goal_enter_data.html', context)

@csrf_exempt
def save_attempt_to_goal(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            print("Received:", data)

            match = get_object_or_404(Match, id=data['match_id'])
            player = get_object_or_404(Player, id=data['player_id'])

            # 🔥 Get team from MatchLineup
            lineup_entry = MatchLineup.objects.filter(match=match, player=player).first()
            if not lineup_entry:
                return JsonResponse({"status": "error", "message": "Player not found in match lineup"}, status=400)

            tag = AttemptToGoal.objects.create(
                match=match,
                player=player,
                team=lineup_entry.team,  # ✅ Required team field now provided
                minute=data['minute'],
                second=data['second'],
                outcome=data['outcome'],
                body_part=data['body_part'],
                delivery_type=data['delivery_type'],
                assist_by_id=data.get('assist_by_id'),
                pre_assist_by_id=data.get('pre_assist_by_id'),
                timestamp=data['timestamp']
            )

            # ✅ Count per outcome per player
            outcome_counts = AttemptToGoal.objects.filter(match=match, player=player) \
                                                  .values('outcome') \
                                                  .annotate(count=Count('id'))

            outcome_dict = {entry['outcome']: entry['count'] for entry in outcome_counts}

            return JsonResponse({
                "status": "ok",
                "updated_counts": outcome_dict,
                "player_id": player.id,
                "player_name": player.name,
            })

        except Exception as e:
            print("Error saving  YOUR tag:", e)
            traceback.print_exc()  # This prints full error trace
            return JsonResponse({"status": "error", "message": str(e)}, status=400)


    return JsonResponse({"status": "error", "message": "Invalid request method"}, status=405)

def export_attempt_to_goal_csv(request, match_id):
   

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="attempt_to_goal_{match_id}.csv"'

    writer = csv.writer(response)
    # Update header to reflect actual model fields
    writer.writerow(['Player', 'Body Part', 'Delivery Type', 'Zone X', 'Zone Y'])

    attempts = AttemptToGoal.objects.filter(match_id=match_id)
    for a in attempts:
        # Use the correct fields from the model
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


