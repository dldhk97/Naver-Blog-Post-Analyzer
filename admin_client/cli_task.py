import core_task

FEEDBACK_TYPE = [
    'system',
    'low_lorem',
    'high_lorem',
    'low_hashtag',
    'high_hashtag',
    'low_ratio',
    'high_ratio',
    'etc',
    'unknown',
    '나가기'
]

def select_feedback_type(msg='Select feedback type.'):
    print(msg)
    i = 1
    for type in FEEDBACK_TYPE:
        print(str(i) + ') ' + type)
        i += 1

    try:
        user_input = int(input('feedback_type : ')) - 1
        feedback_type = FEEDBACK_TYPE[user_input]
        return feedback_type
    except Exception as e:
        return FEEDBACK_TYPE[len(FEEDBACK_TYPE) - 1]

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
        print('[CLEINT][cli_task]] Authorization exception occured', e)
        return False

def get_lines_from_user(type_name='입력하세요'):
    line_cnt = input('몇 줄(혹은 몇개)입니까? : ')

    print(type_name + ' : ')
    data_list = []

    for _ in range(int(line_cnt)):
        data_list.append(input())

    return data_list

def get_analyzed_info():
    urls_dict = get_lines_from_user('URL')

    url_list = []
    for url in urls_dict:
        data = {}
        data['url'] = url
        url_list.append(data)
    core_task.get_analyzed_info(url_list)

def get_keyword():
    url = input('url : ')
    core_task.get_keyword(url)

def get_bloginfo():
    url = input('url : ')
    core_task.get_bloginfo(url)

def send_feedback():
    url = input('url : ')
    ip = input('ip : ')

    feedback_type_name = select_feedback_type()
    if feedback_type_name == FEEDBACK_TYPE[len(FEEDBACK_TYPE) - 1]:
        print('취소하였습니다.')
        return
    message = input('message : ')

    core_task.send_feedback(url, ip, feedback_type_name, message)

def load_module():
    user_input = input('KoGPT2 모듈을 로드하겠습니까?(Y/N)')
    if (user_input == 'y') or (user_input == 'Y'):
        core_task.load_module()
    else:
        print('취소하였습니다.')

def lorem_analyze():
    lines = get_lines_from_user('글을 입력하세요')
    sents = ''
    for l in lines:
        sents += l + '\n'

    core_task.lorem_analyze(sents)

def crawl_by_search_word():
    word = input('검색어 : ')
    if word is None:
        print('검색어가 올바르지 않습니다.')
        return

    post_count = input('크롤링할 포스트의 개수 : ')
    if not post_count.isdigit:
        print('크롤링할 포스트의 개수가 올바르지 않습니다.')
        return

    core_task.crawl_by_search_word(word, post_count)

def crawl_single_post():
    url = input('URL : ')
    if url is None:
        print('URL이 올바르지 않습니다.')
        return

    core_task.crawl_single_post(url)

def crawl_multimedia():
    url = input('URL : ')
    if url is None:
        print('URL이 올바르지 않습니다.')
        return

    core_task.crawl_multimedia()

def get_feedback():
    ip = input('IP (없어도 무관): ')
    feedback_type_name = select_feedback_type('피드백 선택(없어도 무관):')
    
    if feedback_type_name == FEEDBACK_TYPE[len(FEEDBACK_TYPE) - 1]:
        feedback_type_name = None

    if ip is '':
        ip = None
    
    core_task.get_feedback(ip, feedback_type_name)