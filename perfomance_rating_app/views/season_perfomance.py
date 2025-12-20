# performance_rating_app/views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from collections import defaultdict

from players_app.models import Player
from perfomance_rating_app.models import PerformanceRating
from matches_app.models import Match
from lineup_app.models import MatchLineup
from tagging_app.models import AttemptToGoal
from defensive_app.models import PlayerDefensiveStats

@login_required
def season_player_overview(request, season=None):
    selected_season = season or request.GET.get('season')
    selected_age_group = request.GET.get('age_group')  # this should be the Player.age_group ID

    # -------------------------
    # SEASONS FOR DROPDOWN
    # -------------------------
    seasons = Match.objects.values_list('season', flat=True).distinct().order_by('season')

    # -------------------------
    # GET LINEUPS FOR OUR TEAM
    # -------------------------
    lineups = MatchLineup.objects.filter(team__team_type='OUR_TEAM')

    if selected_season:
        lineups = lineups.filter(match__season=selected_season)

    lineups = lineups.select_related('player', 'team', 'match')

    # -------------------------
    # GET PLAYERS FROM LINEUPS
    # -------------------------
    player_ids = lineups.values_list('player_id', flat=True).distinct()

    if selected_age_group:
        # Filter players directly by their age_group
        players = Player.objects.filter(
            id__in=player_ids,
            age_group__id=selected_age_group,
            is_active=True
        ).distinct()
    else:
        players = Player.objects.filter(
            id__in=player_ids,
            is_active=True
        ).distinct()

    match_ids = lineups.values_list('match_id', flat=True)

    # =========================
    # SEASON PERFORMANCE RATINGS
    # =========================
    players_ratings = []

    for player in players:
        ratings = PerformanceRating.objects.filter(
            player=player,
            match_id__in=match_ids,
            is_computed=True
        )
        count = ratings.count()
        if count == 0:
            continue

        avg_att = sum(r.attacking or 0 for r in ratings) / count
        avg_cre = sum(r.creativity or 0 for r in ratings) / count
        avg_def = sum(r.defending or 0 for r in ratings) / count
        avg_tac = sum(r.tactical or 0 for r in ratings) / count
        avg_tec = sum(r.technical or 0 for r in ratings) / count

        overall = round((avg_att + avg_cre + avg_def + avg_tac + avg_tec) / 5, 2)

        players_ratings.append({
            "player": player,
            "attacking": round(avg_att, 2),
            "creativity": round(avg_cre, 2),
            "defending": round(avg_def, 2),
            "tactical": round(avg_tac, 2),
            "technical": round(avg_tec, 2),
            "average": overall,
        })

    players_ratings.sort(key=lambda x: x["average"], reverse=True)

    # =========================
    # SEASON AGGREGATED STATS
    # =========================
    stats = defaultdict(lambda: {
        'appearances': 0,
        'minutes': 0,
        'starts': 0,
        'goals': 0,
        'assists': 0,
        'yellow_cards': 0,
        'red_cards': 0,
    })

    goals = AttemptToGoal.objects.filter(
        match_id__in=match_ids,
        outcome='On Target Goal',
        is_own_goal=False
    )
    assists = goals.exclude(assist_by=None)
    defensive = PlayerDefensiveStats.objects.filter(match_id__in=match_ids)

    for lu in lineups:
        minutes = lu.calculate_minutes_played(final_minute=90) or lu.minutes_played or 0
        if minutes > 0:
            s = stats[lu.player_id]
            s['appearances'] += 1
            s['minutes'] += minutes
            if lu.is_starting:
                s['starts'] += 1

    for g in goals:
        stats[g.player_id]['goals'] += 1
    for a in assists:
        stats[a.assist_by_id]['assists'] += 1
    for d in defensive:
        s = stats[d.player_id]
        s['yellow_cards'] += d.yellow_card or 0
        s['red_cards'] += d.red_card or 0

    players_stats = [{'player': player, **stats[player.id]} for player in players]

    # =========================
    # RENDER TEMPLATE
    # =========================
    return render(
        request,
        "performance_rating_app/player_season_overview.html",
        {
            "players": players_ratings,
            "players_stats": players_stats,
            "seasons": seasons,
            "selected_season": selected_season,
            "selected_age_group": selected_age_group,
        }
    )
