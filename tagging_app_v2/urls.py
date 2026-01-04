# tagging_app_v2/urls.py
from django.urls import path
from tagging_app_v2 import views


app_name = 'tagging_app_v2'


urlpatterns = [
    path("match/<int:match_id>/tag_v2/", views.create_pass_event_v2, name="tag_panel_v2"),
]
