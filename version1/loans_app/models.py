# loans_app/models.py
from django.db import models
from datetime import date

class LoanedPlayer(models.Model):

    FOOT_CHOICES = [
        ("right", "Right"),
        ("left", "Left"),
        ("both", "Both"),
    ]

    # Identity
    full_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    position = models.CharField(max_length=30)
    preferred_foot = models.CharField(max_length=10, choices=FOOT_CHOICES)
    jersey_number = models.PositiveIntegerField(null=True, blank=True)
    photo = models.ImageField(upload_to="loaned_players/photos/", null=True, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    height_cm = models.PositiveIntegerField(null=True, blank=True)
    weight_kg = models.PositiveIntegerField(null=True, blank=True)

    # Loan info
    loan_club = models.CharField(max_length=100)
    loan_club_region = models.CharField(max_length=100, help_text="Region where the loan club is located")
    loan_club_country = models.CharField(max_length=100, help_text="Country where the loan club is located")
    loan_start_date = models.DateField()
    loan_end_date = models.DateField()

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def age(self):
        today = date.today()
        return today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))

    def __str__(self):
        return f"{self.full_name} → {self.loan_club} ({self.loan_club_region})"



# loans_app/models.py

from django.db import models

class LoanDailyEntry(models.Model):

    DAY_TYPE_CHOICES = [
        ("training", "Training"),
        ("match", "Match"),
    ]

    MATCH_TYPE_CHOICES = [
        ("league", "League"),
        ("cup", "Cup"),
        ("friendly", "Friendly"),
        ("international", "International"),
    ]

    player = models.ForeignKey(
        "loans_app.LoanedPlayer",
        on_delete=models.CASCADE,
        related_name="daily_entries"
    )

    date = models.DateField()
    day_type = models.CharField(max_length=10, choices=DAY_TYPE_CHOICES)

    # =========================
    # TRAINING
    # =========================
    training_minutes = models.PositiveIntegerField(null=True, blank=True)

    # =========================
    # MATCH
    # =========================
    match_type = models.CharField(max_length=20, choices=MATCH_TYPE_CHOICES, null=True, blank=True)
    opponent = models.CharField(max_length=100, null=True, blank=True)
    result = models.CharField(max_length=20, null=True, blank=True)

    appearance = models.BooleanField(default=False)
    started = models.BooleanField(default=False)

    minutes_played = models.PositiveIntegerField(null=True, blank=True)

    # 🔹 UPDATED
    sub_in = models.BooleanField(default=False)
    sub_in_minute = models.PositiveIntegerField(null=True, blank=True)

    sub_out = models.BooleanField(default=False)
    sub_out_minute = models.PositiveIntegerField(null=True, blank=True)

    goals = models.PositiveIntegerField(default=0)
    assists = models.PositiveIntegerField(default=0)
    pre_assists = models.PositiveIntegerField(default=0)

    yellow_cards = models.PositiveIntegerField(default=0)
    red_cards = models.PositiveIntegerField(default=0)

    clean_sheet = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("player", "date")
        ordering = ["-date"]

    def __str__(self):
        return f"{self.player.full_name} | {self.date} | {self.day_type}"
