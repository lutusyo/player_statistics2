from django.urls import path
from .views import match_reports, weekly_reports, monthly_reports, player_reports

app_name = 'reports_app'

urlpatterns = [

    # match details view
   # path('match/<int:match_id>/', match_reports.match_detail_view, name='match_detail_view'),

    #path('match/<int:match_id>/summary/', match_reports.match_detail_view, name='match_summary_pdf'),
    #path('match/<int:match_id>/players/', player_reports.export_player_stats_csv, name='player_stats_csv'),
    #path('team/<str:team>/monthly/', monthly_reports.monthly_report_pdf, name='monthly_report_pdf'),
    #path('team/<str:team>/weekly/', weekly_reports.weekly_reports_pdf, name='weekly_report_pdf'),
]
