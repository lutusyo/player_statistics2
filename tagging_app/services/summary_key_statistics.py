from django.db.models import Sum
from tagging_app.models import AttemptToGoal, PassEvent
from defensive_app.models import PlayerDefensiveStats
from gps_app.models import GPSRecord

def safe_pct(a, b):
    return round((a / b) * 100, 1) if b else 0

def empty():
    return {
        "goals": 0,
        "possession": 0,
        "shots_on_target": 0,
        "shots_off_target": 0,
        "blocked_shots": 0,
        "total_passes": 0,
        "pass_completed": 0,
        "ball_recovered": 0,
        "crosses": 0,
        "corners": 0,
        "offsides": 0,
        "fouls": 0,
        "yellow_cards": 0,
        "red_cards": 0,
        "total_distance": 0,
    }

def get_match_summary(match, home_team, away_team):
    home = empty()
    away = empty()

    # ---------------- ATTEMPTS ----------------
    attempts = AttemptToGoal.objects.filter(match=match)
    for team, bucket in [(home_team, home), (away_team, away)]:
        bucket["goals"] = attempts.filter(
            team=team, outcome='On Target Goal', is_own_goal=False
        ).count()
        bucket["shots_on_target"] = attempts.filter(
            team=team, outcome__in=['On Target Goal', 'On Target Saved']
        ).count()
        bucket["shots_off_target"] = attempts.filter(
            team=team, outcome='Off Target'
        ).count()
        bucket["blocked_shots"] = attempts.filter(
            team=team, outcome='Blocked'
        ).count()
        bucket["crosses"] = attempts.filter(team=team, delivery_type='Cross').count()
        bucket["corners"] = attempts.filter(team=team, delivery_type='Corner').count()

    # ---------------- PASSES ----------------
    def get_pass_stats(team, opponent):
        team_passes = PassEvent.objects.filter(match=match, from_team=team)
        opponent_passes = PassEvent.objects.filter(match=match).exclude(from_team=team)

        total_passes = team_passes.count()

        # Ball lost = passes that went to opponent team
        ball_lost = team_passes.filter(to_team=opponent).count()

        # Pass completed = total passes - ball lost
        pass_completed = total_passes - ball_lost

        # Ball recovered: opponent passes that go to your team
        ball_recovered = opponent_passes.filter(to_team=team).count()

        return total_passes, pass_completed, ball_recovered

    home["total_passes"], home["pass_completed"], home["ball_recovered"] = get_pass_stats(home_team, away_team)
    away["total_passes"], away["pass_completed"], away["ball_recovered"] = get_pass_stats(away_team, home_team)

    # ---------------- POSSESSION ----------------
    total_completed = home["pass_completed"] + away["pass_completed"]
    home["possession"] = safe_pct(home["pass_completed"], total_completed)
    away["possession"] = 100 - home["possession"]

    # ---------------- DEFENSIVE & DISCIPLINE ----------------
    for team, bucket in [(home_team, home), (away_team, away)]:
        defensive = PlayerDefensiveStats.objects.filter(match=match, player__team=team)
        bucket["fouls"] = defensive.aggregate(total=Sum("foul_committed"))["total"] or 0
        bucket["offsides"] = defensive.aggregate(total=Sum("offside"))["total"] or 0
        bucket["yellow_cards"] = defensive.aggregate(total=Sum("yellow_card"))["total"] or 0
        bucket["red_cards"] = defensive.aggregate(total=Sum("red_card"))["total"] or 0

    # ---------------- GPS ----------------
    home["total_distance"] = (
        GPSRecord.objects.filter(match=match, player__team=home_team)
        .aggregate(total=Sum("distance"))["total"] or 0
    ) / 1000  # km

    away["total_distance"] = (
        GPSRecord.objects.filter(match=match, player__team=away_team)
        .aggregate(total=Sum("distance"))["total"] or 0
    ) / 1000  # km

    return {"home_team": home, "away_team": away}
