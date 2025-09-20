from django.apps import AppConfig


class SanCmsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'san_cms'

    def ready(self):
        import san_cms.signals
