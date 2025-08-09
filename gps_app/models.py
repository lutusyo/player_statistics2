from django.db import models
from players_app.models import Player
from matches_app.models import Match, MatchLineup  # you can import both in one line

class GPSRecord(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name='gps_records')
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='gps_records')
    lineup = models.ForeignKey(MatchLineup, on_delete=models.SET_NULL, null=True, blank=True, related_name='gps_records')

    date_recorded = models.DateField(auto_now_add=True)

    # Required core metrics
    distance = models.FloatField()
    duration = models.CharField(null=True, blank=True, max_length=20)
    max_velocity = models.FloatField()
    meterage_per_minute = models.FloatField(null=True, blank=True)
    player_load = models.FloatField()
    player_load_per_minute = models.FloatField(null=True, blank=True)

    # Sprint & effort metrics
    sprint_distance = models.FloatField()
    sprint_efforts = models.IntegerField()
    high_speed_distance = models.FloatField()
    high_speed_efforts = models.IntegerField()
    acceleration_efforts = models.IntegerField()
    deceleration_efforts = models.IntegerField()

    max_acceleration = models.FloatField()
    max_deceleration = models.FloatField()
    work_rest_ratio = models.FloatField(null=True, blank=True)

    # Heart rate zones
    max_heart_rate = models.IntegerField(null=True, blank=True)
    avg_heart_rate = models.IntegerField(null=True, blank=True)
    red_zone = models.FloatField(null=True, blank=True)

    # Distance categories
    standing_distance = models.FloatField(null=True, blank=True)
    walking_distance = models.FloatField(null=True, blank=True)
    jogging_distance = models.FloatField(null=True, blank=True)
    running_distance = models.FloatField(null=True, blank=True)
    sprinting_distance = models.FloatField(null=True, blank=True)
    acceleration_distance = models.FloatField(null=True, blank=True)
    deceleration_distance = models.FloatField(null=True, blank=True)
    explosive_distance = models.FloatField(null=True, blank=True)
    sprint_explosive_distance = models.FloatField(null=True, blank=True)

    # Physical impact
    impacts = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.match} | {self.player} | {self.date_recorded}"
