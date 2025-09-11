# Register your models here.
from django.contrib import admin
from .models import AttemptToGoal,PassEvent

admin.site.register(AttemptToGoal)
admin.site.register(PassEvent)



