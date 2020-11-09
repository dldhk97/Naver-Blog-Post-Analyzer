from .util.hasher import get_hash_value

ADMIN_ACCOUNT_INFO = None

def init(admin_account_info):
    global ADMIN_ACCOUNT_INFO
    ADMIN_ACCOUNT_INFO = admin_account_info

def admin_authorization(json_data):
    response = {}
    response['task_type'] = 'admin_authorization'
    response['success'] = 'False'
    response['message'] = '알 수 없는 오류! 인증에 실패하였습니다!'

    try:
        if not ADMIN_ACCOUNT_INFO:
            print('[SYSTEM][auth_task] Cannot load admin_account from constant.py!')
            response['message'] = 'constant.py로 부터 관리자 정보를 불러오는데 실패했습니다! 관리자에게 문의하세요.'
        else:
            # 인증
            admin_id = json_data['id']
            admin_pw = json_data['pw']

            # 해시값으로 비교함.
            input_id_hash = get_hash_value(admin_id)
            input_pw_hash = get_hash_value(admin_pw)

            if input_id_hash == ADMIN_ACCOUNT_INFO.ADMIN_ID_HASH:
                if input_pw_hash == ADMIN_ACCOUNT_INFO.ADMIN_PW_HASH:
                    response['success'] = 'True'
                    response['message'] = '인증 성공!'
                else:
                    response['message'] = '패스워드가 틀립니다!'
            else:
                response['message'] = 'ID가 틀립니다!'
    except Exception as e:
        print('[SYSTEM][auth_task] Error occured!', e)

    return response