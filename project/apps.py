from django.apps import AppConfig
from django.db.models.signals import post_migrate

class ProjectConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'project'

    def ready(self):
        from .ai import train_model
        post_migrate.connect(train_model)



class ProjectConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'project'
