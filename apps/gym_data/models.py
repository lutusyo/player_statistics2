from django.db import models

from version1.teams_app.models import Team
from version1.players_app.models import Player


class GymType(models.Model):
    """
    Defines the type of gym group.

    Examples: Blue Yellow Red
    Individual
    Rehabilitation
    """
    name = models.CharField(max_length=50, unique=True, null=True, default="Individual")

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class ExerciseCategory(models.Model):
    """
    Defines the category of an exercise.
    Examples: Lower Body Upper Body Power
    """
    name = models.CharField(max_length=50, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Exercise(models.Model):
    """
    Exercises available in the gym.
    """

    name = models.CharField(max_length=100, unique=True)
    category = models.ForeignKey(ExerciseCategory, on_delete=models.PROTECT, related_name="exercises",)

    class Meta:
        ordering = ["category__name", "name"]

    def __str__(self):
        return f"{self.name} - {self.category.name}"


class GymSession(models.Model):
    """
    One gym training session for one team on one date.
    """

    date = models.DateField()
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="gym_sessions",)

    class Meta:
        ordering = ["-date"]

    def __str__(self):
        return f"{self.team} - {self.date}"


class GymGroup(models.Model):
    """
    A group within a gym session.
    """

    gym_session = models.ForeignKey(GymSession, on_delete=models.CASCADE, related_name="groups",)
    gym_type = models.ForeignKey(GymType, on_delete=models.PROTECT, related_name="gym_groups", null=True)
    players = models.ManyToManyField(Player, related_name="gym_groups",blank=True,)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["gym_session", "gym_type"],
                name="unique_gym_type_per_session",
            )
        ]

        ordering = ["gym_type__name"]

    def __str__(self):
        return (
            f"{self.gym_session.team} - "
            f"{self.gym_session.date} - "
            f"{self.gym_type.name}"
        )


class GroupExercise(models.Model):
    """
    Exercise performed by a gym group.
    """
    gym_group = models.ForeignKey(GymGroup, on_delete=models.CASCADE, related_name="exercises",)
    exercise = models.ForeignKey(Exercise, on_delete=models.PROTECT, related_name="group_exercises",)
    weight_kg = models.DecimalField(max_digits=6, decimal_places=2, help_text="Weight in kilograms",)
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
            f"{self.exercise.name} - "
            f"{self.weight_kg} kg - "
            f"{self.sets} sets × {self.reps} reps"
        )