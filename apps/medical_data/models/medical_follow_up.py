# models/medical_follow_up.py

from django.db import models
from django.conf import settings
from apps.core.choices import Follow_upStatus


class MedicalFollowUp(models.Model):

    visit = models.ForeignKey("medical_data.MedicalVisit",on_delete=models.CASCADE,related_name="follow_ups")
    review_date = models.DateField()
    notes = models.TextField(blank=True)
    status = models.CharField(max_length=20,choices=Follow_upStatus.choices,default=Follow_upStatus.COMPLETED,)
    doctor = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.SET_NULL,null=True,blank=True,related_name="medical_followups",)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:

        ordering = ["review_date"]

    def __str__(self):

        return (
            f"{self.visit.player} "
            f"- {self.review_date}"
        )