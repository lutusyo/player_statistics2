# apps/medical_data/models/medical_recovery_plan.py

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from datetime import timedelta


class RecoveryPlanStatus(models.TextChoices):
    ACTIVE = "active", "Active"
    COMPLETED = "completed", "Completed"
    CANCELLED = "cancelled", "Cancelled"
    EXTENDED = "extended", "Extended"


class MedicalRecoveryPlan(models.Model):

    visit = models.OneToOneField(
        "medical_data.MedicalVisit",
        on_delete=models.CASCADE,
        related_name="recovery_plan",
    )

    start_date = models.DateField()

    planned_days = models.PositiveIntegerField(
        help_text="Initial number of recovery days."
    )

    expected_end_date = models.DateField(
        null=True,
        blank=True,
    )

    actual_recovery_date = models.DateField(
        null=True,
        blank=True,
    )

    status = models.CharField(
        max_length=20,
        choices=RecoveryPlanStatus.choices,
        default=RecoveryPlanStatus.ACTIVE,
    )

    recovery_notes = models.TextField(
        blank=True
    )

    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="medical_recovery_plans",
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["-start_date", "-created_at"]

        indexes = [
            models.Index(fields=["start_date"]),
            models.Index(fields=["expected_end_date"]),
            models.Index(fields=["status"]),
        ]



    def clean(self):

        if self.planned_days is not None and self.planned_days < 1:
            raise ValidationError(
                "Recovery period must be at least 1 day."
            )

        if (
            self.expected_end_date
            and self.start_date
            and self.expected_end_date < self.start_date
        ):
            raise ValidationError(
                "Expected end date cannot be before start date."
            )

        if (
            self.actual_recovery_date
            and self.start_date
            and self.actual_recovery_date < self.start_date
        ):
            raise ValidationError(
                "Actual recovery date cannot be before start date."
            )


    def save(self, *args, **kwargs):

        if self.start_date and self.planned_days:
            self.expected_end_date = (
                self.start_date
                + timedelta(days=self.planned_days - 1)
            )

        self.full_clean()
        super().save(*args, **kwargs)




    @property
    def recovery_days_completed(self):

        if not self.actual_recovery_date:
            return 0

        return (
            self.actual_recovery_date - self.start_date
        ).days + 1

    @property
    def remaining_days(self):

        if self.status in [
            RecoveryPlanStatus.COMPLETED,
            RecoveryPlanStatus.CANCELLED,
        ]:
            return 0

        if not self.expected_end_date:
            return 0

        remaining = (
            self.expected_end_date
            - timezone.localdate()
        ).days + 1

        return max(remaining, 0)

    def __str__(self):

        return (
            f"{self.visit.player} - "
            f"{self.start_date} - "
            f"{self.expected_end_date}"
        )