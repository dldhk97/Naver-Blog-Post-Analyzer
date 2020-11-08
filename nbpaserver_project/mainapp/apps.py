from django.apps import AppConfig
from mainapp.server.analyzer.lorem_analyzer import load_module


class MainappConfig(AppConfig):
    name = 'mainapp'

    # startup code
    def ready(self):
        print('[SYSTEM][MainappConfig] Run startup code')
        # load_module()

        print('[SYSTEM][MainappConfig] Startup code completed!')