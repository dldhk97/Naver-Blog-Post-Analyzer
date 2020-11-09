import core_task

# 프린트 메뉴 코드
def print_menu():
    print('1. 모듈 로드')
    print('2. 로렘 분석')
    print('3. 검색어로 크롤링하기')
    print('4. URL로 한 게시글 크롤링하기')
    print('5. URL로 한 게시글 멀티미디어 크롤링하기')
    print('6. DB 연결 테스트')
    print('q. 종료')


def cli_loop():
    while True:
        print_menu()
        user_input = input('메뉴 선택 : ')
        if user_input == '1':
            core_task.load_module()

        elif user_input == '2':
            core_task.lorem_analyze()

        elif user_input == '3':
            core_task.crawl_by_search_word()

        elif user_input == '4':
            core_task.crawl_single_post()

        elif user_input == '5':
            core_task.crawl_multimedia()

        elif user_input == '6':
            core_task.test_db_connection()

        elif user_input == 'q':
            return 0
        
def admin_authorization():
    print('관리자용 클라이언트 사용을 위해 로그인이 필요합니다.')
    try:
        while(True):
            admin_id = input('ID:')
            admin_pw = input('PW:')
            
            if core_task.authorization(admin_id, admin_pw):
                print('로그인 성공!')
                return True
            else:
                print('로그인에 실패하였습니다. 다시 시도해주세요.')

    except Exception as e:
        print('[CLEINT][simple_cli] Authorization exception occured', e)
        return False