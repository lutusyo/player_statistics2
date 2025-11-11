from django.db.models import Count, Q
from django.shortcuts import render, get_object_or_404
from matches_app.models import Match
from teams_app.models import Team

def gps_matches_list(request, team_id):
    """
    Display matches for a specific team that have GPS records,
    along with the number of GPS entries per match.
    """
    team = get_object_or_404(Team, id=team_id)

    # Filter matches where this team is either home or away
    matches = (
        Match.objects.filter(Q(home_team=team) | Q(away_team=team))
        .annotate(gps_count=Count('gps_records', distinct=True))
        .filter(gps_count__gt=0)  # Only include matches with GPS data
        .order_by('-date')
    )

    context = {
        'matches': matches,
        'team': team,
    }

    return render(request, 'gps_app/gps_list.html', context)
