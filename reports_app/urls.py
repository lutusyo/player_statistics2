# reports_app/urls.py
from django.urls import path
from reports_app.views.daily_report_views import (
    report_filters
)
from reports_app.views.daily_report_views import fitness_views, iap_views, medical_views, mesocycle_views, performance_views, report_exports, result_views, scouting_views, statistics_view, team_reports_view, transition_views
from reports_app.views.match_report_views import ( 
    goalkeeping_view, 
    set_plays_views, 
    in_possession_views, 
    post_match_summary_views, 
    full_match_report_views,
    summary_key_statistics_views,
    )

from reports_app.views.match_report_views.full_match_report_views import full_match_report_view, download_full_report_pdf
from reports_app.views.match_report_views.match_report_dashboard_view import match_report_dashboard

app_name = 'reports_app'

urlpatterns = [
    # Medical
    path('medical/<int:team_id>/', medical_views.medical_reports, name='medical_reports'),
    path('medical/<int:team_id>/export/excel/', medical_views.export_medical_excel, name='export_medical_excel'),
    path('medical/<int:team_id>/export/pdf/', medical_views.export_medical_pdf, name='export_medical_pdf'),

    # Scouting
    path('scouting/<int:team_id>/', scouting_views.scouting_reports, name='scouting_reports'),
    path('scouting/<int:team_id>/export/excel/', scouting_views.export_scouting_excel, name='export_scouting_excel'),
    path('scouting/<int:team_id>/export/pdf/', scouting_views.export_scouting_pdf, name='export_scouting_pdf'),

    # Performance
    path('performance/<int:team_id>/', performance_views.performance_reports, name='performance_reports'),
    path('performance/<int:team_id>/export/excel/', performance_views.export_performance_excel, name='export_performance_excel'),
    path('performance/<int:team_id>/export/pdf/', performance_views.export_performance_pdf, name='export_performance_pdf'),
    # Mesocycle
    path('mesocycle/<int:team_id>/', mesocycle_views.mesocycle_reports, name='mesocycle_reports'),
    path('mesocycle/<int:team_id>/export/excel/', mesocycle_views.export_mesocycle_excel, name='export_mesocycle_excel'),
    path('mesocycle/<int:team_id>/export/pdf/', mesocycle_views.export_uploaded_mesocycle_pdf, name='export_mesocycle_pdf'),
    path('team/<int:team_id>/export-all-pdfs/', mesocycle_views.export_all_mesocycle_pdfs, name='export_all_mesocycle_pdfs'),
    # Fitness
    path('fitness/<int:team_id>/', fitness_views.fitness_reports, name='fitness_reports'),
    path('fitness/<int:team_id>/export/excel/', fitness_views.export_fitness_excel, name='export_fitness_excel'),
    path('fitness/<int:team_id>/export/pdf/', fitness_views.export_fitness_pdf, name='export_fitness_pdf'),
    # IAP
    path('iap/<int:team_id>/', iap_views.iap_reports, name='iap_reports'),
    path('iap/<int:team_id>/export/excel/', iap_views.export_iap_excel, name='export_iap_excel'),
    path('iap/<int:team_id>/export/pdf/', iap_views.export_iap_pdf, name='export_iap_pdf'),
    # Transition
    path('transition/<int:team_id>/', transition_views.transition_reports, name='transition_reports'),
    path('transition/<int:team_id>/export/excel/', transition_views.export_transition_excel, name='export_transition_excel'),
    path('transition/<int:team_id>/export/pdf/', transition_views.export_transition_pdf, name='export_transition_pdf'),
    # Results
    path('results/<int:team_id>/', result_views.result_reports, name='result_reports'),
    path('results/<int:team_id>/export/excel/', result_views.export_results_excel, name='export_result_excel'),
    path('results/<int:team_id>/export/pdf/', result_views.export_results_pdf, name='export_result_pdf'),
    # Statistics
    path('team/<int:team_id>/statistics/', statistics_view.statistics_list_view, name='statistics_list'),
    path('team/<int:team_id>/statistics/export/excel/', statistics_view.statistics_export_excel, name='statistics_export_excel'),
    path('team/<int:team_id>/statistics/export/pdf/', statistics_view.statistics_export_pdf, name='statistics_export_pdf'),
    # Dashboards
    path('team-reports/<int:team_id>/dashboard/', report_filters.reports_dashboard, name='reports_dashboard'),
    path('team-reports/<int:team_id>/', team_reports_view.team_reports_view, name='team_reports'),
    # existing export URLs
    path('export/excel/<str:section>/', report_exports.export_section_excel, name='export_section_excel'),
    path('reports-dashboard/combined-excel/', report_exports.export_combined_excel, name='export_combined_excel'),
    path('reports-dashboard/combined-pdf/', report_exports.export_combined_pdf, name='export_combined_pdf'),
    path('team-reports/<int:team_id>/dashboard/', report_filters.reports_dashboard, name='reports_dashboard'),
    path('team-reports/<int:team_id>/', team_reports_view.team_reports_view, name='team_reports'),
    

    # MATCH REPORT HOME PAGE
    path('match/<int:match_id>/<int:our_team_id>/report/',match_report_dashboard, name='match_report_dashboard'),

    # 1. Post match summary
    path('match/<int:match_id>/<int:our_team_id>/post-match-summary/', post_match_summary_views.full_match_context_view, name='post_match_summary'),

    # 3. Key statistics summary
    path("match/<int:match_id>/summary-key-statistics/",summary_key_statistics_views.summary_key_statistics_view, name="summary_key_statistics"),

    # 4. In possession
    path('match/<int:match_id>/attempt-to-goal-dashboard/', in_possession_views.attempt_to_goal_dashboard,name='attempt_to_goal_dashboard'),

    # 6. Goalkeeping
    path("match/<int:match_id>/<int:our_team_id>/goalkeeping/", goalkeeping_view.goalkeeping_view,name="goalkeeping_report"),
 
    # 7. Set plays
    path('match/<int:match_id>/<int:team_id>/setplays/', set_plays_views.setplays_dashboard, name='setplays_dashboard'),

    # Full report
    path('match/<int:match_id>/<int:our_team_id>/full-report/',full_match_report_views.full_match_report_view,name='full_match_report'),
    path('match/<int:match_id>/<int:our_team_id>/download-pdf/', download_full_report_pdf,name='download_full_report_pdf'),

]

