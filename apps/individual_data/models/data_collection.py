from django.core.exceptions import ValidationError
from django.db import models

from version1.players_app.models import Player
from version1.teams_app.models import AgeGroup, Team, StaffMember


# ============================================================
# POSITION CHOICES
# ============================================================

POSITION_CHOICES = [
    ("GK", "Goalkeeper"),

    ("CB", "Centre Back"),
    ("LB", "Left Back"),
    ("RB", "Right Back"),
    ("LWB", "Left Wing Back"),
    ("RWB", "Right Wing Back"),

    ("CDM", "Defensive Midfielder"),
    ("CM", "Central Midfielder"),
    ("CAM", "Attacking Midfielder"),
    ("LM", "Left Midfielder"),
    ("RM", "Right Midfielder"),

    ("LW", "Left Winger"),
    ("RW", "Right Winger"),
    ("CF", "Centre Forward"),
    ("ST", "Striker"),
]


# ============================================================
# TRAINING TOPIC
# ============================================================

class TrainingTopic(models.Model):

    CATEGORY_CHOICES = [
        ("TECHNICAL", "Technical"),
        ("TACTICAL", "Tactical"),
        ("PHYSICAL", "Physical"),
        ("MENTAL", "Mental"),
        ("POSITIONAL", "Positional"),
        ("OTHER", "Other"),
    ]

    name = models.CharField(max_length=100)

    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default="TECHNICAL",
    )

    description = models.TextField(blank=True)

    is_active = models.BooleanField(default=True)

    order = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["category", "order", "name"]

    def __str__(self):
        return self.name


# ============================================================
# TRAINING OBJECTIVE
# ============================================================

class TrainingObjective(models.Model):

    topic = models.ForeignKey(
        TrainingTopic,
        on_delete=models.CASCADE,
        related_name="objectives",
    )

    name = models.CharField(max_length=150)

    description = models.TextField(blank=True)

    is_active = models.BooleanField(default=True)

    order = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order", "name"]

        constraints = [
            models.UniqueConstraint(
                fields=["topic", "name"],
                name="unique_objective_per_topic",
            )
        ]

    def __str__(self):
        return f"{self.topic.name} - {self.name}"


# ============================================================
# COACHING POINT
# ============================================================

class CoachingPoint(models.Model):

    objective = models.ForeignKey(
        TrainingObjective,
        on_delete=models.CASCADE,
        related_name="coaching_points",
    )

    name = models.CharField(max_length=200)

    # Blank = general coaching point.
    # Position selected = position-specific.
    position = models.CharField(
        max_length=10,
        choices=POSITION_CHOICES,
        null=True,
        blank=True,
        help_text="Leave blank if this applies to all positions.",
    )

    description = models.TextField(blank=True)

    is_active = models.BooleanField(default=True)

    order = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["position", "order", "name"]

        constraints = [
            models.UniqueConstraint(
                fields=["objective", "name", "position"],
                name="unique_coaching_point_per_objective_position",
            )
        ]

    def __str__(self):
        if self.position:
            return f"{self.name} ({self.get_position_display()})"

        return self.name


# ============================================================
# TRAINING SESSION
# ============================================================

