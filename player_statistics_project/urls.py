 # project/urls.py
from django.urls import path, include
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from version1.accounts_app import views 

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('version1.accounts_app.urls')),
    path('players_app/', include('version1.players_app.urls')),
    path('matches_app/', include('version1.matches_app.urls',  namespace='matches_app')),
    path('actions_app/', include('version1.actions_app.urls')),
    path('gps_app/', include('version1.gps_app.urls')),
    path('', views.index, name='home'),
    path('teams/', include('version1.teams_app.urls')),

    path('announcements/', include('version1.announcements_app.urls')),

    path('reports_app/', include('version1.reports_app.urls')),  #reports_app
    path('tagging/', include('version1.tagging_app.urls')),      #tagging_app
    path('defensive/', include('version1.defensive_app.urls')),  #defensive_app
    path('lineup_app/', include('version1.lineup_app.urls')),    #lineup
    path('performance_rating_app/', include('version1.perfomance_rating_app.urls')),
    path('training/', include('version1.training_app.urls')),
    path("sheets/", include("version1.sheets_generator_app.urls")), #sheets generator

    #############################
    path('tagging_v2/', include('version2.tagging_app_v2.urls')), #tagging_app_v2
    path('loans_app/', include('version1.loans_app.urls')), # loaned players

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)







if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])

