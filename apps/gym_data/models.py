from django.db import models

from version1.teams_app.models import Team
from version1.players_app.models import Player


class GymSession(models.Model):
    """
    One gym training session for one team on a specific date.
    """
    date = models.DateField()
    team = models.ForeignKey(Team,on_delete=models.CASCADE,related_name="gym_sessions",)

    class Meta:
        ordering = ["-date"]

    def __str__(self):
        return f"{self.team} - {self.date}"

class GymGroup(models.Model):
    """
    Blue, Yellow, or Red group inside a gym session.
    """

    class GroupColour(models.TextChoices):
        BLUE = "BLUE", "Blue"
        YELLOW = "YELLOW", "Yellow"
        RED = "RED", "Red"

    gym_session = models.ForeignKey(GymSession,on_delete=models.CASCADE,related_name="groups",)
    group_colour = models.CharField(max_length=10,choices=GroupColour.choices,)
    players = models.ManyToManyField(Player,related_name="gym_groups",blank=True,)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["gym_session", "group_colour"],
                name="unique_group_colour_per_gym_session",
            )
        ]

        ordering = ["group_colour"]

    def __str__(self):
        return (
            f"{self.gym_session.team} - "
            f"{self.gym_session.date} - "
            f"{self.get_group_colour_display()}"
        )


class GroupExercise(models.Model):
    """
    An exercise assigned to a gym group.
    """

    class Exercise(models.TextChoices):
        BACK_SQUAT = "BACK_SQUAT", "Back Squat"
        FRONT_SQUAT = "FRONT_SQUAT", "Front Squat"
        DEADLIFT = "DEADLIFT", "Deadlift"
        BENCH_PRESS = "BENCH_PRESS", "Bench Press"
        LEG_PRESS = "LEG_PRESS", "Leg Press"
        LUNGES = "LUNGES", "Lunges"
        ROMANIAN_DEADLIFT = "ROMANIAN_DEADLIFT", "Romanian Deadlift"
        HIP_THRUST = "HIP_THRUST", "Hip Thrust"
        CALF_RAISE = "CALF_RAISE", "Calf Raise"
        PUSH_UP = "PUSH_UP", "Push-Up"
        PULL_UP = "PULL_UP", "Pull-Up"
        PLANK = "PLANK", "Plank"

    gym_group = models.ForeignKey(GymGroup,on_delete=models.CASCADE,related_name="exercises",)
    exercise = models.CharField(max_length=50,choices=Exercise.choices,)

    weight_kg = models.DecimalField(max_digits=6,decimal_places=2,help_text="Weight in kilograms",)
    sets = models.PositiveIntegerField()
    reps = models.PositiveIntegerField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["gym_group", "exercise"],
                name="unique_exercise_per_gym_group",
            )
        ]

    def __str__(self):
        return (
            f"{self.get_exercise_display()} - "
            f"{self.weight_kg} kg - "
            f"{self.sets} sets × {self.reps} reps"
        )