from django.apps import AppConfig
import os


class SanSrmConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'san_srm'

    def ready(self):
        import san_srm.signals

        if os.environ.get("RUN_MAIN", None) == "true":
            from . import scheduler
            scheduler.start()