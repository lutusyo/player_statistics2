from collections import Counter
from django.db.models import Q
from version1.tagging_app.models import AttemptToGoal
from version1.lineup_app.models import MatchLineup
from version1.teams_app.models import Team
from version1.performance_analysis.services.match_analysis import ( get_period_teams, get_finished_matches,)
from version2.tagging_app_v2.models import PassEvent_v2


def count_breakdown(queryset, field):
    counts = Counter(queryset.values_list(field, flat=True))

    return [
        {"name": name or "Not specified", "count": count}
        for name, count in counts.most_common()
    ]


def calculate_shooting_analysis(team, match_ids):
    attempts = AttemptToGoal.objects.filter(
        match_id__in=match_ids,
        team=team,
        is_opponent=False,
    ).exclude(
        outcome="Own Goal"
    )

    total = attempts.count()

    on_target = attempts.filter(
        outcome__in=["On Target Saved", "On Target Goal"]
    ).count()

    goals = attempts.filter(
        outcome="On Target Goal",
        is_own_goal=False,
    ).count()

    saved = attempts.filter(
        outcome="On Target Saved"
    ).count()

    blocked = attempts.filter(outcome="Blocked").count()
    off_target = attempts.filter(outcome="Off Target").count()
    player_errors = attempts.filter(outcome="Player Error").count()

    return {
        "shots": total,
        "shots_on_target": on_target,
        "goals": goals,
        "saved": saved,
        "blocked": blocked,
        "off_target": off_target,
        "player_errors": player_errors,
        "shooting_accuracy": round(on_target / total * 100, 1) if total else 0,
        "conversion_rate": round(goals / total * 100, 1) if total else 0,
        "outcomes": count_breakdown(attempts, "outcome"),
        "delivery_types": count_breakdown(attempts, "delivery_type"),
        "body_parts": count_breakdown(attempts, "body_part"),
        "locations": count_breakdown(attempts, "location_tag"),
    }



def calculate_foul_card_analysis(team, match_ids):
    fouls = PassEvent_v2.objects.filter(
        match_id__in=match_ids,
        actor__team=team,
        action_type="FOULS",
    )

    no_card = fouls.filter(foul_outcome="NO CARD").count()
    yellow_cards = fouls.filter(foul_outcome="YELLOW CARD").count()
    red_cards = fouls.filter(foul_outcome="RED CARD").count()

    fouls_won = PassEvent_v2.objects.filter(
        match_id__in=match_ids,
        action_type="FOULS",
        receiver__team=team,
    ).exclude(actor__team=team).count()

    return {
        "fouls_committed": fouls.count(),
        "fouls_won": fouls_won,
        "no_card_fouls": no_card,
        "yellow_cards": yellow_cards,
        "red_cards": red_cards,
        "total_cards": yellow_cards + red_cards,
    }


def calculate_goalkeeper_analysis(team, matches):
    match_ids = [match.id for match in matches]
    match_map = {match.id: match for match in matches}

    lineups = MatchLineup.objects.filter(
        team=team,
        match_id__in=match_ids,
        player__isnull=False,
    ).filter(
        Q(player__specific_position="GK")
        | Q(player__position="Goalkeeper")
    ).select_related("player", "match")

    goalkeepers = {}

    for lineup in lineups:
        if lineup.is_unused_sub:
            continue

        player = lineup.player

        stats = goalkeepers.setdefault(player.id, {
            "player_id": player.id,
            "player_name": player.full_name,
            "matches_played": 0,
            "starts": 0,
            "substitute_appearances": 0,
            "minutes": 0,
            "clean_sheets": 0,
            "matches_with_goals_conceded": 0,
            "team_goals_conceded": 0,
            "missing_entry_time": 0,
            "invalid_time_intervals": 0,
        })

        if lineup.time_in is None:
            stats["missing_entry_time"] += 1
            continue

        start = lineup.time_in
        end = lineup.time_out if lineup.time_out is not None else 90

        if end < start:
            stats["invalid_time_intervals"] += 1
            continue

        match = match_map.get(lineup.match_id)

        if not match:
            continue

        if match.home_team_id == team.id:
            goals_conceded = match.away_score
        else:
            goals_conceded = match.home_score

        stats["matches_played"] += 1
        stats["minutes"] += end - start

        if lineup.is_starting:
            stats["starts"] += 1
        else:
            stats["substitute_appearances"] += 1

        stats["team_goals_conceded"] += goals_conceded

        if goals_conceded == 0:
            stats["clean_sheets"] += 1
        else:
            stats["matches_with_goals_conceded"] += 1

    goalkeeper_list = []

    for stats in goalkeepers.values():
        appearances = stats["matches_played"]

        stats["average_minutes"] = (
            round(stats["minutes"] / appearances, 1)
            if appearances else 0
        )

        stats["clean_sheet_percentage"] = (
            round(stats["clean_sheets"] / appearances * 100, 1)
            if appearances else 0
        )

        goalkeeper_list.append(stats)

    goalkeeper_list.sort(
        key=lambda item: (
            item["matches_played"],
            item["clean_sheets"],
            item["minutes"],
        ),
        reverse=True,
    )

    return {
        "goalkeepers": goalkeeper_list,
        "total_goalkeepers": len(goalkeeper_list),
    }


def build_technical_analysis(analysis):
    technical_analysis = []

    for period in analysis.periods.order_by("order"):
        team_ids = get_period_teams(analysis, period)

        teams = Team.objects.filter(
            id__in=team_ids,
            team_type="OUR_TEAM",
        )

        period_teams = []

        for team in teams:
            matches = get_finished_matches(period, [team.id])
            match_ids = [match.id for match in matches]

        period_teams.append({
            "team_id": team.id,
            "team_name": team.name,
            "matches_played": len(matches),
            "shooting": calculate_shooting_analysis(team, match_ids),
            "goalkeeping": calculate_goalkeeper_analysis(team, matches),
            "discipline": calculate_foul_card_analysis(team, match_ids),
        })

        technical_analysis.append({
            "period_id": period.id,
            "period_name": period.name,
            "teams": period_teams,
        })

    return technical_analysis
