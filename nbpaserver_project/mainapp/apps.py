import sys, os

from django.apps import AppConfig
from .api.analyzer.lorem_analyzer import load_module
from .api.crawler.naverblogcrawler import init

# 상위폴더의 모듈 임포트
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
import constants


class MainappConfig(AppConfig):
    name = 'mainapp'

    # startup code
    def ready(self):
        print('[SYSTEM][MainappConfig] Run startup code')
        # load_module()
        init(constants.NaverAPI.NAVER_CLIENT_ID, constants.NaverAPI.NAVER_CLIENT_SECRET)
        

        print('[SYSTEM][MainappConfig] Startup code completed!')