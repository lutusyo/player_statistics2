# tagging_app/urls.py
from django.urls import path
from tagging_app.views  import attempt_to_goal, goalkeeper_distribution, pass_network, tagging_view, current_players, attempt_to_goal_opp
from tagging_app import views
from tagging_app.views import current_players

from tagging_app.views.output.summary_key_statistics import summary_key_statistics_view
from tagging_app.views.output import full_report, match_summary3, table_of_contents, post_match_summary

from tagging_app.views2 import delivery_type


app_name = 'tagging_app'

urlpatterns = [



    path('match/<int:match_id>/delivery-summary/', delivery_type.delivery_summary_view, name='delivery_summary'),



    path("full-report/<int:match_id>/<int:our_team_id>/", full_report.full_report_view, name="full_report"),

    #table of contents
    path("table-of-contents/<int:match_id>/<int:our_team_id>/", table_of_contents.table_of_contents_view, name="report_cover"),

    path('intro/post-match-summary/<int:match_id>/<int:our_team_id>/', post_match_summary.full_match_context_view, name='post_match_summary'),

    # kikosi
    path('match-summary/<int:match_id>/<int:team_id>/', match_summary3.match_summary_view, name='match_summary'),


    path('api_current_on_field_players/<int:match_id>/', current_players.api_current_on_field_players, name='api_current_on_field_players'),
    #path("current_players/<int:match_id>/", current_players.api_current_on_field_players, name="api_current_players"),
    path("match/<int:match_id>/api/outcome-counts/", attempt_to_goal.get_outcome_counts, name="get_outcome_counts"),

    # tagging_Dashboards
    path('dashboard/', tagging_view.tagging_dashboard, name='dashboard'),
    # Each section has five-5 urls of the view to:
    # (1)entering data (2)saving data (3)dashboard to view data (4) export  csv file (5) export pdf file

    # tagging_app/urls.py


    # Attempt to Goal enter data: our team
    path('match/<int:match_id>/attempt_to_goal/', attempt_to_goal.enter_attempt_to_goal, name='enter_attempt_to_goal'),

    # Attempt to Goal enter data: opp team 
    path('match/<int:match_id>/attempt_to_goal_opp/', attempt_to_goal_opp.enter_attempt_to_goal_opp, name='enter_attempt_to_goal_opp'),



    path('match/save-attempt-to-goal/', attempt_to_goal.save_attempt_to_goal, name='save_attempt_to_goal'),

    path('api/save_opponent_attempt/', attempt_to_goal_opp.save_attempt_to_goal_opp, name='save_opponent_attempt_to_goal'),

    path('match/<int:match_id>/attempt-to-goal-dashboard/', attempt_to_goal.attempt_to_goal_dashboard, name='attempt_to_goal_dashboard'),
    path('match/<int:match_id>/csv/export-attempt-to-goal-csv/',attempt_to_goal.export_attempt_to_goal_csv, name='export_attempt_to_goal_csv'),
    path('match/<int:match_id>/pdf/export-attempt-to-goal-pdf/',attempt_to_goal.export_attempt_to_goal_pdf, name='export_attempt_to_goal_pdf'),
    # acros multiple device
    path('match/<int:match_id>/live_state/', attempt_to_goal.get_live_tagging_state, name='get_live_tagging_state'),
    # update substitute api
    

    # Passing Network
    path('pass-network/<int:match_id>/', pass_network.pass_network_enter_data, name='pass_network_enter_data'),
    #path('match/<int:match_id>/pass-network/', pass_network.get_pass_network_data, name='enter_pass_network'),
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


    # All summary key statistics ( attempToGoal,Pass,Goalkeeper)
    path("summary_key_statistics/<int:match_id>/", summary_key_statistics_view, name="summary_key_statistics"),


]




    
