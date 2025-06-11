from django.db import models


UNDER_20 = 'U20'
UNDER_17 = 'U17'
UNDER_15 = 'U15'
AGE_GROUP_CHOICES = [
    (UNDER_20, 'Under 20'),
    (UNDER_17, 'Under 17'),
    (UNDER_15, 'Under 15'),
]

SEASON_CHOICES = [
    ("2022/2023", "2022/2023"),
    ("2023/2024", "2023/2024"),
    ("2024/2025", "2024/2025"),
]

COMPETITION_CHOICES = [
    ('Local Friendly', 'Local Friendly'),
    ('International Friendly', 'International Friendly'),
    ('NBC Youth League', 'NBC Youth League'),
]

class Player(models.Model):
    name = models.CharField(max_length=100)
    birthdate = models.CharField(max_length=10, null=True, blank=True)
    place_of_birth = models.CharField(max_length=100, default="Tanzania")
    nationality = models.CharField(max_length=50, default="Tanzania")
    position = models.CharField(max_length=50, choices=[
        ('Forward', 'Forward'),
        ('Midfielder', 'Midfielder'),
        ('Defender', 'Defender'),
        ('Goalkeeper', 'Goalkeeper'),
    ])
    height = models.DecimalField(max_digits=5, decimal_places=0, default=170)
    weight = models.DecimalField(max_digits=5, decimal_places=0, default=65)
    foot_preference = models.CharField(max_length=5, choices=[('Left', 'Left'), ('Right', 'Right')], default='Right')
    jersey_number = models.PositiveIntegerField(default=0)
    photo = models.ImageField(upload_to='player_photos/', default='files_to_be_imported/default_image.png')
    age_group = models.CharField(max_length=30, choices=AGE_GROUP_CHOICES, default=UNDER_20)

    def __str__(self):
        return self.name
    
class PlayerCareerStage(models.Model):
    STAGE_CHOICES = [
        ('academy', 'Academy'),
        ('club', 'Club'),
        ('national', 'National Team'),
    ]

    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='career_stages')
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