import sys
import os

sys.path.insert(0, '/home/afcportal/player_statistics2')
os.environ['DJANGO_SETTINGS_MODULE'] = 'player_statistics_project.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
