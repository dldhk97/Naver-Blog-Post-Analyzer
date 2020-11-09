import sys, os

from django.apps import AppConfig
from .api.model_task import load_module
from .api.crawler import naverblogcrawler
from .api import auth_task

# 상위폴더의 모듈 임포트
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
import constants


class MainappConfig(AppConfig):
    name = 'mainapp'

    # startup code
    def ready(self):
        print('[SYSTEM][MainappConfig] Run startup code')
        # load_module()
        naverblogcrawler.init(constants.NaverAPI)
        auth_task.init(constants.AdminAccountInfo)

        print('[SYSTEM][MainappConfig] Startup code completed!')