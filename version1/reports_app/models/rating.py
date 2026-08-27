from django.db import models
from django.utils import timezone
from version1.teams_app.models import Team, StaffMember
from version1.players_app.models import Player, SEASON_CHOICES

class PlayerPerformancePotentialRating(models.Model):

    RATING_CHOICES = [
        (1, '1 - Poor'),
        (2, '2 - Average'),
        (3, '3 - Good'),
    ]

    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='performance_potential_ratings')
    team = models.ForeignKey(Team, on_delete=models.CASCADE,related_name='player_ratings')
    season = models.CharField(max_length=20, choices=SEASON_CHOICES)
    performance = models.PositiveSmallIntegerField(choices=RATING_CHOICES)
    potential = models.PositiveSmallIntegerField(choices=RATING_CHOICES)
    rated_by = models.ForeignKey(StaffMember, on_delete=models.SET_NULL,null=True,blank=True,related_name='player_ratings')

    # Date and time when the coach submitted the rating
    rated_at = models.DateTimeField(default=timezone.now)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-rated_at']

        indexes = [
            models.Index(fields=['player', '-rated_at']),
            models.Index(fields=['team', 'season', '-rated_at']),
    ]

   
    def __str__(self):
        return (
            f"{self.player.name} "
            f"{self.player.second_name} "
            f"{self.player.surname} - "
            f"{self.get_matrix_category()} - "
            f"{self.rated_at.date()}"
    )

    def get_matrix_category(self):

        matrix = {
            (1, 1): 'Risk',
            (2, 1): 'Threshold',
            (3, 1): 'Culture carrier',

            (1, 2): 'Dilemma',
            (2, 2): 'Solid',
            (3, 2): 'No brainer',

            (1, 3): 'Enigma',
            (2, 3): 'Unpolished',
            (3, 3): 'Exceptional',
        }

        return matrix.get((self.performance, self.potential))