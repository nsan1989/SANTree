from django.apps import AppConfig


class SanAmsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'san_ams'

    def ready(self):
        from .scheduler import start
        start()
