# models/medical_visit.py
from django.conf import settings
from django.db import models
from version1.teams_app.models import Team
from version1.players_app.models import Player

from apps.core.choices import ( VisitType, MainComplaint, BodySide, InjuryStatus, InjuryMechanism, TrainingStatus,AvailabilityStatus )
from django.core.exceptions import ValidationError

class MedicalVisit(models.Model):

    date = models.DateField()
    team = models.ForeignKey(Team,on_delete=models.PROTECT,related_name="medical_visits")
    player = models.ForeignKey(Player,on_delete=models.PROTECT,related_name="medical_visits")
    visit_type = models.CharField(max_length=30, choices=VisitType.choices)
    main_complaint = models.CharField(max_length=40,choices=MainComplaint.choices)
    body_side = models.CharField(max_length=20,choices=BodySide.choices,default=BodySide.NOT_APPLICABLE)
    injury_status = models.CharField(max_length=20,choices=InjuryStatus.choices,default=InjuryStatus.NEW)
    mechanism_of_injury = models.CharField(max_length=30,choices=InjuryMechanism.choices,blank=True)
    history_of_injury = models.TextField(blank=True)
    physical_examination = models.TextField(blank=True)
    working_diagnosis = models.TextField(blank=True)
    therapy = models.TextField(blank=True)

    training_session_status = models.CharField(max_length=30,choices=TrainingStatus.choices)
    availability_status = models.CharField(max_length=30,choices=AvailabilityStatus.choices,default=AvailabilityStatus.REASSESSMENT)
    recommendations = models.TextField(blank=True)
    next_review_date = models.DateField(null=True, blank=True)
    expected_return_date = models.DateField(null=True, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.SET_NULL,null=True,blank=True, related_name="medical_visits_created")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-date", "-created_at"]

        indexes = [
            models.Index(fields=["date"]),
            models.Index(fields=["team"]),
            models.Index(fields=["player"]),
            models.Index(fields=["visit_type"]),
            models.Index(fields=["main_complaint"]),
            models.Index(fields=["availability_status"]),
        ]

    def clean(self):

        if (self.expected_return_date and self.expected_return_date < self.date):
            raise ValidationError("Expected return date cannot be before visit date.")

        if (self.next_review_date and self.next_review_date < self.date):
            raise ValidationError("Next review date cannot be before visit date.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return (
            f"{self.player} | {self.date} | "
            f"{self.get_main_complaint_display()}"
        )
