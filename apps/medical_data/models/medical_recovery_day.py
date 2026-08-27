# apps/medical_data/models/medical_recovery_day.py

from django.db import models

class RecoveryDayStatus(models.TextChoices):
    PLANNED = "planned", "Planned"
    COMPLETED = "completed", "Completed"
    CANCELLED = "cancelled", "Cancelled"
    SKIPPED = "skipped", "Skipped"

class MedicalRecoveryDay(models.Model):

    recovery_plan = models.ForeignKey("medical_data.MedicalRecoveryPlan",on_delete=models.CASCADE,related_name="daily_programs",)
    day_number = models.PositiveIntegerField()
    date = models.DateField()
    focus_point = models.CharField(max_length=250, help_text="Main activity or focus for this day.",)
    activities = models.TextField(help_text="Detailed activities or instructions for the player.",)
    status = models.CharField(max_length=20, choices=RecoveryDayStatus.choices,default=RecoveryDayStatus.PLANNED,)
    coach_notes = models.TextField(blank=True, help_text="Notes added by the special coach.",)
    completed_at = models.DateTimeField(null=True, blank=True,)

    class Meta:

        ordering = ["date", "day_number"]
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "recovery_plan",
                    "day_number",
                ],
                name="unique_recovery_plan_day",
            ),

            models.UniqueConstraint(
                fields=[
                    "recovery_plan",
                    "date",
                ],
                name="unique_recovery_plan_date",
            ),
        ]

        indexes = [
            models.Index(fields=["date"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):

        return (
            f"{self.recovery_plan.visit.player} - "
            f"Day {self.day_number} - "
            f"{self.date}"
        )