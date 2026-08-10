# models/medical_attachment.py
from django.db import models

from apps.core.choices import AttachmentType
from apps.medical_data.models.medical_visit import MedicalVisit





class MedicalAttachment(models.Model):

    visit = models.ForeignKey(MedicalVisit,on_delete=models.CASCADE,related_name="attachments")
    title = models.CharField(max_length=150)
    attachment_type = models.CharField(max_length=20,choices=AttachmentType.choices,default=AttachmentType.OTHER,)
    description = models.CharField(max_length=200,blank=True)
    file = models.FileField(upload_to="medical_attachments/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):

        return (
            f"Attachment - "
            f"{self.visit.player}"
        )