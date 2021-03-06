from django.http import JsonResponse

import json

# for Forbidden(CSRF cookie not set)
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from .models import BlogInfo
from .api import core_task, mlmodel_task, test_task, auth_task

# 분석 정보 요청 시
# 클라이언트로부터 url 목록을 받아와 BlogInfo, AnalyzedInfo, MultimediaRatio, Dictionary 등을 반환함.

HTTP_METHOD_NAMES = ['POST', 'OPTIONS']

def check_banned_ip(request):
    is_banned, reason = core_task.is_banend_ip(request)
    if is_banned:
        response = []
        header = {}
        header['success'] = 'False'
        header['message'] = '밴 IP이기 때문에 요청이 거부되었습니다.\n사유 : ' + reason
        header['banned'] = 'True'
        response.append(header)
        
        return response
    return None

@method_decorator(csrf_exempt, name='dispatch')
def get_analyzed_info(request):
    if request.method in HTTP_METHOD_NAMES:

        res = check_banned_ip(request)
        if res:
            return JsonResponse(res, safe=False)

        json_array = json.loads(request.body)

        result = core_task.get_entire_info_from_urls(json_array)

        # send data to client 
        return JsonResponse(result, safe=False)
    
    print('[SYSTEM]Do not handle get request.')

# 키워드 요청 시
@method_decorator(csrf_exempt, name='dispatch')
def get_keyword(request):
    if request.method in HTTP_METHOD_NAMES:
        
        res = check_banned_ip(request)
        if res:
            return JsonResponse(res, safe=False)
    
        json_array = json.loads(request.body)

        result = core_task.get_keyword(json_array)

        # send data to client 
        return JsonResponse(result, safe=False)
    
    print('[SYSTEM]Do not handle get request.')

# 블로그 정보(미리보기) 요청 시
@method_decorator(csrf_exempt, name='dispatch')
def get_bloginfo(request):
    if request.method in HTTP_METHOD_NAMES:

        res = check_banned_ip(request)
        if res:
            return JsonResponse(res, safe=False)
    
        json_array = json.loads(request.body)

        result = core_task.get_bloginfo(json_array)

        # send data to client 
        return JsonResponse(result, safe=False)
    
    print('[SYSTEM]Do not handle get request.')

# 피드백 생성시
@method_decorator(csrf_exempt, name='dispatch')
def send_feedback(request):
    if request.method in HTTP_METHOD_NAMES:

        res = check_banned_ip(request)
        if res:
            return JsonResponse(res, safe=False)
        
        json_data = json.loads(request.body)

        result = core_task.send_feedback(json_data, request)

        # send data to client 
        return JsonResponse(result, safe=False)
    
    print('[SYSTEM]Do not handle get request.')

################################
#          admin views         #
################################
# Feedback

@method_decorator(csrf_exempt, name='dispatch')
def get_feedbacks(request):
    if request.method in HTTP_METHOD_NAMES:
        
        json_data = json.loads(request.body)

        result = core_task.get_feedback(json_data)

        # send data to client 
        return JsonResponse(result, safe=False)
    
    print('[SYSTEM]Do not handle get request.')

@method_decorator(csrf_exempt, name='dispatch')
def delete_feedback(request):
    if request.method in HTTP_METHOD_NAMES:
        
        json_data = json.loads(request.body)

        result = core_task.delete_feedback(json_data)

        # send data to client 
        return JsonResponse(result, safe=False)
    
    print('[SYSTEM]Do not handle get request.')

################################
# Ban

@method_decorator(csrf_exempt, name='dispatch')
def ban_user(request):
    if request.method in HTTP_METHOD_NAMES:
        
        json_data = json.loads(request.body)

        result = core_task.ban_user(json_data)

        # send data to client 
        return JsonResponse(result, safe=False)
    
    print('[SYSTEM]Do not handle get request.')

@method_decorator(csrf_exempt, name='dispatch')
def get_banned_user(request):
    if request.method in HTTP_METHOD_NAMES:
        
        json_data = json.loads(request.body)

        result = core_task.get_banned_user(json_data)

        # send data to client 
        return JsonResponse(result, safe=False)
    
    print('[SYSTEM]Do not handle get request.')

@method_decorator(csrf_exempt, name='dispatch')
def unban_user(request):
    if request.method in HTTP_METHOD_NAMES:
        
        json_data = json.loads(request.body)

        result = core_task.unban_user(json_data)

        # send data to client 
        return JsonResponse(result, safe=False)
    
    print('[SYSTEM]Do not handle get request.')

################################
# Model


@method_decorator(csrf_exempt, name='dispatch')
def learn_model(request):
    pass

# 관리자에게서 아이디, 비밀번호를 받고 인증 후 모델 로드 후 결과 반환
@method_decorator(csrf_exempt, name='dispatch')
def load_model(request):
    if request.method == 'GET':
        load_result = mlmodel_task.mlload_module()

        return JsonResponse(load_result)
    
    print('[SYSTEM]Do not handle get request.')
    pass

@method_decorator(csrf_exempt, name='dispatch')
def save_model(request):
    pass

################################
# Test

@method_decorator(csrf_exempt, name='dispatch')
def authorization(request):
    if request.method in HTTP_METHOD_NAMES:
        json_data = json.loads(request.body)

        auth_result = auth_task.admin_authorization(json_data)

        return JsonResponse(auth_result)
    
    print('[SYSTEM]Do not handle get request.')
    pass

@method_decorator(csrf_exempt, name='dispatch')
def lorem_analyze(request):
    if request.method in HTTP_METHOD_NAMES:
        json_data = json.loads(request.body)

        analyzed_data = test_task.lorem_analyze(json_data)

        return JsonResponse(analyzed_data)
    
    print('[SYSTEM]Do not handle get request.')
    pass

@method_decorator(csrf_exempt, name='dispatch')
def analyze_post_body(request):
    if request.method in HTTP_METHOD_NAMES:
        json_data = json.loads(request.body)

        analyzed_data = test_task.analyze_post_body(json_data)

        return JsonResponse(analyzed_data)
    
    print('[SYSTEM]Do not handle get request.')
    pass

@method_decorator(csrf_exempt, name='dispatch')
def crawl_by_search_word(request):
    if request.method in HTTP_METHOD_NAMES:
        json_data = json.loads(request.body)

        analyzed_data = test_task.crawl_by_search_word()

        return JsonResponse(analyzed_data)
    
    print('[SYSTEM]Do not handle get request.')
    pass

@method_decorator(csrf_exempt, name='dispatch')
def crawl_single_blog(request):
    pass

@method_decorator(csrf_exempt, name='dispatch')
def crawl_single_blog_multimedia(request):
    pass