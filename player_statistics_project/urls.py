 # project/urls.py
from django.urls import path, include
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from accounts_app import views 

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts_app.urls')),
    path('players_app/', include('players_app.urls')),
    path('matches_app/', include('matches_app.urls',  namespace='matches_app')),
    path('actions_app/', include('actions_app.urls')),
    path('gps_app/', include('gps_app.urls')),
    path('', views.index, name='home'),
    path('teams/', include('teams_app.urls')),

    path('announcements/', include('announcements_app.urls')),

    #reports_app
    path('reports_app/', include('reports_app.urls')),

    #tagging_app
    path('tagging/', include('tagging_app.urls')),

    #defensive_app
    path('defensive/', include('defensive_app.urls')),
 


]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])

