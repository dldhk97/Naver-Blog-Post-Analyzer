import requests, json

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

def get_feedback(ip=None, feedback_type_name=None):
    '''
    ip, 피드백 유형으로 피드백 조회
    '''
    request_url = HOST_URL_HEAD + 'admin/feedback/get'

    try:    
        data = {}
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
                
                for feedback in feedbacks:
                    print(feedback)

                return True
            else:    
                print('[SERVER]', response_data['message'])
                return False

        print('[CLEINT][core_task] send_feedback error occured! Status_code is not 200 or 201!')
    except Exception as e:
        print('[CLEINT][core_task] send_feedback exception occured.\n', e)