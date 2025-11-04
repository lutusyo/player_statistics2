from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import Http404
from collections import defaultdict

from matches_app.models import Match
from players_app.models import Player
from defensive_app.models import PlayerDefensiveStats
from tagging_app.models import AttemptToGoal, PassEvent, GoalkeeperDistributionEvent
from lineup_app.models import MatchLineup, Substitution


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

    # Helper to apply season/competition filters to QuerySets that are related to Match via `match`
    def apply_match_filters(qs):
        if selected_season != 'all':
            qs = qs.filter(match__season=selected_season)
        if selected_competition != 'all':
            qs = qs.filter(match__competition_type=selected_competition)
        return qs

    # --- QuerySets with safe conditional filtering ---
    lineup_qs = MatchLineup.objects.filter(player=player).select_related('match')
    lineup_qs = apply_match_filters(lineup_qs)

    # Goals (only count attempts that are actual goals)
    goals_qs = AttemptToGoal.objects.filter(
        player=player,
        outcome='On Target Goal',  # matches OutcomeChoices.ON_TARGET_GOAL
        is_own_goal=False
    ).select_related('match')
    goals_qs = apply_match_filters(goals_qs)

    # Assists: only count assists that led to a goal (i.e. the assisted AttemptToGoal has outcome = goal)
    assists_qs = AttemptToGoal.objects.filter(
        assist_by=player,
        outcome='On Target Goal',
        is_own_goal=False
    ).select_related('match')
    assists_qs = apply_match_filters(assists_qs)

    defensive_qs = PlayerDefensiveStats.objects.filter(player=player).select_related('match')
    defensive_qs = apply_match_filters(defensive_qs)


        # --- INDIVIDUAL DATA ---

    # 1️⃣ Attempt to Goal (shots)
    attempts_qs = AttemptToGoal.objects.filter(player=player).select_related('match')
    attempts_qs = apply_match_filters(attempts_qs)

    # 2️⃣ Passes
    passes_qs = PassEvent.objects.filter(from_player=player).select_related('match')
    passes_qs = apply_match_filters(passes_qs)

    # 3️⃣ Goalkeeper Distributions
    gk_dist_qs = GoalkeeperDistributionEvent.objects.filter(goalkeeper=player).select_related('match')
    gk_dist_qs = apply_match_filters(gk_dist_qs)




    # Substitutions (use Substitution model to count sub-in / sub-out)
    subs_in_qs = Substitution.objects.filter(player_in__player=player).select_related('match', 'player_in__match')
    subs_out_qs = Substitution.objects.filter(player_out__player=player).select_related('match', 'player_out__match')
    subs_in_qs = apply_match_filters(subs_in_qs)
    subs_out_qs = apply_match_filters(subs_out_qs)

    # Sets of match ids where the player appears in each source
    lineup_match_ids = set(lineup_qs.values_list('match_id', flat=True))
    goals_match_ids = set(goals_qs.values_list('match_id', flat=True))
    assists_match_ids = set(assists_qs.values_list('match_id', flat=True))
    defensive_match_ids = set(defensive_qs.values_list('match_id', flat=True))
    subs_in_match_ids = set(subs_in_qs.values_list('match_id', flat=True))
    subs_out_match_ids = set(subs_out_qs.values_list('match_id', flat=True))

    all_match_ids = lineup_match_ids | goals_match_ids | defensive_match_ids | assists_match_ids | subs_in_match_ids | subs_out_match_ids

    # initialize dict per competition
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

    # preload matches
    matches = Match.objects.filter(id__in=all_match_ids).select_related()

    # build a quick map of lineups by match for faster lookup
    lineups_by_match = {}
    for lu in lineup_qs:
        lineups_by_match.setdefault(lu.match_id, []).append(lu)

    # Count substitution events per competition (use unique substitution events)
    subs_in_by_match = {}
    for s in subs_in_qs:
        subs_in_by_match.setdefault(s.match_id, 0)
        subs_in_by_match[s.match_id] += 1

    subs_out_by_match = {}
    for s in subs_out_qs:
        subs_out_by_match.setdefault(s.match_id, 0)
        subs_out_by_match[s.match_id] += 1

    # Now iterate matches and populate stats per competition
    for match in matches:
        comp = match.competition_type or 'Unknown'
        stats = stats_dict[comp]

        # match elapsed minutes fallback
        try:
            final_minute = match.elapsed_minutes() if callable(getattr(match, 'elapsed_minutes', None)) else 90
        except Exception:
            final_minute = 90

        # Minutes & starts from lineup (prefer accurate lineup calc)
        mp_for_match = 0
        starts_for_match = 0
        if match.id in lineups_by_match:
            for lu in lineups_by_match[match.id]:
                # calculate minutes using match final minute where possible
                mp = lu.calculate_minutes_played(final_minute=final_minute)
                # fallback to stored minutes_played if save wasn't called earlier
                if not mp and getattr(lu, 'minutes_played', 0):
                    mp = lu.minutes_played
                mp_for_match += (mp or 0)
                if lu.is_starting:
                    starts_for_match += 1

        # Determine if this match counts as an appearance
        had_attempt_or_def = (match.id in goals_match_ids) or (match.id in defensive_match_ids) or (match.id in assists_match_ids)
        had_sub_event = (match.id in subs_in_by_match) or (match.id in subs_out_by_match)
        played_minutes_flag = mp_for_match > 0

        if played_minutes_flag or had_attempt_or_def or had_sub_event:
            stats['appearances'] += 1

            if played_minutes_flag:
                # use actual lineup minutes
                stats['minutes'] += mp_for_match
            elif had_sub_event:
                # estimate 10 minutes if substituted (no lineup info)
                stats['minutes'] += 10
            else:
                # no lineup or substitution info → 0 minutes
                stats['minutes'] += 0

            stats['starts'] += starts_for_match
            stats['sub_in'] += subs_in_by_match.get(match.id, 0)
            stats['sub_out'] += subs_out_by_match.get(match.id, 0)


    # --- goals (already filtered to real goals) ---
    for g in goals_qs:
        comp = g.match.competition_type or 'Unknown'
        stats_dict[comp]['goals'] += 1

    # --- assists (only those that led to goals) ---
    for a in assists_qs:
        comp = a.match.competition_type or 'Unknown'
        stats_dict[comp]['assists'] += 1

    # --- defensive aggregates ---
    for d in defensive_qs:
        comp = d.match.competition_type or 'Unknown'
        s = stats_dict[comp]
        s['tackles_won'] += getattr(d, 'tackle_won', 0) or 0
        s['tackles_lost'] += getattr(d, 'tackle_lost', 0) or 0
        s['yellow_cards'] += getattr(d, 'yellow_card', 0) or 0
        s['red_cards'] += getattr(d, 'red_card', 0) or 0

    # Build player_stats list and totals (same layout your template expects)
    player_stats = []
    totals = dict.fromkeys([
        'appearances', 'minutes', 'starts', 'sub_in', 'sub_out',
        'goals', 'assists', 'tackles_won', 'tackles_lost',
        'yellow_cards', 'red_cards'
    ], 0)

    if selected_competition != 'all':
        # show only that competition (if any stats exist)
        comp = selected_competition
        if comp in stats_dict:
            stats = stats_dict[comp]
            player_stats.append({'competition': comp, **stats})
            for key in totals:
                totals[key] += stats[key]
    else:
        # show all competitions
        for comp, stats in stats_dict.items():
            player_stats.append({'competition': comp, **stats})
            for key in totals:
                totals[key] += stats[key]

    # Seasons and competitions for filter dropdowns
    seasons = Match.objects.values_list('season', flat=True).distinct().order_by('season')
    competitions = Match.objects.values_list('competition_type', flat=True).distinct().order_by('competition_type')

    tab = request.GET.get('tab', 'profile')





    # build a list of matches the player actually played
    matches_played = []

    for match in matches:
        # Try to get the player's lineup for this match
        lineup = MatchLineup.objects.filter(match=match, player=player).first()
        if lineup or match.id in goals_match_ids or match.id in assists_match_ids or match.id in defensive_match_ids:
            matches_played.append({
                'match': match,
                'minutes_played': lineup.minutes_played if lineup else 0,
            })





    return render(request, 'players_app/player_detail.html', {
        'player': player,
        'related_players': related_players,
        'seasons': seasons,
        'competitions': competitions,
        'selected_season': selected_season,
        'selected_competition': selected_competition,
        'matches_played': matches_played, 
        'player_stats': player_stats,
        'totals': totals,
        'tab': tab,


            # NEW CONTEXT DATA
        'attempts_qs': attempts_qs,
        'passes_qs': passes_qs,
        'gk_dist_qs': gk_dist_qs,
        })