class TrainingSession(models.Model):

    TRAINING_TYPE_CHOICES = [
        ("INDIVIDUAL", "Individual"),
        ("POSITIONAL", "Position-Specific"),
        ("SMALL_GROUP", "Small Group"),
        ("OTHER", "Other"),
    ]

    INTENSITY_CHOICES = [
        ("LOW", "Low"),
        ("MEDIUM", "Medium"),
        ("HIGH", "High"),
    ]

    date = models.DateField()

    age_group = models.ForeignKey(
        AgeGroup,
        on_delete=models.PROTECT,
        related_name="individual_training_sessions",
    )

    team = models.ForeignKey(
        Team,
        on_delete=models.PROTECT,
        related_name="individual_training_sessions",
        null=True,
        blank=True,
    )

    coach = models.ForeignKey(
        StaffMember,
        on_delete=models.SET_NULL,
        related_name="individual_training_sessions",
        null=True,
        blank=True,
    )

    training_type = models.CharField(
        max_length=20,
        choices=TRAINING_TYPE_CHOICES,
        default="INDIVIDUAL",
    )

    duration_minutes = models.PositiveIntegerField(
        null=True,
        blank=True,
    )

    intensity = models.CharField(
        max_length=10,
        choices=INTENSITY_CHOICES,
        blank=True,
    )

    notes = models.TextField(
        blank=True,
        help_text="General notes about the session.",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-date", "-created_at"]

    def __str__(self):
        team_name = self.team.name if self.team else "No Team"

        return f"{self.date} - {self.age_group.name} - {team_name}"


# ============================================================
# SESSION TOPIC
# ============================================================

class SessionTopic(models.Model):
    """
    A topic/objective covered during a particular session.

    One session can have multiple topics.
    """

    session = models.ForeignKey(
        TrainingSession,
        on_delete=models.CASCADE,
        related_name="session_topics",
    )

    topic = models.ForeignKey(
        TrainingTopic,
        on_delete=models.PROTECT,
        related_name="session_topics",
    )

    objective = models.ForeignKey(
        TrainingObjective,
        on_delete=models.PROTECT,
        related_name="session_topics",
    )

    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

        constraints = [
            models.UniqueConstraint(
                fields=["session", "topic", "objective"],
                name="unique_session_topic_objective",
            )
        ]

    def clean(self):
        if (
            self.objective_id
            and self.topic_id
            and self.objective.topic_id != self.topic_id
        ):
            raise ValidationError(
                "The selected objective does not belong to this topic."
            )

    def __str__(self):
        return f"{self.topic.name} - {self.objective.name}"


# ============================================================
# PLAYER PARTICIPATION
# ============================================================

class PlayerParticipation(models.Model):
    """
    Records the player's participation in a training session.

    A player appears only ONCE per session.

    This stores attendance, minutes and general performance.
    """

    PARTICIPATION_CHOICES = [
        ("FULL", "Full"),
        ("PARTIAL", "Partial"),
        ("OBSERVATION", "Observation Only"),
    ]

    PERFORMANCE_CHOICES = [
        ("1", "1 - Needs Significant Improvement"),
        ("2", "2 - Below Expectation"),
        ("3", "3 - Expected"),
        ("4", "4 - Good"),
        ("5", "5 - Excellent"),
    ]

    session = models.ForeignKey(
        TrainingSession,
        on_delete=models.CASCADE,
        related_name="player_participations",
    )

    player = models.ForeignKey(
        Player,
        on_delete=models.PROTECT,
        related_name="individual_training_participations",
    )

    # Snapshot of position during this session.
    position = models.CharField(
        max_length=10,
        choices=POSITION_CHOICES,
        blank=True,
    )

    participation = models.CharField(
        max_length=20,
        choices=PARTICIPATION_CHOICES,
        default="FULL",
    )

    minutes = models.PositiveIntegerField(
        null=True,
        blank=True,
    )

    performance = models.CharField(
        max_length=1,
        choices=PERFORMANCE_CHOICES,
        blank=True,
    )

    observation = models.TextField(
        blank=True,
        help_text="General observation about the player's session.",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["player__surname", "player__name"]

        constraints = [
            models.UniqueConstraint(
                fields=["session", "player"],
                name="unique_player_participation_per_session",
            )
        ]

    def __str__(self):
        return f"{self.player.full_name} - {self.session.date}"


# ============================================================
# PLAYER INTERVENTION
# ============================================================

class PlayerIntervention(models.Model):
    """
    Records a specific development intervention for a player.

    One player can have MULTIPLE interventions in the same session.
    """

    RESULT_CHOICES = [
        ("NOT_ASSESSED", "Not Assessed"),
        ("NOT_ACHIEVED", "Not Achieved"),
        ("PARTIALLY_ACHIEVED", "Partially Achieved"),
        ("ACHIEVED", "Achieved"),
        ("EXCEEDED", "Exceeded"),
    ]

    player_participation = models.ForeignKey(
        PlayerParticipation,
        on_delete=models.CASCADE,
        related_name="interventions",
    )

    session_topic = models.ForeignKey(
        SessionTopic,
        on_delete=models.PROTECT,
        related_name="player_interventions",
    )

    result = models.CharField(
        max_length=25,
        choices=RESULT_CHOICES,
        default="NOT_ASSESSED",
    )

    observation = models.TextField(
        blank=True,
        help_text="Specific observation for this intervention.",
    )

    next_action = models.TextField(
        blank=True,
        help_text="What should be worked on next?",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["id"]

    def clean(self):
        if (
            self.player_participation_id
            and self.session_topic_id
            and (
                self.player_participation.session_id
                != self.session_topic.session_id
            )
        ):
            raise ValidationError(
                "The player participation and session topic "
                "must belong to the same training session."
            )

    def __str__(self):
        return (
            f"{self.player_participation.player.full_name} - "
            f"{self.session_topic.topic.name}"
        )


# ============================================================
# PLAYER INTERVENTION COACHING POINT
# ============================================================

class PlayerInterventionCoachingPoint(models.Model):
    """
    Coaching points actually selected for a player's intervention.
    """

    intervention = models.ForeignKey(
        PlayerIntervention,
        on_delete=models.CASCADE,
        related_name="coaching_points",
    )

    coaching_point = models.ForeignKey(
        CoachingPoint,
        on_delete=models.PROTECT,
        related_name="intervention_selections",
    )

    achieved = models.BooleanField(default=False)

    note = models.CharField(
        max_length=255,
        blank=True,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["intervention", "coaching_point"],
                name="unique_intervention_coaching_point",
            )
        ]

    def clean(self):
        if (
            self.intervention_id
            and self.coaching_point_id
            and (
                self.coaching_point.objective_id
                != self.intervention.session_topic.objective_id
            )
        ):
            raise ValidationError(
                "The coaching point must belong to the intervention objective."
            )

    def __str__(self):
        return (
            f"{self.intervention.player_participation.player.full_name} - "
            f"{self.coaching_point.name}"
        )


# ============================================================
# SESSION EVALUATION
# ============================================================

class SessionEvaluation(models.Model):

    OBJECTIVE_STATUS_CHOICES = [
        ("NOT_ASSESSED", "Not Assessed"),
        ("NOT_ACHIEVED", "Not Achieved"),
        ("PARTIALLY_ACHIEVED", "Partially Achieved"),
        ("ACHIEVED", "Achieved"),
    ]

    QUALITY_CHOICES = [
        ("POOR", "Poor"),
        ("BELOW_EXPECTATION", "Below Expectation"),
        ("GOOD", "Good"),
        ("VERY_GOOD", "Very Good"),
    ]

    session = models.OneToOneField(
        TrainingSession,
        on_delete=models.CASCADE,
        related_name="evaluation",
    )

    objective_status = models.CharField(
        max_length=25,
        choices=OBJECTIVE_STATUS_CHOICES,
        default="NOT_ASSESSED",
    )

    training_quality = models.CharField(
        max_length=25,
        choices=QUALITY_CHOICES,
        blank=True,
    )

    what_went_well = models.TextField(blank=True)

    challenges = models.TextField(blank=True)

    coach_comment = models.TextField(blank=True)

    next_action = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Evaluation - {self.session}"