#version1/library_app/models.py
from django.db import models

from version1.tagging_app.models import AttemptToGoal
# import other clip models later if needed


class Highlight(models.Model):
    name = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    STATUS_CHOICES = [ ('draft', 'Draft'), ('generated', 'Generated'),]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES,default='draft')

    def __str__(self):
        return self.name


class HighlightClip(models.Model):
    highlight = models.ForeignKey(Highlight,on_delete=models.CASCADE,related_name='clips')
    clip = models.ForeignKey(AttemptToGoal,on_delete=models.CASCADE)
    order = models.PositiveIntegerField(default=0)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order']


class Reel(models.Model):
    highlight = models.ForeignKey(Highlight, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    video_file = models.FileField(upload_to='reels/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_generated = models.BooleanField(default=False)

    def __str__(self):
        return self.title