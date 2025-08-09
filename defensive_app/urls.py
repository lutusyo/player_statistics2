from django.urls import path
from . import views

app_name = 'defensive_app'

urlpatterns = [
    path('<int:match_id>/', views.tagging_panel, name='enter_defensive_stats'),
    path('<int:match_id>/record/', views.record_event, name='record_event'),
    path('<int:match_id>/defensive-summary/', views.defensive_summary, name='defensive_summary'),  # new line
]
