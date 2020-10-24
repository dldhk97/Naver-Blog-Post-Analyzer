from analyzer import lorem_analyzer
from crawler import naver_blog_post_crawler
from crawler import multimediacrawler
from db import db_connector

# 프린트 메뉴 코드
def print_menu():
    print('1. 모듈 로드')
    print('2. 원본 문장 생성')
    print('3. 부자연스러움 분석')
    print('4. 검색어로 크롤링하기')
    print('5. URL로 한 게시글 크롤링하기')
    print('6. URL로 한 게시글 멀티미디어 크롤링하기')
    print('7. DB 연결 테스트')
    print('q. 종료')

def task_org_create_sent():
    user_word = input('단어 입력 : ')
    created_sent = lorem_analyzer.org_craete_sent(user_word)
    print('생성된 문장 : ')
    print(created_sent)

def task_get_distance():
    user_sent = input('문장 입력 : ')
    distances = lorem_analyzer.get_distance(user_sent)
    mean, variance, standard_deviation = lorem_analyzer.distance_describe(distances)

    distances_with_token = lorem_analyzer.distances_with_token(user_sent, distances)
    print('')
    print('토큰 : ')
    print(str(distances_with_token[0]))
    print(str(distances_with_token[1]))
    # 평균값 내보기
    print('평균값 : ' + str(mean))
    # 분산 내보기
    print('분산 : ' + str(variance))
    # 표준편차 구하기
    print('표준편차 : ' + str(standard_deviation))
    print('')

def task_crawltask_crawl_by_search_word():
    print('검색어 : ')
    search_word = input()
    if search_word is not None:
        print('크롤링할 포스트의 개수 : ')
        blog_post_count = input()
        try:
            if blog_post_count.isdigit:
                naver_blog_post_crawler.crawl_by_search_word(search_word, int(blog_post_count))
            else:
                print('크롤링할 포스트의 개수가 올바르지 않습니다.')
        except Exception as e:
            print(e)
    else:
        print('검색어가 올바르지 않습니다.')

def task_crawl_single_post():
    print('URL : ')
    url = input()
    if url is not None:
        naver_blog_post_crawler.crawl_single_post(url)
    else:
        print('URL이 올바르지 않습니다.')

def task_crawl_multimedia():
    print('URL : ')
    url = input()
    if url is not None:
        images_ratio, imos_ratio, videos_ratio, hyperlinks_ratio, etcs_ratio, texts_ratio, lefts_ratio = multimediacrawler.get_multimedia(url)
        
        # 멀티미디어 종류별 비율 표시
        print('이미지의 비율 : ', str(round(images_ratio, 3) * 100), '%')
        print('이모티콘의 비율 : ', str(round(imos_ratio, 3) * 100), '%')
        print('비디오의 비율 : ', str(round(videos_ratio, 3) * 100), '%')
        print('하이퍼링크 비율 : ', str(round(hyperlinks_ratio, 3) * 100), '%')
        print('기타(iframe) 비율 : ', str(round(etcs_ratio, 3) * 100), '%')
        print('텍스트 비율 : ', str(round(texts_ratio, 3) * 100), '%')
        print('공백 비율 : ', str(round(lefts_ratio, 3) * 100), '%')
    else:
        print('URL이 올바르지 않습니다.')

def task_test_db_connection():
    db_connector.test_connection()
    pass


def cli_loop():
    while True:
        print_menu()
        user_input = input('메뉴 선택 : ')
        if user_input == '1':
            lorem_analyzer.load_module()

        elif user_input == '2':
            task_org_create_sent()

        elif user_input == '3':
            task_get_distance()

        elif user_input == '4':
            task_crawltask_crawl_by_search_word()

        elif user_input == '5':
            task_crawl_single_post()

        elif user_input == '6':
            task_crawl_multimedia()

        elif user_input == '7':
            task_test_db_connection()

        elif user_input == 'q':
            return 0
        