from django.db import models

class Player(models.Model):
    name = models.CharField(max_length=100)
    position = models.CharField(max_length=30)
    birthdate = models.CharField(null=True, blank=True)

    def __str__(self):
        return self.name
    
class Match(models.Model):
    date = models.DateField()
    opponent = models.CharField(max_length=100)
    is_home = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.date} vs {self.opponent}"
    
class PlayerMatchStats(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    goals = models.PositiveIntegerField(default=0)
    assists = models.PositiveIntegerField(default=0)
    minutes_played = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('player', 'match')

    def __str__(self):
        return f"{self.player.name} - {self.match}"