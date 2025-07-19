# announcements_app/views.py
from django.shortcuts import render
from .models import Announcement
from datetime import date

def announcement_list(request):
    announcements = Announcement.objects.filter(date_for__gte=date.today()).order_by('date_for')
    return render(request, 'announcements_app/announcement_list.html', {'announcements': announcements})

def announcement_by_age_group(request, age_group):
    announcements = Announcement.objects.filter(age_group=age_group).order_by('-date_for')
    return render(request, 'announcements_app/announcement_list.html', {
        'announcements': announcements,
        'selected_age_group': age_group,
    })
