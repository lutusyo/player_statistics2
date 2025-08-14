from django.urls import path
from .views import match_reports, weekly_reports, monthly_reports, player_reports, intro_page, match_summary_stats


app_name = 'reports_app'

urlpatterns = [

    # 0
    path('match-summary/<int:match_id>/', match_reports.match_summary_view, name='match_summary'),
    path('match-summary/<int:match_id>/summary-stats/', match_summary_stats.match_summary_stats_view, name='match_summary_stats'),

    # 1. intro pages
    path('intro/<str:report_type>/<int:match_id>/', intro_page.intro_page_view, name='intro_page'),
    # 1. /reports_app/intro/goalkeeping/5/
    # 2. /reports_app/intro/in-possession/5/
    # 3. /reports_app/intro/set-plays/5/
    # 4. /reports_app/intro/out-of-possession/
    # 5. /reports_app/intro/
    # 6. /reports_app/intro/
    # 7. /reports_app/intro/
    # 8. /reports_app/intro/

    # How to put them in html
    # <a href="{% url 'reports_app:intro_page' report_type='in-possession' match_id=match.id %}">IN POSSESSION</a>




    # 2. match details view
    #path('match/<int:match_id>/', match_reports.match_detail_view, name='match_detail_view'),

    #path('match/<int:match_id>/summary/', match_reports.match_detail_view, name='match_summary_pdf'),
    #path('match/<int:match_id>/players/', player_reports.export_player_stats_csv, name='player_stats_csv'),
    #path('team/<str:team>/monthly/', monthly_reports.monthly_report_pdf, name='monthly_report_pdf'),
    #path('team/<str:team>/weekly/', weekly_reports.weekly_reports_pdf, name='weekly_report_pdf'),
]

