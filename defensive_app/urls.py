from django.urls import path
from defensive_app.views import tagging_panel, record_event, defensive_summary

app_name = 'defensive_app'

urlpatterns = [
    path('<int:match_id>/', tagging_panel.tagging_panel_view, name='enter_defensive_stats'),
    path('<int:match_id>/record/', record_event.record_event_view, name='record_event'),
    path('<int:match_id>/defensive-summary/', defensive_summary.defensive_summary_view, name='defensive_summary'),  # new line
]
