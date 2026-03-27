from django.apps import AppConfig

class TeamsAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'version1.teams_app'

    def ready(self):
        import version1.teams_app.signals