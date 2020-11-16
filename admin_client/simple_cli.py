import cli_task

CLIENT_FUNCS = [
    [cli_task.get_analyzed_info, '게시글 분석 정보 보기'],
    [cli_task.get_keyword, '게시글 키워드 미리보기'],
    [cli_task.get_bloginfo, '게시글 미리보기'],
    [cli_task.send_feedback, '피드백 남기기'],
]
ADMIN_FUNCS = [
    [cli_task.manage_feedback, '피드백 관리'],
    [cli_task.manage_ban, 'Ban 사용자 관리'],
    [None, '모델 학습'],
    [None, '모델 불러오기'],
    [None, '모델 저장하기'],
]
TEST_FUNCS = [
    [cli_task.load_module, '모듈 로드'],
    [cli_task.lorem_analyze, '로렘 분석'],
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
        
