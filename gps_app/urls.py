from django.urls import path
from gps_app.views import gps_visualization, upload_gps_data, gps_match_list, gps_match_detail_positions
from gps_app.views.gps_visualization import gps_dashboard, gps_dashboard_data


app_name = 'gps_app'

urlpatterns = [
    path('<int:team_id>/matches_gps_list/', gps_match_list.gps_matches_list, name='gps_list'),
    path('upload/<int:match_id>/', upload_gps_data.upload_gps_csv, name='gps_upload'),
    path('match/<int:match_id>/dashboard/data/', gps_visualization.gps_dashboard_data, name='gps_dashboard_data'),

        # Dashboard page (HTML template)
    path('match/<int:match_id>/dashboard/', gps_dashboard, name='gps_dashboard'),

    # Dashboard JSON data endpoint
    path('match/<int:match_id>/dashboard/data/', gps_dashboard_data, name='gps_dashboard_data'),


     # ... gps data according to position
    path('match/<int:match_id>/position_detail/', gps_match_detail_positions.gps_position_detail, name='gps_position_detail'),
]


