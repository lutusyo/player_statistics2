from django.db import models
from datetime import date
from version1.teams_app.models import Team
from version1.players_app.models import Player


ROLE_CHOICES = [
    ("GK", "Goalkeeper"),
    ("CB", "Center Back"),
    ("FB", "Full Back"),
    ("WB", "Wing Back"),
    ("DM", "Defensive Midfielder"),
    ("CM", "Central Midfielder"),
    ("AM", "Attacking Midfielder"),
    ("WM", "Wide Midfielder"),
    ("W", "Winger"),
    ("ST", "Striker"),
]


POSITION_CHOICES = [
    ("Forward", "Forward"),
    ("Winger", "Winger"),
    ("Midfielder", "Midfielder"),
    ("Defender", "Defender"),
    ("Goalkeeper", "Goalkeeper"),
]


class LoanedPlayer(models.Model):

    FOOT_CHOICES = [
        ("right", "Right"),
        ("left", "Left"),
        ("both", "Both"),
    ]

    # ✅ LINK TO PLAYER (IMPORTANT)
    player = models.ForeignKey(
        Player,
        on_delete=models.CASCADE,
        related_name="loans"
    )

    date_of_birth = models.DateField()

    position = models.CharField(
        max_length=20,
        choices=POSITION_CHOICES
    )

    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        blank=True,
        null=True
    )

    preferred_foot = models.CharField(max_length=10, choices=FOOT_CHOICES)

    jersey_number = models.PositiveSmallIntegerField(null=True, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    height_cm = models.PositiveSmallIntegerField(null=True, blank=True)
    weight_kg = models.PositiveSmallIntegerField(null=True, blank=True)

    photo = models.ImageField(upload_to="loaned_players/photos/", null=True, blank=True)

    # TEAM
    loan_club = models.ForeignKey(
        Team,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="loaned_players_v2"  # ✅ avoid conflict
    )

    loan_start_date = models.DateField()
    loan_end_date = models.DateField()

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # AGE
    def age(self):
        today = date.today()
        return today.year - self.date_of_birth.year - (
            (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
        )

    def __str__(self):
        return f"{self.player.full_name} → {self.loan_club}"

class LoanDailyEntry(models.Model):

    DAY_TYPE_CHOICES = [
        ("training", "Training"),
        ("match", "Match"),
    ]

    COMPETITION_TYPE_CHOICES = [
        ("league", "League"),
        ("cup", "Cup"),
        ("friendly", "Friendly"),
        ("international", "International"),
        ("tournament", "Tournament"),
    ]

    TEAM_SIDE_CHOICES = [
        ("home", "Home"),
        ("away", "Away"),
    ]

    player = models.ForeignKey(LoanedPlayer,
        on_delete=models.CASCADE,
        related_name="daily_entries"
    )

    date = models.DateField()
    day_type = models.CharField(max_length=10, choices=DAY_TYPE_CHOICES)

    training_minutes = models.PositiveIntegerField(null=True, blank=True)

    competition_type = models.CharField(max_length=20, choices=COMPETITION_TYPE_CHOICES, null=True, blank=True)

    competition_name = models.CharField(max_length=50, blank=True, null=True)

    home_team = models.ForeignKey(
        Team,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="loan_home_matches"
    )

    away_team = models.ForeignKey(
        Team,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="loan_away_matches"
    )

    home_score = models.PositiveSmallIntegerField(null=True, blank=True)
    away_score = models.PositiveSmallIntegerField(null=True, blank=True)

    team_side = models.CharField(max_length=10, choices=TEAM_SIDE_CHOICES, null=True, blank=True)

    appearance = models.BooleanField(default=False)
    started = models.BooleanField(default=False)

    minutes_played = models.PositiveSmallIntegerField(null=True, blank=True)

    goals = models.PositiveSmallIntegerField(default=0)
    assists = models.PositiveSmallIntegerField(default=0)
    pre_assists = models.PositiveSmallIntegerField(default=0)

    yellow_cards = models.PositiveSmallIntegerField(default=0)
    red_cards = models.PositiveSmallIntegerField(default=0)

    clean_sheet = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("player", "date")
        ordering = ["-date"]