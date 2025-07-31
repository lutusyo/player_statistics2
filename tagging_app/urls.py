from django.urls import path
from . import views

app_name = 'tagging_app'

urlpatterns = [
    path('match/<int:match_id>/attempt-to-goal/', views.attempt_to_goal_page, name='attempt_to_goal'),
    path('save-attempt-to-goal/', views.save_attempt_to_goal, name='save_attempt_to_goal'),
]
