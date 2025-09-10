import os
from django.core.wsgi import get_wsgi_application

# Replace 'your_project' with your actual Django project folder name
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'player_statistics_project.settings')

application = get_wsgi_application()
