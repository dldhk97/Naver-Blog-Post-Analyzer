import requests, json
import constants
import file_task

HOST_IP = constants.ServerInfo.CONNECTION_INFO['default']['HOST']
HOST_PORT = constants.ServerInfo.CONNECTION_INFO['default']['PORT']
HOST_URL_HEAD = 'http://' + HOST_IP + ':' + HOST_PORT + '/request/'

def authorization(admin_id, admin_pw):
    request_url = HOST_URL_HEAD + 'admin/test/authorization'

    try:
        data = {}
        data['id'] = admin_id
        data['pw'] = admin_pw
        
        json_data = json.dumps(data)
        
        response = requests.post(request_url, data=json_data)

        if response.status_code == 200 or response.status_code == 201:
            json_data = json.loads(response.text)
            if json_data['success'] == 'True':
                return True
            else:    
                print('[SERVER]', json_data['message'])
                return False

        print('[CLEINT][core_task] Authorization failed! Status_code is not 200 or 201!')
    except Exception as e:
        print('[CLEINT][core_task] Exception occured at authorization\n', e)

def load_module():
    request_url = HOST_URL_HEAD + 'admin/model/load'

    try:        
        response = requests.get(request_url)

        if response.status_code == 200 or response.status_code == 201:
            json_data = json.loads(response.text)
            print('[SERVER]', json_data['message'])
            return True

        print('[CLEINT][core_task] Load_module failed! Status_code is not 200 or 201!')
    except Exception as e:
        print('[CLEINT][core_task] Failed to load_module.\n', e)

def lorem_analyze(sents):
    request_url = HOST_URL_HEAD + 'admin/test/lorem_analyze'
    
    try:
        data = {}
        data['sents'] = sents
        
        json_data = json.dumps(data)
        
        response = requests.post(request_url, data=json_data)

        if response.status_code == 200 or response.status_code == 200:
            json_data = json.loads(response.text)
            if json_data['success'] == 'True':
                print('')
                print('확률 : ')
                print(json_data['distances'])
                print('토큰 : ')
                print(json_data['tokens'])
                print('평균값 : ' + json_data['mean'])
                # 분산 내보기
                print('분산 : ' + json_data['variance'])
                # 표준편차 구하기
                print('표준편차 : ' + json_data['standard_deviation'])
                print('로렘 확률 : ' + json_data['lorem_percentage'])
                print('')

                return True
            else:    
                print('[SERVER]', json_data['message'])
                return False

        print('[CLEINT][core_task] Lorem_analyze error occured! Status_code is not 200 or 201!')
    except Exception as e:
        print('[CLEINT][core_task] Lorem_analyze exception occured.\n', e)

def print_blog_entire_info(blog_info, analyzed_info, multimedia_ratios, tags, hyperlinks, keywords):
    if blog_info:
        blog_info = blog_info['fields']
        print(blog_info)

    if analyzed_info:
        analyzed_info = analyzed_info['fields']
        print(analyzed_info)

    if multimedia_ratios:
        for multimedia_ratio in multimedia_ratios:
            mr = multimedia_ratio['fields']
            print(mr)

    if tags:
        for tag in tags:
            t = tag['fields']
            print(t)

    if hyperlinks:
        for hyperlink in hyperlinks:
            h = hyperlink['fields']
            print(h)

    if keywords:
        for keyword in keywords:
            k = keyword['fields']
            print(k)

    pass

