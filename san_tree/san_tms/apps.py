from django.apps import AppConfig

class SanTmsConfig(AppConfig):
    name = 'san_tms'
    default_auto_field = 'django.db.models.BigAutoField'

    def ready(self):
        import san_tms.signals
