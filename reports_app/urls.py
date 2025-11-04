from django.urls import path
from reports_app.views import  ( 
    intro_page, match_summary_stats, results_view, statistics_view, team_reports_view, match_report_view, scouting_views
      )
from reports_app.views import report_filters, report_exports, team_report_dashboard, medical_views


# reports_app/urls.py
from django.urls import path
from reports_app.views import (
    medical_views, scouting_views, performance_views, mesocycle_views,
    fitness_views, iap_views, transition_views, result_views
)


app_name = 'reports_app'

urlpatterns = [




    # Medical
    path('medical/', medical_views.medical_reports, name='medical_reports'),
    path('medical/export/excel/', medical_views.export_medical_excel, name='export_medical_excel'),
    path('medical/export/pdf/', medical_views.export_medical_pdf, name='export_medical_pdf'),

    # Scouting
    path('scouting/', scouting_views.scouting_reports, name='scouting_reports'),
    path('scouting/export/excel/', scouting_views.export_scouting_excel, name='export_scouting_excel'),
    path('scouting/export/pdf/', scouting_views.export_scouting_pdf, name='export_scouting_pdf'),

    # Performance
    path('performance/', performance_views.performance_reports, name='performance_reports'),
    path('performance/export/excel/', performance_views.export_performance_excel, name='export_performance_excel'),
    path('performance/export/pdf/', performance_views.export_performance_pdf, name='export_performance_pdf'),

    # Mesocycle
    path('mesocycle/', mesocycle_views.mesocycle_reports, name='mesocycle_reports'),
    path('mesocycle/export/excel/', mesocycle_views.export_mesocycle_excel, name='export_mesocycle_excel'),
    path('mesocycle/export/pdf/', mesocycle_views.export_mesocycle_pdf, name='export_mesocycle_pdf'),

    # Fitness
    path('fitness/', fitness_views.fitness_reports, name='fitness_reports'),
    path('fitness/export/excel/', fitness_views.export_fitness_excel, name='export_fitness_excel'),
    path('fitness/export/pdf/', fitness_views.export_fitness_pdf, name='export_fitness_pdf'),

    # Individual Action Plan (IAP)
    path('iap/', iap_views.iap_reports, name='iap_reports'),
    path('iap/export/excel/', iap_views.export_iap_excel, name='export_iap_excel'),
    path('iap/export/pdf/', iap_views.export_iap_pdf, name='export_iap_pdf'),

    # Transition
    path('transition/', transition_views.transition_reports, name='transition_reports'),
    path('transition/export/excel/', transition_views.export_transition_excel, name='export_transition_excel'),
    path('transition/export/pdf/', transition_views.export_transition_pdf, name='export_transition_pdf'),

    # Results
    path('results/', result_views.result_reports, name='result_reports'),
    path('results/export/excel/', result_views.export_result_excel, name='export_result_excel'),
    path('results/export/pdf/', result_views.export_result_pdf, name='export_result_pdf'),

    #path('results/', results_view.results_list_view, name='results_list'),
    #path('results/export/excel/', results_view.results_export_excel, name='results_export_excel'),
    #path('results/export/pdf/', results_view.results_export_pdf, name='results_export_pdf'),



    # existing export URLs
    path('export/excel/<str:section>/', report_exports.export_section_excel, name='export_section_excel'),
    path('reports-dashboard/combined-excel/', report_exports.export_combined_excel, name='export_combined_excel'),
    path('reports-dashboard/combined-pdf/', report_exports.export_combined_pdf, name='export_combined_pdf'),


    path('team-reports/<int:team_id>/dashboard/', report_filters.reports_dashboard, name='reports_dashboard'),
    path('team-reports/<int:team_id>/', team_reports_view.team_reports_view, name='team_reports'),


    path("statistics/<int:team_id>/", statistics_view.statistics_list_view, name="statistics_list"),
    path("statistics/export/excel/", statistics_view.statistics_export_excel, name="statistics_export_excel"),
    path("statistics/export/pdf/", statistics_view.statistics_export_pdf, name="statistics_export_pdf"),



    path('match-report/<int:match_id>/', match_report_view.match_report_html, name='match_report'),
    path('match-report/<int:match_id>/download-pdf/', match_report_view.download_match_report_pdf, name='download_match_report_pdf'),






    # 1. intro pages
    #path('intro/post-match-summary/<int:match_id>/', post_match_summary.full_match_context_view, name='post_match_summary'),
    path('intro/in-possession/<int:match_id>/', intro_page.in_possession_view, name='in_possession'),
    path('intro/out-of-possession/<int:match_id>/', intro_page.out_of_possession_view, name='out_of_possession'),
    path('intro/goalkeeping/<int:match_id>/', intro_page.goalkeeping_view, name='goalkeeping'),
    path('intro/set-plays/<int:match_id>/', intro_page.set_plays_view, name='set_plays'),
    path('intro/individual-in-possession/<int:match_id>/', intro_page.individual_in_possession_view, name='individual_in_possession'),
    path('intro/individual-out-of-possession/<int:match_id>/', intro_page.individual_out_of_possession_view, name='individual_out_of_possession'),
    path('intro/individual-physical/<int:match_id>/', intro_page.individual_physical_view, name='individual_physical'),
    path('match-summary/<int:match_id>/summary-stats/', match_summary_stats.match_summary_stats_view, name='match_summary_stats'),

]