def get_analyzed_info(data_list):
    '''
    URL 목록 딕셔너리를 입력받으면 서버로 보내고 결과 출력
    '''
    request_url = HOST_URL_HEAD + 'admin/test/getanalyzedinfo'
    
    try:
        json_data = json.dumps(data_list)
        
        response = requests.post(request_url, data=json_data)

        if response.status_code == 200 or response.status_code == 200:
            blog_entire_info_arr = json.loads(response.text)

            header_data = blog_entire_info_arr[0]
                
            if header_data['success'] == 'True':
                for info in blog_entire_info_arr[1:]:
                    analyzed_info = None
                    multimedia_ratios = None
                    keywords = None
                    blog_info = json.loads(info['blog_info'])[0]
                    if 'analyzed_info' in info:
                        analyzed_info = json.loads(info['analyzed_info'])[0]
                        
                    if 'multimedia_ratios' in info:
                        multimedia_ratios = json.loads(info['multimedia_ratios'])
                    
                    tags = json.loads(info['tags'])
                    hyperlinks = json.loads(info['hyperlinks'])
                    if 'keywords' in info:
                        keywords = json.loads(info['keywords'])
                    
                    print_blog_entire_info(blog_info, analyzed_info, multimedia_ratios, tags, hyperlinks, keywords)
                    
                return True
            else:    
                print('[SERVER]', header_data['message'])
                return False

        print('[CLEINT][core_task] get_analyzed_info error occured! Status_code is not 200 or 201!')
    except Exception as e:
        print('[CLEINT][core_task] get_analyzed_info exception occured.\n', e)

def get_keyword(url):
    '''
    URL 하나만 서버로 보내서, 해당 게시글의 키워드목록 가져옴
    '''
    request_url = HOST_URL_HEAD + 'user/keyword/get'
    
    try:
        data = {}
        data['url'] = url
        json_data = json.dumps(data)
        
        response = requests.post(request_url, data=json_data)

        if response.status_code == 200 or response.status_code == 200:
            response_data = json.loads(response.text)
                
            if response_data['success'] == 'True':
                keywords = json.loads(response_data['keywords'])
                
                for keyword in keywords:
                    k = keyword['fields']
                    print(k)

                return True
            else:    
                print('[SERVER]', response_data['message'])
                return False

        print('[CLEINT][core_task] get_keywords error occured! Status_code is not 200 or 201!')
    except Exception as e:
        print('[CLEINT][core_task] get_keywords exception occured.\n', e)

def get_bloginfo(url):
    '''
    URL 하나만 서버로 보내서, 해당 게시글의 BlogInfo 가져옴
    '''
    request_url = HOST_URL_HEAD + 'user/bloginfo/get'
    
    try:
        data = {}
        data['url'] = url
        json_data = json.dumps(data)
        
        response = requests.post(request_url, data=json_data)

        if response.status_code == 200 or response.status_code == 200:
            response_data = json.loads(response.text)
                
            if response_data['success'] == 'True':
                blog_info = json.loads(response_data['blog_info'])
                blog_info = blog_info[0]['fields']
                print(blog_info)
                return True
            else:    
                print('[SERVER]', response_data['message'])
                return False

        print('[CLEINT][core_task] get_bloginfo error occured! Status_code is not 200 or 201!')
    except Exception as e:
        print('[CLEINT][core_task] get_bloginfo exception occured.\n', e)


def send_feedback(url, ip, feedback_type, message):
    '''
    url, ip, 피드백 타입, 메시지 등을 서버로 보내 피드백테이블에 저장하게 함.
    '''
    request_url = HOST_URL_HEAD + 'user/feedback/send'
    
    try:
        data = {}
        data['url'] = url
        data['ip'] = ip
        data['feedback_type'] = feedback_type
        data['message'] = message
        
        json_data = json.dumps(data)
        
        response = requests.post(request_url, data=json_data)

        if response.status_code == 200 or response.status_code == 200:
            response_data = json.loads(response.text)
                
            if response_data['success'] == 'True':
                msg = response_data['message']
                print('[SERVER', msg)
                return True
            else:    
                print('[SERVER]', response_data['message'])
                return False

        print('[CLEINT][core_task] send_feedback error occured! Status_code is not 200 or 201!')
    except Exception as e:
        print('[CLEINT][core_task] send_feedback exception occured.\n', e)

