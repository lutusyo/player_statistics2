# reports_app/urls.py
from django.urls import path

from version1.reports_app.views.daily_report_views import ( mesocycle_views, report_exports, result_views,
    scouting_views, statistics_view, individual_statistics_view, team_reports_view, transition_views, report_filters)

from version1.reports_app.views.match_report_views import ( goalkeeping_view, set_plays_views, in_possession_views, 
    post_match_summary_views, full_match_report_views, summary_key_statistics_views,)

from version1.reports_app.views.match_report_views.full_match_report_views import full_match_report_view, download_full_report_pdf
from version1.reports_app.views.match_report_views import match_summary_team_view
from version1.reports_app.views.daily_report_views import technical_report_views
from version1.reports_app.views import aar_report_view

from version1.reports_app.views.daily_report_views.technical_report_views import (technical_report_page,)
from version1.reports_app.views2.download_technical_report_pdf import download_technical_report_pdf
from version1.reports_app.views2.download_technical_report_ppt import download_technical_report_ppt
from version1.reports_app.views2.download_technical_report_excel import download_technical_report_excel
from version1.reports_app.views2.preview_technical_report import preview_technical_report
from version1.reports_app.views2.rating import rate_player, player_rating_list

from version1.reports_app.views.training_min import training_minutes_entry
from version1.reports_app.views.training_dashboard import ( training_minutes_dashboard, )

from version1.reports_app.views2 import performance_potential_matrix

app_name = 'reports_app'
urlpatterns = [

    # Performance and potential rating
    path('teams/<int:team_id>/ratings/', player_rating_list, name='player_rating_list',),
    path('teams/<int:team_id>/players/<int:player_id>/rate/', rate_player, name='rate_player',),
    # path('player-rating/', player_rating.rate_players, name='player_rating'),

    path('performance-potential/', performance_potential_matrix.performance_potential_matrix, name='performance_potential_matrix'),
    path('performance-potential/', performance_potential_matrix.performance_potential_matrix, name='performance_potential_matrix'),

    #path("technical-report/<int:team_id>/", technical_report_views.download_technical_report_excel, name="download_technical_report"),
    path("technical-report/<int:team_id>/", technical_report_page, name="technical_report_page",),
    path("technical-report/<int:team_id>/preview/", preview_technical_report, name="technical_report_preview",),

    path("technical-report/<int:team_id>/excel/",download_technical_report_excel,name="technical_report_excel2",),
    path("technical-report/<int:team_id>/pdf/",download_technical_report_pdf,name="technical_report_pdf2",),
    path("technical-report/<int:team_id>/ppt/",download_technical_report_ppt,name="technical_report_ppt2",),

    # Medical


    # Scouting
    path('scouting/<int:team_id>/', scouting_views.scouting_reports, name='scouting_reports'),
    path('scouting/<int:team_id>/export/excel/', scouting_views.export_scouting_excel, name='export_scouting_excel'),
    path('scouting/<int:team_id>/export/pdf/', scouting_views.export_scouting_pdf, name='export_scouting_pdf'),

    # Performance


    # Mesocycle
    path('mesocycle/<int:team_id>/', mesocycle_views.mesocycle_reports, name='mesocycle_reports'),
    path('mesocycle/<int:team_id>/export/excel/', mesocycle_views.export_mesocycle_excel, name='export_mesocycle_excel'),
    path('mesocycle/<int:team_id>/export/pdf/', mesocycle_views.export_uploaded_mesocycle_pdf, name='export_mesocycle_pdf'),
    path('team/<int:team_id>/export-all-pdfs/', mesocycle_views.export_all_mesocycle_pdfs, name='export_all_mesocycle_pdfs'),

    # Fitness
  
    # IAP

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

    # Individual statistics
    path("player/<int:player_id>/report/", individual_statistics_view.player_report_view, name='individual_statistics'),
    path("player/<int:player_id>/report/excel/", individual_statistics_view.player_report_export_excel, name='player_report_excel'),
    path("player/<int:player_id>/report/pdf/", individual_statistics_view.player_report_export_pdf, name="player_report_pdf"),

    # Dashboards
    path('team-reports/<int:team_id>/dashboard/', report_filters.reports_dashboard, name='reports_dashboard'),
    path('team-reports/<int:team_id>/', team_reports_view.team_reports_view, name='team_reports'),

    # existing export URLs
    path('export/excel/<str:section>/', report_exports.export_section_excel, name='export_section_excel'),
    path('reports-dashboard/combined-excel/', report_exports.export_combined_excel, name='export_combined_excel'),
    path('reports-dashboard/combined-pdf/', report_exports.export_combined_pdf, name='export_combined_pdf'),
    path('team-reports/<int:team_id>/dashboard/', report_filters.reports_dashboard, name='reports_dashboard'),
    path('team-reports/<int:team_id>/', team_reports_view.team_reports_view, name='team_reports'),

    # 1. Post match summary,Key statS,team,In possession,         Goalkeeping,Set plays
    path('match/<int:match_id>/post-match-summary/', post_match_summary_views.full_match_context_view, name='post_match_summary'),
    path("match/<int:match_id>/summary-key-statistics/",summary_key_statistics_views.summary_key_statistics_view, name="summary_key_statistics"),
    path("match-lineup/<int:match_id>/", match_summary_team_view.match_lineup_report, name="match_lineup_report"),
    path('match/<int:match_id>/attempt-to-goal-dashboard/', in_possession_views.attempt_to_goal_dashboard,name='attempt_to_goal_dashboard'),
    #path("shotmap/<int:match_id>/<str:team_type>/", in_possession_views.create_shotmap_base64, name="generate_shotmap"),

    path("match/<int:match_id>/goalkeeping/", goalkeeping_view.goalkeeping_view,name="goalkeeping_report"),
    path('match/<int:match_id>/setplays/', set_plays_views.setplays_dashboard, name='setplays_dashboard'),

    # 9. physical data
    # Full report
    path('match/<int:match_id>/<int:our_team_id>/full-report/',full_match_report_views.full_match_report_view,name='full_match_report'),
    path('match/<int:match_id>/download-pdf/', download_full_report_pdf,name='download_full_report_pdf'),

    path("aar/<int:report_id>/", aar_report_view.after_action_review_detail, name="aar_detail"),
    path("aar/<int:report_id>/pdf/", aar_report_view.download_aar_pdf, name="aar_pdf"),
    path("aar/<int:report_id>/ppt/", aar_report_view.download_aar_ppt, name="aar_ppt"),

    # Training minutes
    path( "training-minutes/", training_minutes_entry, name="training_minutes_entry",),
    path( "training-minutes/dashboard/", training_minutes_dashboard, name="training_minutes_dashboard",),
]


