import sys, os

from django.apps import AppConfig
from .api.model_task import load_module
from .api.crawler import naverblogcrawler, multimediacrawler
from .api import auth_task

# 상위폴더의 모듈 임포트
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
import constants


class MainappConfig(AppConfig):
    name = 'mainapp'

    # startup code
    def ready(self):
        print('[SYSTEM][MainappConfig] Run startup code')
        
        # 상수 전달
        naverblogcrawler.init(constants.NaverAPI)
        auth_task.init(constants.AdminAccountInfo)
        
        # KoGPT2 모듈 로드
        # load_module()
        # 셀레니움 준비
        # multimediacrawler.prepare_selenium()

        print('[SYSTEM][MainappConfig] Startup code completed!')