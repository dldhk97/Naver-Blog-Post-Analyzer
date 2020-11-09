from django.http import JsonResponse

import json

# for Forbidden(CSRF cookie not set)
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from .models import BlogInfo
from .api import core_task, feedback_task, model_task, ban_task, test_task, auth_task

# 분석 정보 요청 시
# 클라이언트로부터 url 목록을 받아와 BlogInfo, AnalyzedInfo, MultimediaRatio, Dictionary 등을 반환함.
@method_decorator(csrf_exempt, name='dispatch')
def get_analyzed_info(request):
    print('Request received from client')

    if request.method == 'POST':

        json_array = json.loads(request.body)

        result = core_task.get_analyzed_info(json_array)

        # send data to client 
        return JsonResponse(result)
    
    print('[SYSTEM]Do not handle get request.')
    pass

# 키워드 요청 시
@method_decorator(csrf_exempt, name='dispatch')
def get_keywords(request):
    pass

@method_decorator(csrf_exempt, name='dispatch')
def create_feedback(request):
    pass

################################
#          admin views         #
################################
# Feedback

@method_decorator(csrf_exempt, name='dispatch')
def get_feedbacks(request):
    pass

@method_decorator(csrf_exempt, name='dispatch')
def delete_feedback(request):
    pass

################################
# Ban

@method_decorator(csrf_exempt, name='dispatch')
def ban_ip(request):
    pass

@method_decorator(csrf_exempt, name='dispatch')
def get_banned_ip(request):
    pass

@method_decorator(csrf_exempt, name='dispatch')
def unban_ip(request):
    pass

################################
# Model


@method_decorator(csrf_exempt, name='dispatch')
def learn_model(request):
    pass

# 관리자에게서 아이디, 비밀번호를 받고 인증 후 모델 로드 후 결과 반환
@method_decorator(csrf_exempt, name='dispatch')
def load_model(request):
    print('[SYSTEM][views][load_model] Request received from client')

    if request.method == 'POST':
        json_data = json.loads(request.body)

        auth_result = auth_task.admin_authorization(json_data)

        if auth_result['success'] == 'True':
            load_result = model_task.load_module()
            return JsonResponse(load_result)
        else:
            return JsonResponse(auth_result)
    
    print('[SYSTEM]Do not handle get request.')
    pass

@method_decorator(csrf_exempt, name='dispatch')
def save_model(request):
    pass

################################
# Test

@method_decorator(csrf_exempt, name='dispatch')
def crawl_single_blog(request):
    pass

@method_decorator(csrf_exempt, name='dispatch')
def crawl_single_blog_multimedia(request):
    pass