# tagging_app_v3/urls.py

from django.urls import path
from version3.tagging_app_v3.views import create_match_event

urlpatterns = [
    path("match/<int:match_id>/event/", create_match_event, name="create_match_event"),
]