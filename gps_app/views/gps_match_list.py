from django.db.models import Count
from django.shortcuts import render
from matches_app.models import Match


def gps_matches_list(request):
    """
    List matches that have at least one GPS record,
    annotated with the number of GPS records.
    """
    matches = (
        Match.objects.annotate(gps_count=Count('gps_records', distinct=True))
        .filter(gps_count__gt=0)
        .order_by('-date')
    )

    return render(request, 'gps_app/gps_list.html', {'matches': matches})
