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
    'unknown'
]

def get_url_list_from_user():
    line_cnt = input('전송할 URL의 개수는? : ')

    print('URL : ')
    data_list = []

    for _ in range(int(line_cnt)):
        data = {}
        data['url'] = input()
        data_list.append(data)

def get_analyzed_info():
    url_list = get_url_list_from_user()
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
    
    print('Select feedback type.')
    i = 1
    for type in FEEDBACK_TYPE:
        print(str(i) + ') ' + type)
        i += 1

    user_input = int(input('feedback_type : ')) - 1
    feedback_type = FEEDBACK_TYPE[user_input]
    message = input('message : ')

    core_task.send_feedback(url, ip, feedback_type, message)