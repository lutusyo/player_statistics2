# tagging_app/urls.py
from django.urls import path
from .views  import attempt_to_goal, goalkeeper_distribution, pass_network, tagging_view
from tagging_app.views.goal_and_pass_enter import tagging_base_view

app_name = 'tagging_app'

urlpatterns = [
    # tagging_Dashboards
    path('dashboard/', tagging_view.tagging_dashboard, name='dashboard'),
    # Each section has five-5 urls of the view to:
    # (1)entering data (2)saving data (3)dashboard to view data (4) export  csv file (5) export pdf file

    path('match/<int:match_id>/goal_and_pass_enter/', tagging_base_view, name='tagging_base'),


    # Attempt to Goal
    #path('match/<int:match_id>/attempt-to-goal/', attempt_to_goal.enter_attempt_to_goal, name='enter_attempt_to_goal'),
    path('match/save-attempt-to-goal/', attempt_to_goal.save_attempt_to_goal, name='save_attempt_to_goal'),
    path('match/<int:match_id>/attempt-to-goal-dashboard/', attempt_to_goal.attempt_to_goal_dashboard, name='attempt_to_goal_dashboard'),
    path('match/<int:match_id>/csv/export-attempt-to-goal-csv/',attempt_to_goal.export_attempt_to_goal_csv, name='export_attempt_to_goal_csv'),
    path('match/<int:match_id>/pdf/export-attempt-to-goal-pdf/',attempt_to_goal.export_attempt_to_goal_pdf, name='export_attempt_to_goal_pdf'),
    # acros multiple device
    path('match/<int:match_id>/live_state/', attempt_to_goal.get_live_tagging_state, name='get_live_tagging_state'),
    # update substitute api
    

    # Passing Network
    #path('match/<int:match_id>/pass-network/', pass_network.pass_network_page, name='enter_pass_network'),
    path('match/save-pass-network/', pass_network.save_pass_network, name='save_pass_network'),
    path('match/<int:match_id>/pass-network-dashboard/', pass_network.pass_network_dashboard, name='pass_network_dashboard'),
    path('match/<int:match_id>/csv/export-pass-network-csv/', pass_network.export_pass_network_csv, name='export_pass_network_csv'),
    path('match/<int:match_id>/excel/export-pass-network-excel/', pass_network.export_pass_network_excel, name='export_pass_network_excel'),
    path('match/<int:match_id>/pdf/export-pass-network-pdf/', pass_network.export_pass_network_pdf, name='export_pass_network_pdf'),

    # Goalkeeper Distribution
    path('match/<int:match_id>/goalkeeper_distibution/', goalkeeper_distribution.goalkeeper_distribution_page, name='enter_goalkeeper_distribution'),
    path('match/<int:match_id>/save-goalkeeper-distribution/', goalkeeper_distribution.save_goalkeeper_distribution, name='save_goalkeeper_distribution'),
    path('match/<int:match_id>/goalkeeper-distribution-dashboard/', goalkeeper_distribution.goalkeeper_distribution_dashboard, name='goalkeeper_distribution_dashboard'),
    path('match/<int:match_id>/csv/export-goalkeeper-distribution-csv/', goalkeeper_distribution.export_goalkeeper_distribution_csv, name='export_goalkeeper_distribution_csv'),
    path('match/<int:match_id>/pdf/export-goalkeeper-distribution-pdf/', goalkeeper_distribution.export_goalkeeper_distribution_pdf, name='export_goalkeeper_distribution_pdf'),
]




    
