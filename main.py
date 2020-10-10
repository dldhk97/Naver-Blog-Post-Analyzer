from analyzer import lorem_analyzer
from crawler import naver_blog_post_crawler

def run():
    print('Naver-Blog-Post_Analyzer server started')
    pass

def printMenu():
    print('1. 모듈 로드')
    print('2. 원본 문장 생성')
    print('3. 부자연스러움 분석')
    print('4. 검색어로 크롤링하기')
    print('5. URL로 한 게시글 크롤링하기')
    print('6. URL로 한 게시글 멀티미디어 크롤링하기')
    print('7. 종료')

def console():
    while True:
        printMenu()
        user_input = input('메뉴 선택 : ')
        if user_input == '1':
            lorem_analyzer.load_module()

        elif user_input == '2':
            user_word = input('단어 입력 : ')
            created_sent = lorem_analyzer.org_craete_sent(user_word)
            print('생성된 문장 : ')
            print(created_sent)
        
        elif user_input == '3':
            user_sent = input('문장 입력 : ')
            distances = lorem_analyzer.magic(user_sent)
            lorem_analyzer.magic_describe(user_sent, distances)

        elif user_input == '4':
            naver_blog_post_crawler.task_crawl_by_search_word()
            break

        elif user_input == '5':
            naver_blog_post_crawler.task_crawl_single_post()
            break

        elif user_input == '6':
            naver_blog_post_crawler.task_crawl_multimedia()
            break

        elif user_input == '7':
            break

if __name__ == '__main__':
    print('테스트 서버 시작')
    print('모듈 자동 로드')
    lorem_analyzer.load_module()
    console()
    print('테스트 서버 종료')

if __name__ == '__main__':
    run()