from django.urls import path
from .views import match_reports, weekly_reports, monthly_reports, player_reports, intro_page, match_summary_stats, full_report


app_name = 'reports_app'

urlpatterns = [

    path('full-report/<int:match_id>/', full_report.full_report_view, name='full_report'),
    # 0
    path('match-summary/<int:match_id>/', match_reports.match_summary_view, name='match_summary'),
    ## /reports_app/match-summary/6/
    path('match-summary/<int:match_id>/summary-stats/', match_summary_stats.match_summary_stats_view, name='match_summary_stats'),

    # 1. intro pages

    path('intro/post-match-summary/<int:match_id>/', intro_page.post_match_summary_view, name='post_match_summary'),
    path('intro/in-possession/<int:match_id>/', intro_page.in_possession_view, name='in_possession'),
    path('intro/out-of-possession/<int:match_id>/', intro_page.out_of_possession_view, name='out_of_possession'),
    path('intro/goalkeeping/<int:match_id>/', intro_page.goalkeeping_view, name='goalkeeping'),
    path('intro/set-plays/<int:match_id>/', intro_page.set_plays_view, name='set_plays'),
    path('intro/individual-in-possession/<int:match_id>/', intro_page.individual_in_possession_view, name='individual_in_possession'),
    path('intro/individual-out-of-possession/<int:match_id>/', intro_page.individual_out_of_possession_view, name='individual_out_of_possession'),
    path('intro/individual-physical/<int:match_id>/', intro_page.individual_physical_view, name='individual_physical'),


    # How to put them in html
    # <a href="{% url 'reports_app:intro_page' report_type='in-possession' match_id=match.id %}">IN POSSESSION</a>

    # 2. match details view
    #path('match/<int:match_id>/', match_reports.match_detail_view, name='match_detail_view'),

    path('match/<int:match_id>/summary/', match_reports.match_summary_view, name='match_summary_pdf'),
    #### /matches_app/match/6/summary/
    #path('match/<int:match_id>/players/', player_reports.export_player_stats_csv, name='player_stats_csv'),
    #path('team/<str:team>/monthly/', monthly_reports.monthly_report_pdf, name='monthly_report_pdf'),
    #path('team/<str:team>/weekly/', weekly_reports.weekly_reports_pdf, name='weekly_report_pdf'),
]

