import core_task

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


def cli_loop():
    while True:
        print_menu()
        user_input = input('메뉴 선택 : ')
        if user_input == '1':
            core_task.load_module()

        elif user_input == '2':
            core_task.org_create_sent()

        elif user_input == '3':
            core_task.get_distance()

        elif user_input == '4':
            core_task.crawl_by_search_word()

        elif user_input == '5':
            core_task.crawl_single_post()

        elif user_input == '6':
            core_task.crawl_multimedia()

        elif user_input == '7':
            core_task.test_db_connection()

        elif user_input == 'q':
            return 0
        