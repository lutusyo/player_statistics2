from . import views
from django.urls import path

app_name = 'matches_app'

urlpatterns = [

    path('<str:team>/player-statistics/', views.player_statistics_view, name='players_statistics'),
    path('career-stage/<int:stage_id>/', views.career_stage_detail, name='career_stage_detail'),
    path('<str:team>/', views.team_dashboard, name='team_dashboard'),
    path('<str:team>/fixtures/', views.fixtures_view, name='team_fixtures'),
    path('<str:team>/results/', views.results_view, name='team_results'),
    path('<str:team>/table/', views.table_view, name='team_table'),


  
    # Match details
    path('match/<int:match_id>/', views.match_detail, name='match_detail'),
    #path('match/<int:match_id>/add-goal/', views.add_goal, name='add_goal'),

    # Export features
    path('match/<int:match_id>/export/csv/', views.export_player_stats_csv, name='export_csv'),
    path('match/<int:match_id>/export/pdf/', views.export_match_summary_pdf, name='export_pdf'),

 
    path('<str:team>/monthly-report/', views.monthly_report_pdf, name='monthly_report_pdf'),

]