def admin_authorization(json_data):

    admin_id = json_data['id']
    admin_pw = json_data['pw']

    # 인증
    result = True

    response = {}
    response['task_type'] = 'admin_authorization'
    
    if result:
        response['success'] = 'True'
        response['message'] = 'Authorization success!'
    else:
        response['success'] = 'False'
        response['message'] = 'Authorization failed!'

    return response