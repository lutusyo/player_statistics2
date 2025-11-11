from django.db import models
from teams_app.models import AgeGroup, Team
from django import forms

# Season choices
SEASON_CHOICES = [
    ("2022/2023", "2022/2023"),
    ("2023/2024", "2023/2024"),
    ("2024/2025", "2024/2025"),
    ("2025/2026", "2025/2026"),
    ("2026/2027", "2026/2027"),
]

# Competition choices
COMPETITION_CHOICES = [
    ('Local Friendly', 'Local Friendly'),
    ('International Friendly', 'International Friendly'),
    ('NBC Youth League', 'NBC Youth League'),
]

# Medical test Choices
MEDICAL_TEST_CHOICES = [
    ('DONE', 'DONE'),
    ('NOT DONE', 'NOT DONE'),
]


# position choices


# Specific position choices
SPECIFIC_POSITION_CHOICES = [
    # Goalkeepers
    ('GK', 'Goalkeeper'),

    # Defenders
    ('CB', 'Centre Back'),
    ('LB', 'Left Back'),
    ('RB', 'Right Back'),
    ('LWB', 'Left Wing Back'),
    ('RWB', 'Right Wing Back'),

    # Midfielders
    ('CDM', 'Defensive Midfielder'),
    ('CM', 'Central Midfielder'),
    ('CAM', 'Attacking Midfielder'),
    ('LM', 'Left Midfielder'),
    ('RM', 'Right Midfielder'),

    # Forwards / Wingers
    ('LW', 'Left Winger'),
    ('RW', 'Right Winger'),
    ('CF', 'Centre Forward'),
    ('ST', 'Striker'),
]


# Player model
class Player(models.Model):
    name = models.CharField(max_length=50)
    second_name = models.CharField(max_length=50, default='Second_name')
    surname = models.CharField(max_length=50, default='surname')
    jina_maarufu = models.CharField(max_length=50, default='nickname', null=True, blank=True)
    team = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, blank=True, related_name='players')
    birthdate = models.DateField(null=True, blank=True)
    place_of_birth = models.CharField(max_length=100, default="Tanzania")
    nationality = models.CharField(max_length=50, default="Tanzania")

    passport_number = models.CharField(max_length=20, null=True, blank=True)
    medical_test = models.CharField(max_length=10, choices=MEDICAL_TEST_CHOICES, default='NOT DONE')
    joined_azamfc_year = models.PositiveIntegerField(null=True, blank=True)
    
    position = models.CharField(
        max_length=50,
        choices=[
            ('Forward', 'Forward'),
            ('Winger', 'Winger'),
            ('Midfielder', 'Midfielder'),
            ('Defender', 'Defender'),
            ('Goalkeeper', 'Goalkeeper'),
            
        ]
    )
    specific_position = models.CharField(max_length=10, choices=SPECIFIC_POSITION_CHOICES, null=True, blank=True,help_text="e.g., CB, RW, LW, CM, etc.")

    height = models.DecimalField(max_digits=5, decimal_places=0, default=170)
    weight = models.DecimalField(max_digits=5, decimal_places=0, default=65)

    foot_preference = models.CharField(
        max_length=5,
        choices=[('Left', 'Left'), ('Right', 'Right')],
        default='Right'
    )

    jersey_number = models.PositiveIntegerField(default=0)
    former_club = models.CharField(max_length=50, default="Null")
    photo = models.ImageField(
        upload_to='player_photos/',
        default='files_to_be_imported/default_image.png'
    )

    age_group = models.ForeignKey(AgeGroup, on_delete=models.SET_NULL, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.name} - {self.age_group} - {self.team}"

# Career stage for each player
class PlayerCareerStage(models.Model):
    STAGE_CHOICES = [
        ('academy', 'Academy'),
        ('club', 'Club'),
        ('national', 'National Team'),
    ]

    player = models.ForeignKey(
        Player,
        on_delete=models.CASCADE,
        related_name='career_stages'
    )

    stage_type = models.CharField(max_length=20, choices=STAGE_CHOICES)
    team_name = models.CharField(max_length=100)
    start_year = models.PositiveIntegerField()
    end_year = models.PositiveIntegerField(null=True, blank=True)

    position = models.CharField(max_length=50, blank=True)
    matches_played = models.PositiveIntegerField(default=0)
    minutes_played = models.PositiveIntegerField(default=0)
    goals_scored = models.PositiveIntegerField(default=0)
    assists = models.PositiveIntegerField(default=0)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['start_year']

    def __str__(self):
        return f"{self.player.name} - {self.team_name} ({self.start_year}-{self.end_year or 'Present'})"
