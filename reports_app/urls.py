from django.urls import path
from .views import match_reports, weekly_reports, monthly_reports, player_reports, intro_page

app_name = 'reports_app'

urlpatterns = [

    # 1. intro pages
    path('intro/<str:report_type>/<int:match_id>/', intro_page.intro_page_view, name='intro_page'),
    #/reports_app/intro/goalkeeping/5/
    #/reports_app/intro/in-possession/5/
    #/reports_app/intro/set-plays/5/

    # How to put them in html
    # <a href="{% url 'reports_app:intro_page' report_type='in-possession' match_id=match.id %}">IN POSSESSION</a>




    # 2. match details view
    #path('match/<int:match_id>/', match_reports.match_detail_view, name='match_detail_view'),

    #path('match/<int:match_id>/summary/', match_reports.match_detail_view, name='match_summary_pdf'),
    #path('match/<int:match_id>/players/', player_reports.export_player_stats_csv, name='player_stats_csv'),
    #path('team/<str:team>/monthly/', monthly_reports.monthly_report_pdf, name='monthly_report_pdf'),
    #path('team/<str:team>/weekly/', weekly_reports.weekly_reports_pdf, name='weekly_report_pdf'),
]
