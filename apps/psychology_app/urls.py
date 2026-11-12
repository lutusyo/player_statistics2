
from django.urls import path

from .views import enter_data_views, display_data_views
from .views import home_page


app_name = 'psychology_app'

urlpatterns = [

    # Main pages
    path('', home_page.home, name='home'),
    path('dashboard/', display_data_views.dashboard, name='dashboard'),

    # Player pages
    path('players/', display_data_views.player_directory, name='player_directory'),
    path(
        'players/<int:player_id>/',
        display_data_views.player_profile,
        name='player_profile'
    ),

    # Assessment pages
    path('assessments/', enter_data_views.assessment_list, name='assessment_list'),
    path('assessment/add/', enter_data_views.add_assessment, name='add_assessment'),
    path(
        'assessment/<int:pk>/',
        enter_data_views.assessment_detail,
        name='assessment_detail'
    ),

    # AJAX / filtering
    path('filter-players/', enter_data_views.filter_players, name='filter_players'),

]
