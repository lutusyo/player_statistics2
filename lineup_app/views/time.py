# matches_app/views.py
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.http import JsonResponse
from matches_app.models import Match   # make sure Match is imported

def api_match_time(request, match_id):
    match = get_object_or_404(Match, id=match_id)

    if not match.start_time:
        return JsonResponse({"minute": 0, "status": "not_started"})
    
    if match.end_time:
        elapsed = int((match.end_time - match.start_time).total_seconds() // 60)
        return JsonResponse({"minute": elapsed, "status": "ended"})
    
    elapsed = int((timezone.now() - match.start_time).total_seconds() // 60)
    return JsonResponse({"minute": elapsed, "status": "running"})