def get_feedback(id=None, ip=None, feedback_type_name=None):
    '''
    ip, 피드백 유형으로 피드백 조회
    '''
    request_url = HOST_URL_HEAD + 'admin/feedback/get'

    try:    
        data = {}
        if id:
            data['id'] = id
        if ip:
            data['ip'] = ip
        
        if feedback_type_name:
            data['feedback_type_name'] = feedback_type_name

        json_data = json.dumps(data)
        
        response = requests.post(request_url, data=json_data)

        if response.status_code == 200 or response.status_code == 200:
            response_data = json.loads(response.text)
                
            if response_data['success'] == 'True':
                feedbacks = json.loads(response_data['feedbacks'])
                return feedbacks
            else:    
                print('[SERVER]', response_data['message'])
                return None

        print('[CLEINT][core_task] get_feedback error occured! Status_code is not 200 or 201!')
    except Exception as e:
        print('[CLEINT][core_task] get_feedback exception occured.\n', e)

def delete_feedback(feedbacks):
    '''
    피드백 id로 조회된 모든 피드백 삭제
    '''
    request_url = HOST_URL_HEAD + 'admin/feedback/delete'

    try:    
        if not feedbacks:
            return

        data = {}
        data['feedbacks'] = feedbacks

        json_data = json.dumps(data)
            
        response = requests.post(request_url, data=json_data)

        if response.status_code == 200 or response.status_code == 200:
            response_data = json.loads(response.text)
                
            if response_data['success'] == 'True':
                print('[SERVER]', response_data['message'])
                return True
            else:    
                print('[SERVER]', response_data['message'])
                return False

        print('[CLEINT][core_task] get_feedback error occured! Status_code is not 200 or 201!')
    except Exception as e:
        print('[CLEINT][core_task] get_feedback exception occured.\n', e)

def save_feedback_as_csv(feedbacks, save_directory=None):
    file_task.save_as_csv(feedbacks, save_directory)

def get_banned_user(id=None, ip=None):
    '''
    id, ip로 banned_ip 조회
    '''
    request_url = HOST_URL_HEAD + 'admin/ban/get'

    try:    
        data = {}
        if id:
            data['id'] = id
        if ip:
            data['ip'] = ip

        json_data = json.dumps(data)
        
        response = requests.post(request_url, data=json_data)

        if response.status_code == 200 or response.status_code == 200:
            response_data = json.loads(response.text)
                
            if response_data['success'] == 'True':
                banned_users = json.loads(response_data['banned_users'])
                return banned_users
            else:    
                print('[SERVER]', response_data['message'])
                return None

        print('[CLEINT][core_task] get_banned_ip error occured! Status_code is not 200 or 201!')
    except Exception as e:
        print('[CLEINT][core_task] get_banned_ip exception occured.\n', e)

def ban_user(ip, reason):
    '''
    ip와 사유를 넣으면 서버로 전송
    '''
    request_url = HOST_URL_HEAD + 'admin/ban/ban'

    try:    
        if not ip:
            return

        data = {}
        data['ip'] = ip
        data['reason'] = reason

        json_data = json.dumps(data)
            
        response = requests.post(request_url, data=json_data)

        if response.status_code == 200 or response.status_code == 200:
            response_data = json.loads(response.text)
                
            if response_data['success'] == 'True':
                print('[SERVER]', response_data['message'])
                return True
            else:    
                print('[SERVER]', response_data['message'])
                return False

        print('[CLEINT][core_task] ban ip error occured! Status_code is not 200 or 201!')
    except Exception as e:
        print('[CLEINT][core_task] ban ip exception occured.\n', e)

def unban_user(banned_users):
    '''
    사용자 목록으로 Unban
    '''
    request_url = HOST_URL_HEAD + 'admin/ban/unban'

    try:    
        if not banned_users:
            return

        data = {}
        data['banned_users'] = banned_users

        json_data = json.dumps(data)
            
        response = requests.post(request_url, data=json_data)

        if response.status_code == 200 or response.status_code == 200:
            response_data = json.loads(response.text)
                
            if response_data['success'] == 'True':
                print('[SERVER]', response_data['message'])
                return True
            else:    
                print('[SERVER]', response_data['message'])
                return False

        print('[CLEINT][core_task] Unban ip error occured! Status_code is not 200 or 201!')
    except Exception as e:
        print('[CLEINT][core_task] Unban ip exception occured.\n', e)