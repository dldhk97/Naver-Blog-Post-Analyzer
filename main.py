import simple_cli
from multiprocessing  import Process, Queue
from analyzer import lorem_analyzer
from crawler import naver_blog_post_crawler

def main_task():
    # 서버 listening

    exit_code = simple_cli.cli_loop()

    if exit_code == 0:
        print('정상적으로 종료합니다.')

if __name__ == '__main__':
    print('테스트 서버 시작')
    print('KoGPT2 모듈 로드')       # 모듈 로드를 해야 KoGPT2를 사용할 수 있음
    lorem_analyzer.load_module()

    main_task()

    