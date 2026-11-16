
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from django.utils.dateparse import parse_date

from version1.teams_app.models import Team, AgeGroup
from version1.players_app.models import Player
from version1.reports_app.models.rating import PlayerPerformancePotentialRating


MATRIX_CATEGORIES = {
    (1, 3): 'Enigma',
    (2, 3): 'Unpolished',
    (3, 3): 'Exceptional',
    (1, 2): 'Dilemma',
    (2, 2): 'Solid',
    (3, 2): 'No brainer',
    (1, 1): 'Risk',
    (2, 1): 'Threshold',
    (3, 1): 'Culture carrier',
}


@login_required
def performance_potential_matrix(request):

    teams = Team.objects.filter(
        team_type='OUR_TEAM'
    ).select_related('age_group').order_by('name')

    age_groups = AgeGroup.objects.all().order_by('code')

    team_id = request.GET.get('team', '')
    age_group_id = request.GET.get('age_group', '')
    start_date_value = request.GET.get('start_date', '')
    end_date_value = request.GET.get('end_date', '')

    context = {
        'teams': teams,
        'age_groups': age_groups,
        'selected_team_id': team_id,
        'selected_age_group_id': age_group_id,
        'start_date': start_date_value,
        'end_date': end_date_value,
        'matrix': {},
        'matrix_rows': [],
        'unrated_players': [],
        'error': None,
        'report_generated': False,
    }

    # All four filters are compulsory
    if not all([
        team_id,
        age_group_id,
        start_date_value,
        end_date_value,
    ]):
        return render(
            request,
            'reports_app/performance_potential/matrix.html',
            context
        )

    start_date = parse_date(start_date_value)
    end_date = parse_date(end_date_value)

    if not start_date or not end_date:
        context['error'] = 'Please enter valid start and end dates.'
        return render(
            request,
            'reports_app/performance_potential/matrix.html',
            context
        )

    if start_date > end_date:
        context['error'] = 'Start date cannot be later than end date.'
        return render(
            request,
            'reports_app/performance_potential/matrix.html',
            context
        )

    team = get_object_or_404(teams, id=team_id)
    age_group = get_object_or_404(AgeGroup, id=age_group_id)

    context.update({
        'team': team,
        'age_group': age_group,
    })

    # Only active players from the selected team and age group
    players = Player.objects.filter(
        team=team,
        age_group=age_group,
        is_active=True,
    ).order_by('name', 'second_name', 'surname')

    # Prepare all nine categories
    matrix = {
        category: []
        for category in MATRIX_CATEGORIES.values()
    }

    # Get ratings from ALL seasons within the selected date range
    ratings = (
        PlayerPerformancePotentialRating.objects
        .filter(
            team=team,
            player__in=players,
            rated_at__date__range=(start_date, end_date),
        )
        .select_related('player', 'rated_by')
        .order_by('player_id', '-rated_at')
    )

    # Keep only the latest rating per player
    latest_ratings = {}

    for rating in ratings:
        if rating.player_id not in latest_ratings:
            latest_ratings[rating.player_id] = rating

    unrated_players = []

    for player in players:
        rating = latest_ratings.get(player.id)

        if rating is None:
            unrated_players.append(player)
            continue

        category = MATRIX_CATEGORIES.get(
            (rating.performance, rating.potential)
        )

        if category:
            matrix[category].append({
                'player': player,
                'rating': rating,
            })

    matrix_rows = [
        [
            {'category': 'Enigma', 'players': matrix['Enigma']},
            {'category': 'Unpolished', 'players': matrix['Unpolished']},
            {'category': 'Exceptional', 'players': matrix['Exceptional']},
        ],
        [
            {'category': 'Dilemma', 'players': matrix['Dilemma']},
            {'category': 'Solid', 'players': matrix['Solid']},
            {'category': 'No brainer', 'players': matrix['No brainer']},
        ],
        [
            {'category': 'Risk', 'players': matrix['Risk']},
            {'category': 'Threshold', 'players': matrix['Threshold']},
            {'category': 'Culture carrier', 'players': matrix['Culture carrier']},
        ],
    ]

    context.update({
        'matrix': matrix,
        'matrix_rows': matrix_rows,
        'unrated_players': unrated_players,
        'report_generated': True,
        'start_date_obj': start_date,
        'end_date_obj': end_date,
    })

    return render(
        request,
        'reports_app/performance_potential/matrix.html',
        context
    )
