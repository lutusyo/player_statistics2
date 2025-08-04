from django.urls import path
from . views import introduction_page

app_name = 'goalkeeping_app'

urlpatterns = [
    path('intro/<int:match_id>/', introduction_page.goalkeeping_intro, name='goalkeeping__intro_page'),
]
