# tagging_app/views.py
from django.shortcuts import render
from tagging_app.models import PassEvent, GoalkeeperDistributionEvent, AttemptToGoal
from matches_app.models import Match
from django.db.models import Count, Avg

def tagging_dashboard(request):
    matches = Match.objects.all().order_by('-date')

    pass_summary = (
        PassEvent.objects.values('match__id', 'match__date')
        .annotate(total_passes=Count('id'))
        .order_by('-match__date')
    )

    gk_summary = (
        GoalkeeperDistributionEvent.objects.values('match__id', 'match__date')
        .annotate(total_distributions=Count('id'))
        .order_by('-match__date')
    )

    attempt_summary = (
        AttemptToGoal.objects.values('match__id', 'match__date')
        .annotate()
        .order_by('-match__date')
    )

    context = {
        'matches': matches,
        'pass_summary': pass_summary,
        'gk_summary': gk_summary,
        'attempt_summary': attempt_summary,
    }
    return render(request, 'tagging_app/merge.html', context)
