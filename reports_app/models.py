from django.db import models
from teams_app.models import Team
from players_app.models import Player
from matches_app.models import VenueChoices, CompetitionType, SeasonChoices
from django.utils import timezone

# Common choices
class ActivityChoices(models.TextChoices):
    MATCH = 'MATCH', 'Match'
    TRAINING = 'TRAINING', 'Training'


class AgreementChoices(models.TextChoices):
    TRIAL = 'TRIAL', 'Trial'
    SIGNING = 'SIGNING', 'Signing'


class Medical(models.Model):
    name = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='medical_records')
    date = models.DateField(null=True, blank=True)
    born = models.DateField(null=True, blank=True)
    squad = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='medical_team')
    injury_or_illness = models.CharField(max_length=100)
    comments = models.CharField(max_length=150, blank=True)
    status = models.CharField(max_length=50)

    

    def __str__(self):
        return f"{self.name} - {self.status}"

class Transition(models.Model):
    name = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='transition_records')
    born = models.DateField(null=True, blank=True)
    squad = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='transition_team')
    played_for = models.CharField(max_length=100)
    activity = models.CharField(max_length=20, choices=ActivityChoices.choices)
    comments = models.CharField(max_length=150, blank=True)
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.activity}"


class Scouting(models.Model):
    name = models.CharField(max_length=100)
    date = models.DateField()
    pos = models.CharField(max_length=50)
    dob = models.DateField()
    squad = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='scouting_team')
    agreement = models.CharField(max_length=20, choices=AgreementChoices.choices)
    comments = models.TextField(blank=True)

    # ✅ New fields
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    former_club = models.CharField(max_length=100, default='Unknown')
    school_name = models.CharField(max_length=150, blank=True, null=True)
    education_level = models.CharField(max_length=100, blank=True, null=True)
    parent_or_coach_phone = models.CharField(max_length=20, blank=True, null=True)
    guardian_name = models.CharField(
        max_length=150,
        blank=True,
        null=True,
        help_text="Name of guardian (if parent or coach)"
    )
    scouting_location = models.CharField(
        max_length=150,
        blank=True,
        null=True,
        help_text="Place where the player was scouted"
    )

    def __str__(self):
        return f"{self.name} - {self.agreement}"



class Performance(models.Model):
    date = models.DateField()
    squad = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='performance_team')
    activity = models.CharField(max_length=20, choices=ActivityChoices.choices)
    comments = models.TextField(blank=True)

    def __str__(self):
        return f"{self.squad} - {self.activity} ({self.date})"


class IndividualActionPlan(models.Model):
    CATEGORY_CHOICES = [
        ('Football', 'Football'),
        ('Physical', 'Physical'),
        ('Medical', 'Medical'),
        ('Lifestyle', 'Lifestyle'),
        ('Mental', 'Mental'),
    ]

    date = models.DateField()
    name = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='action_plans')
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    responsibility = models.CharField(max_length=100)
    action = models.TextField()
    status = models.CharField(max_length=50)
    follow_up = models.CharField(max_length=100, blank=True)
    squad = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='action_plan_team')

    def __str__(self):
        return f"{self.name} - {self.category}"



class Mesocycle(models.Model):
    title = models.CharField(max_length=100)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='mesocycles')
    start_date = models.DateField()
    end_date = models.DateField()
    pdf = models.FileField(upload_to='mesocycles_pdfs/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.team})"



class FitnessPlan(models.Model):
    date = models.DateField()
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='fitness_plans')
    focus_area = models.CharField(max_length=100)
    objective = models.TextField()
    week_number = models.PositiveIntegerField(null=True, blank=True)
    comments = models.TextField(blank=True)

    def __str__(self):
        return f"{self.team} - {self.focus_area} ({self.date})"


class Result(models.Model):
    date = models.DateField()
    venue = models.CharField(max_length=50, choices=VenueChoices.choices, default=VenueChoices.CHAMAZI_COMPLEX)
    competition_type = models.CharField(max_length=50, choices=CompetitionType.choices, default=CompetitionType.LOCAL_FRIENDLY)
    season = models.CharField(max_length=20, choices=SeasonChoices.choices, default=SeasonChoices.SEASON_2025_2026)

    home_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='home_results')
    away_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='away_results')
    
    home_score = models.PositiveIntegerField(default=0)
    away_score = models.PositiveIntegerField(default=0)
    
    goal_scorers = models.TextField(
        blank=True,
        help_text="List goal scorers with team and minute, e.g., 'Player A 23', 'Player B 45'"
    )
    
    # Result choices
    RESULT_CHOICES = [
        ('WIN', 'Win'),
        ('LOSE', 'Lose'),
        ('DRAW', 'Draw'),
    ]
    result = models.CharField(max_length=5, choices=RESULT_CHOICES, blank=True)
    
    # Whether our team is involved
    our_team = models.ForeignKey(
        Team, on_delete=models.CASCADE, related_name='our_results',
        null=True, blank=True,
        help_text="Select our team if this result involves us"
    )

    # Optional column/notes
    notes = models.CharField(max_length=200, blank=True)

    def save(self, *args, **kwargs):
        """
        Automatically determine result if our_team is set
        """
        if self.our_team:
            if self.our_team == self.home_team:
                if self.home_score > self.away_score:
                    self.result = 'WIN'
                elif self.home_score < self.away_score:
                    self.result = 'LOSE'
                else:
                    self.result = 'DRAW'
            elif self.our_team == self.away_team:
                if self.away_score > self.home_score:
                    self.result = 'WIN'
                elif self.away_score < self.home_score:
                    self.result = 'LOSE'
                else:
                    self.result = 'DRAW'
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.home_team} {self.home_score} - {self.away_score} {self.away_team} ({self.date})"






class TrainingMinutes(models.Model):
    date = models.DateField(default=timezone.now)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='training_minutes')
    
    total_minutes = models.PositiveIntegerField(default=0)
    physical_minutes = models.PositiveIntegerField(default=0)
    tactical_minutes = models.PositiveIntegerField(default=0)
    technical_minutes = models.PositiveIntegerField(default=0)
    recovery_minutes = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.team.name} - {self.date} Training"

    def save(self, *args, **kwargs):
        """
        When training is saved, automatically assign minutes to all players in the team.
        Injured players (in Medical table for that date) get 0 minutes by default.
        """
        super().save(*args, **kwargs)

        # Loop through all players in the team
        for player in Player.objects.filter(team=self.team):
            # Check if player is in medical table for this date
            injured = Medical.objects.filter(name=player, date=self.date).exists()

            # Create or update player’s training minutes record
            PlayerTrainingMinutes.objects.update_or_create(
                player=player,
                training_session=self,
                defaults={
                    'minutes': 0 if injured else self.total_minutes,
                }
            )


class PlayerTrainingMinutes(models.Model):
    training_session = models.ForeignKey(
        TrainingMinutes, on_delete=models.CASCADE, related_name='player_minutes'
    )
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='training_minutes')
    minutes = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.player} - {self.training_session.date}: {self.minutes} min"
