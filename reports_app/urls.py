from django.urls import path
from reports_app.views import match_summary3, intro_page, match_summary_stats, full_report, post_match_summary, table_of_contents
from reports_app import views


app_name = 'reports_app'

urlpatterns = [

    # 1. intro pages
    path('intro/post-match-summary/<int:match_id>/', post_match_summary.full_match_context_view, name='post_match_summary'),
    path('intro/in-possession/<int:match_id>/', intro_page.in_possession_view, name='in_possession'),
    path('intro/out-of-possession/<int:match_id>/', intro_page.out_of_possession_view, name='out_of_possession'),
    path('intro/goalkeeping/<int:match_id>/', intro_page.goalkeeping_view, name='goalkeeping'),
    path('intro/set-plays/<int:match_id>/', intro_page.set_plays_view, name='set_plays'),
    path('intro/individual-in-possession/<int:match_id>/', intro_page.individual_in_possession_view, name='individual_in_possession'),
    path('intro/individual-out-of-possession/<int:match_id>/', intro_page.individual_out_of_possession_view, name='individual_out_of_possession'),
    path('intro/individual-physical/<int:match_id>/', intro_page.individual_physical_view, name='individual_physical'),


    # 2. contents pages
    path("table-of-contents/<int:match_id>/<int:our_team_id>/", table_of_contents.table_of_contents_view, name="report_cover"),
    path("full-report/<int:match_id>/<int:our_team_id>/", full_report.full_report_view, name="full_report"),
    path('match-summary/<int:match_id>/', match_summary3.match_summary_view, name='match_summary'),
    path('match-summary/<int:match_id>/summary-stats/', match_summary_stats.match_summary_stats_view, name='match_summary_stats'),

    # 2. match details view
    #path('match/<int:match_id>/', match_reports.match_detail_view, name='match_detail_view'),

    path('match/<int:match_id>/summary/', match_summary3.match_summary_view, name='match_summary_pdf'),
    #### /matches_app/match/6/summary/
    #path('match/<int:match_id>/players/', player_reports.export_player_stats_csv, name='player_stats_csv'),
    #path('team/<str:team>/monthly/', monthly_reports.monthly_report_pdf, name='monthly_report_pdf'),
    #path('team/<str:team>/weekly/', weekly_reports.weekly_reports_pdf, name='weekly_report_pdf'),
]

