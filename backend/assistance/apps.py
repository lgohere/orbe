from django.apps import AppConfig


class AssistanceConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "assistance"

    def ready(self):
        """Import signals when app is ready"""
        import assistance.signals  # noqa
