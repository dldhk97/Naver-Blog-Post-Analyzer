import core_task
import cli_task

CLIENT_FUNCS = [
    [cli_task.get_analyzed_info, '게시글 분석 정보 보기'],
    [cli_task.get_keyword, '게시글 키워드 미리보기'],
    [cli_task.get_bloginfo, '게시글 미리보기'],
    [cli_task.send_feedback, '피드백 남기기'],
]
ADMIN_FUNCS = [
    [None, '피드백 조회'],
    [None, '피드백 삭제'],
    [None, '피드백 저장'],
    [None, 'Ban IP'],
    [None, 'Ban IP 조회'],
    [None, 'Unban IP'],
    [None, '모델 학습'],
    [None, '모델 불러오기'],
    [None, '모델 저장하기'],
]
TEST_FUNCS = [
    [core_task.load_module, '모듈 로드'],
    [core_task.lorem_analyze, '로렘 분석'],
    [core_task.crawl_by_search_word, '검색어로 크롤링하기'],
    [core_task.crawl_single_post, 'URL로 한 게시글 크롤링하기'],
    [core_task.crawl_multimedia, 'URL로 한 게시글 멀티미디어 크롤링하기'],
    [core_task.get_analyzed_info, 'URL 목록 전송하여 분석결과 반환'],
]

MENU_DICTS = [
    [CLIENT_FUNCS, '클라이언트 메뉴 보기'],
    [ADMIN_FUNCS, '관리자 메뉴 보기'],
    [TEST_FUNCS, '테스트 메뉴 보기'],
]

def main_loop(funcs):
    while True:
        print(' ')
        i = 1
        for d in funcs:
            print(str(i) + '. ' + d[1])
            i += 1
        print('q. 나가기')

        user_input = input('메뉴 선택 : ')
        if user_input == 'q':
            return 0
        

        try:
            user_input = int(user_input) - 1
            selected_funcs = funcs[user_input][0]

            if callable(selected_funcs):
                selected_funcs()
            else:
                main_loop(selected_funcs)

        except Exception as e:
            print('[SYSTEM][main_loop]', e)
            # return -1
        
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