from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import Http404
from collections import defaultdict
from django.db.models import Q
from matches_app.models import Match
from players_app.models import Player
from tagging_app.models import AttemptToGoal
from defensive_app.models import PlayerDefensiveStats
from lineup_app.models import MatchLineup

@login_required
def player_detail(request, player_id):
    player = get_object_or_404(Player, id=player_id)
    if not player.is_active:
        raise Http404("This player is inactive")

    related_players = Player.objects.filter(
        age_group=player.age_group, is_active=True
    ).exclude(id=player_id)

    selected_season = request.GET.get('season', 'all')
    selected_competition = request.GET.get('competition', 'all')

    # Build filters for related matches
    match_filters = Q()
    if selected_season != 'all':
        match_filters &= Q(match__season=selected_season)
    if selected_competition != 'all':
        match_filters &= Q(match__competition_type=selected_competition)

    # Get related match IDs from tagging and defensive apps for existing stats coverage
    atg_match_ids = AttemptToGoal.objects.filter(player=player).filter(match_filters).values_list('match_id', flat=True)
    def_match_ids = PlayerDefensiveStats.objects.filter(player=player).filter(match_filters).values_list('match_id', flat=True)
    all_match_ids = set(atg_match_ids).union(set(def_match_ids))

    # Initialize stats dict per competition
    stats_dict = defaultdict(lambda: {
        'appearances': 0,
        'minutes': 0,
        'starts': 0,
        'sub_in': 0,
        'sub_out': 0,
        'goals': 0,
        'assists': 0,
        'tackles_won': 0,
        'tackles_lost': 0,
        'yellow_cards': 0,
        'red_cards': 0
    })

    # --- Add Lineup data (minutes, starts, sub ins/outs, appearances) ---
    lineup_qs = MatchLineup.objects.filter(player=player).filter(
        match__season=selected_season if selected_season != 'all' else None,
        match__competition_type=selected_competition if selected_competition != 'all' else None,
    )

    # If filters are 'all', remove None filters:
    if selected_season == 'all':
        lineup_qs = lineup_qs.exclude(match__season__isnull=True)
    if selected_competition == 'all':
        lineup_qs = lineup_qs.exclude(match__competition_type__isnull=True)

    # Process each lineup record
    for lineup in lineup_qs.select_related('match'):
        comp = lineup.match.competition_type
        stats = stats_dict[comp]
        stats['appearances'] += 1
        stats['minutes'] += lineup.minutes_played or 0
        if lineup.is_starting:
            stats['starts'] += 1
        elif lineup.time_in is not None and lineup.time_in > 0:
            stats['sub_in'] += 1
        if lineup.time_out is not None:
            stats['sub_out'] += 1

    # --- Add matches from AttemptToGoal and DefensiveStats for appearances & minutes fallback ---
    lineup_match_ids = set(lineup_qs.values_list('match_id', flat=True))
    extra_match_ids = all_match_ids - lineup_match_ids

    if extra_match_ids:
        matches = Match.objects.filter(id__in=extra_match_ids)
        for match in matches:
            comp = match.competition_type
            stats_dict[comp]['appearances'] += 1
            stats_dict[comp]['minutes'] += match.elapsed_minutes() or 90

    # --- Add goals ---
    goals_qs = AttemptToGoal.objects.filter(
        player=player,
        outcome='On Target Goal',
        is_own_goal=False
    ).filter(match_filters)

    for g in goals_qs:
        comp = g.match.competition_type
        stats_dict[comp]['goals'] += 1

    # --- Add assists ---
    assists_qs = AttemptToGoal.objects.filter(
        assist_by=player,
        is_own_goal=False
    ).filter(match_filters)

    for a in assists_qs:
        comp = a.match.competition_type
        stats_dict[comp]['assists'] += 1

    # --- Add defensive stats ---
    defensive_qs = PlayerDefensiveStats.objects.filter(player=player).filter(match_filters)
    for d in defensive_qs:
        comp = d.match.competition_type
        stats_dict[comp]['tackles_won'] += d.tackle_won or 0
        stats_dict[comp]['tackles_lost'] += d.tackle_lost or 0
        stats_dict[comp]['yellow_cards'] += d.yellow_card or 0
        stats_dict[comp]['red_cards'] += d.red_card or 0

    # Prepare data for template
    player_stats = []
    totals = dict.fromkeys([
        'appearances', 'minutes', 'starts', 'sub_in', 'sub_out',
        'goals', 'assists', 'tackles_won', 'tackles_lost',
        'yellow_cards', 'red_cards'
    ], 0)

    # If a specific competition is selected, show only that one and sum totals accordingly
    if selected_competition != 'all':
        if selected_competition in stats_dict:
            stats = stats_dict[selected_competition]
            player_stats.append({'competition': selected_competition, **stats})
            for key in totals:
                totals[key] += stats[key]
    else:
        # Show all competitions
        for comp, stats in stats_dict.items():
            player_stats.append({'competition': comp, **stats})
            for key in totals:
                totals[key] += stats[key]

    # Seasons and competitions for filter dropdowns
    seasons = Match.objects.values_list('season', flat=True).distinct().order_by('season')
    competitions = Match.objects.values_list('competition_type', flat=True).distinct().order_by('competition_type')

    tab = request.GET.get('tab', 'profile')

    return render(request, 'players_app/player_detail.html', {
        'player': player,
        'related_players': related_players,
        'seasons': seasons,
        'competitions': competitions,
        'selected_season': selected_season,
        'selected_competition': selected_competition,
        'player_stats': player_stats,
        'totals': totals,
        'tab': tab,
    })
