from django.urls import path
from . import views

app_name = 'library_app'

urlpatterns = [

    # Library home page
    path('',views.library_home, name='library_home'),

    # Add to highlight
    path('add-to-highlight/<int:clip_id>/', views.add_to_highlight, name='add_to_highlight'),

    # Highlights page
    path('highlights/', views.highlights_list, name='highlights_list'),

    # Reels page
    path('reels/', views.reels_list, name='reels_list'),


    path('highlight/<int:highlight_id>/', views.view_highlight, name='view_highlight'),

    path('generate/<int:highlight_id>/', views.generate_reel, name='generate_reel'),

    path('delete/<int:highlight_id>/', views.delete_highlight,name='delete_highlight'),

    path('generate-action/<int:highlight_id>/', views.generate_reel_action, name='generate_reel_action'),
]