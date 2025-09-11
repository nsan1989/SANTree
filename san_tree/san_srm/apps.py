from django.apps import AppConfig


class SanSrmConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'san_srm'

    def ready(self):
        from .scheduler import start
        start()
