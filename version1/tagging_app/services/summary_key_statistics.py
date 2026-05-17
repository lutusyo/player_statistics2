from django.db.models import Sum
from version1.tagging_app.models import AttemptToGoal, PassEvent
from version1.defensive_app.models import PlayerDefensiveStats
from version1.gps_app.models import GPSRecord

from django.db.models import F
from version2.tagging_app_v2.models import PassEvent_v2
from version2.tagging_app_v2.models import PassEvent_v2

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
# ---------------- PASSES (V2) ----------------




    def get_pass_stats(team):

        # ALL PASSES MADE BY TEAM
        team_passes = PassEvent_v2.objects.filter(
            match=match,
            actor__team=team,
            action_type__in=["LOW_BALL", "HIGH_BALL"]
        )

        # TOTAL PASSES
        total_passes = team_passes.count()

        # COMPLETED PASSES
        pass_completed = team_passes.filter(
            receiver__isnull=False,
            actor__team=F("receiver__team")
        ).count()

        # BALL RECOVERED
        ball_recovered = PassEvent_v2.objects.filter(
            match=match,
            receiver__team=team
        ).exclude(
            actor__team=F("receiver__team")
        ).count()

        return total_passes, pass_completed, ball_recovered


    home["total_passes"], home["pass_completed"], home["ball_recovered"] = get_pass_stats(home_team)

    away["total_passes"], away["pass_completed"], away["ball_recovered"] = get_pass_stats(away_team)

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
