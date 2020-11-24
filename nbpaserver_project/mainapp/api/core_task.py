import os, sys, json, time
import concurrent.futures
from django.db.models import Q
from django.core import serializers

from .. import models
from .crawler.util import url_normalization
from .crawler import naverblogcrawler
from .util import model_converter, request_util
from .task.task import Task, TaskType
from .task.task_manager import *
from .task.bloginfo_task import bloginfo_task

def blog_me_normalization(url):
    try:
        splited = url.split('/')
        head = splited[2]
        blog_id = head.split('.')
        blog_id = blog_id[0]
        log_no = splited[3]
        return "https://blog.naver.com/" + blog_id + '/' + log_no
    except Exception as e:
        print(e)
        return url

# 분석, 키워드 추출 등 핵심 메소드
def get_entire_info_from_urls(json_array):
    '''
    클라이언트에게 url 목록을 받으면 해당 게시글의 모든 정보(BlogInfo, AnalyzedInfo, tag, 를 반환함.
    '''
    json_data_list = []

    header = {}
    header['success'] = 'False'

    json_data_list.append(header)

    # 받아온 url 목록을 순차 탐색
    for json_obj in json_array:
        try:
            org_url = json_obj['url']

            # 블로그 게시글이 아니면 패스
            if 'blog.me' in org_url:
                org_url = blog_me_normalization(org_url)
            if 'blog.naver.com' not in org_url:
                continue

            target_url = url_normalization(org_url)

            # URL 정규화에 실패한 경우
            if not target_url:
                print(org_url + ' 은 제한된 블로그이거나, 비공개 게시글이입니다.')
                continue
            
            blog_info, tag_list, hyperlink_list = fetch_blog_info(target_url)

            if blog_info is None:
                print('[SYSTEM][core_task][fetch_entire_info_from_urls] Failed to fetch blog_info!')
                continue
            
            ###
            # 여기부턴 처리가 오래걸려서, 느리면 스레드 나누던지 해야할듯? 키워드 추출 알고리즘 & 로렘분석 & 멀티미디어 분석이 필요함.
            # 너무 코드가 길다. 함수로 나누자. 끔찍한 코드가 만들어지고 있음.
            # 키워드추출, 로렘분석, 멀티미디어 비율 분석을 멀테프로세스로 처리
            ###

            # 테이블 조회하고 정보가 없으면 작업 목록에 추가함.
            keyword_list = fetch_dictionary(blog_info, 'keyword')
            analyzedinfo_list = list(models.AnalyzedInfo.objects.filter(blog_info=blog_info))
            multimedia_ratio_list = list(models.MultimediaRatio.objects.filter(blog_info=blog_info))
            
            if len(keyword_list) <= 0:
                print('[SYSTEM][core_task] Keywords(' + blog_info.blog_id +', ' + blog_info.log_no + ') does not exists in database!')
                task = Task(TaskType.KEYWORD, blog_info.blog_id, blog_info.log_no, blog_info.url)
                task._dict['body'] = blog_info.body
                TaskManager.instance().add_task(task)

            analyzed_info = None
            if len(analyzedinfo_list) <= 0:
                print('[SYSTEM][core_task] AnalyzedInfo(' + blog_info.blog_id +', ' + blog_info.log_no + ') does not exists in database!')
                task = Task(TaskType.ANALYZE, blog_info.blog_id, blog_info.log_no, blog_info.url)
                task._dict['body'] = blog_info.body
                TaskManager.instance().add_task(task)
            else:
                analyzed_info = analyzedinfo_list[0]

            if len(multimedia_ratio_list) <= 0:
                print('[SYSTEM][core_task] MultimediaInfo(' + blog_info.blog_id +', ' + blog_info.log_no + ') does not exists in database!')
                task = Task(TaskType.MULTIMEDIA, blog_info.blog_id, blog_info.log_no, blog_info.url)
                task._dict['url'] = blog_info.url
                TaskManager.instance().add_task(task)

            # 한 URL에 대해 모든 분석 혹은 로드를 마쳤음. 메모리 안에 해당 게시글의 모든 정보가 존재함.
            # 수집한 녀석들을 Json으로 바꾼다.
            # 클라이언트에게 줘야할 녀석들은, BlogInfo, Dictionary, AnalyzedInfo, MultimediaRatio임.
            data = {}
            
            data['blog_info'] = serializers.serialize('json', [blog_info, ])
            if analyzed_info:
                data['analyzed_info'] = serializers.serialize('json', [analyzed_info, ])
            else:
                data['analyzed_info'] = serializers.serialize('json', [])

            data['tags'] = serializers.serialize('json', tag_list)
            data['hyperlinks'] = serializers.serialize('json', hyperlink_list)
            if len(keyword_list) > 0:
                data['keywords'] = serializers.serialize('json', keyword_list)
            else:
                data['keywords'] = serializers.serialize('json', [])
                
            if len(multimedia_ratio_list) > 0:
                data['multimedia_ratios'] = serializers.serialize('json', multimedia_ratio_list)
            else:
                data['multimedia_ratios'] = serializers.serialize('json', [])

            json_data_list.append(data)
        except Exception as e:
            print('[SYSTEM][core_task][fetch_entire_info_from_urls] AnalyzedInfo(' + target_url + ') failed to fetch_entire_info_from_urls.\n', e)
            header['message'] = '게시글 분석 정보를 불러오는 중 오류 발생!'

    if len(json_data_list) > 1:
        header['success'] = 'True'
        header['message'] = '게시물 분석 정보 로드하였음.'
    else:
        header['message'] = '게시물 분석 결과가 존재하지 않습니다. 올바른 URL을 제공해주세요.'

    return json_data_list

def get_keyword(json_data):

    json_data_list = []

    header = {}
    header['success'] = 'False'

    json_data_list.append(header)
    try:
        target_url = json_data['url']

        # 블로그 게시글이 아니면 패스
        if 'blog.naver.com' not in target_url:
            header['message'] = '네이버 블로그가 아닙니다!'
            return json_data_list

        target_url = url_normalization(target_url)
        
        blog_info, tag_list, hyperlink_list = fetch_blog_info(target_url)

        if blog_info is None:
            header['message'] = 'DB에 블로그 데이터가 존재하지 않습니다!'
            return json_data_list

        # 테이블 조회하고 정보가 없으면 작업 목록에 추가함.
        keyword_list = fetch_dictionary(blog_info, 'keyword')

        if len(keyword_list) <= 0:
            print('[SYSTEM][core_task] Keywords(' + blog_info.blog_id +', ' + blog_info.log_no + ') does not exists in database!')
            task = Task(TaskType.KEYWORD, blog_info.blog_id, blog_info.log_no, blog_info.url)
            task._dict['body'] = blog_info.body
            TaskManager.instance().add_task(task)

        if len(keyword_list) > 0:
            keywords_data = {}
            keywords_data['keywords'] = serializers.serialize('json', keyword_list)
            json_data_list.append(keywords_data)

            header['success'] = 'True'
            header['message'] = '키워드 정보 로드하였음.'
        else : 
            header['message'] = '키워드 정보를 추출하는 중입니다.'
    except Exception as e:
        print('[SYSTEM][core_task][get_keyword]\n', e)
        header['message'] = '키워드 분석 정보를 불러오는 중 오류 발생!'

    return json_data_list
    
def get_bloginfo(json_data):
    json_data_list = []

    header = {}
    header['success'] = 'False'

    json_data_list.append(header)

    try:
        target_url = json_data['url']

        # 블로그 게시글이 아니면 패스
        if 'blog.naver.com' not in target_url:
            header['message'] = '네이버 블로그가 아닙니다!'
            return json_data_list

        target_url = url_normalization(target_url)
        
        blog_info, tag_list, hyperlink_list = fetch_blog_info(target_url)

        if blog_info is None:
            header['message'] = 'DB에 블로그 데이터가 존재하지 않습니다!'
            return json_data_list
        
        blog_info_data = {}
        blog_info_data['blog_info'] = serializers.serialize('json', [blog_info, ])
        json_data_list.append(blog_info_data)
        header['success'] = 'True'
        header['message'] = '게시글 정보 로드하였음.'
    except Exception as e:
        print('[SYSTEM][core_task][get_bloginfo] AnalyzedInfo(' + target_url + ') failed to fetch_entire_info_from_urls.\n', e)
        header['message'] = '게시글 정보를 불러오는 중 오류 발생!'

    return json_data_list

def send_feedback(json_data, request):
    json_data_list = []

    header = {}
    header['success'] = 'False'

    json_data_list.append(header)

    try:
        target_url = json_data['url']

        if 'blog.naver.com' not in target_url:
            header['message'] = '네이버 블로그가 아닙니다!'
            return json_data_list

        target_url = url_normalization(target_url)
        
        blog_info, tag_list, hyperlink_list = fetch_blog_info(target_url)

        if blog_info is None:
            header['message'] = 'DB에 블로그 데이터가 존재하지 않습니다!'
            return json_data_list

        # 피드백 생성
        feedback = models.Feedback()
        feedback.blog_info = blog_info
        if 'ip' in json_data:
            feedback.ip = json_data['ip']
        else:
            feedback.ip = request_util.get_client_ip(request)

        feedback_type_str = json_data['feedback_type']
        feedback_type = models.FeedbackType.objects.filter(name=feedback_type_str)[0]
        feedback.feedback_type = feedback_type
        feedback.message = json_data['message']

        feedback.save()
        header['success'] = 'True'
        header['message'] = '피드백을 DB에 저장하는데 성공했습니다!'
        
    except Exception as e:
        print('[SYSTEM][core_task][send_feedback] FeedbackInfo(' + target_url + ') failed to fetch_entire_info_from_urls.\n', e)
        header['message'] = '피드백을 제출하는 도중 오류 발생!'

    return json_data_list

##########################################################################

def get_feedback(json_data):
    json_data_list = []

    header = {}
    header['success'] = 'False'

    json_data_list.append(header)

    try:
        id = None
        ip = None
        feedback_type_name = None
        
        if 'id' in json_data:
            id = json_data['id']
        
        if 'ip' in json_data:
            ip = json_data['ip']
        
        if 'feedback_type_name' in json_data:
            feedback_type_name = json_data['feedback_type_name']
        
        feedback_list = fetch_feedback(id=id, ip=ip, feedback_type_name=feedback_type_name)
        
        header['success'] = 'True'
        feedback_data = {}
        if len(feedback_list) > 0:
            feedback_data['feedbacks'] = serializers.serialize('json', feedback_list)
            header['message'] = '피드백 정보 로드하였음.'
        else : 
            feedback_data['feedbacks'] = serializers.serialize('json', [])
            header['message'] = '피드백 정보가 없습니다.'
        json_data_list.append(feedback_data)
        
    except Exception as e:
        print('[SYSTEM][core_task][get_feedback]', e)
        header['message'] = '피드백 정보를 불러오는 중 알 수 없는 오류 발생!'

    return json_data_list

def delete_feedback(json_data):
    json_data_list = []

    header = {}
    header['success'] = 'False'

    json_data_list.append(header)

    try:
        feedbacks = None
        if not 'feedbacks' in json_data:
            header['message'] = '삭제할 피드백 목록이 비어있습니다.'
            return  json_data_list

        # 클라이언트에게서 삭제할 피드백 목록을 받음.
        feedbacks = json_data['feedbacks']
        
        feedback_list = []
        for f in feedbacks:
            feedback = fetch_feedback(id=f['pk'])[0]
            feedback_list.append(feedback)

        if len(feedback_list) > 0:
            
            # 피드백 삭제
            for f in feedback_list:
                f.delete()
            header['success'] = 'True'
            header['message'] = '피드백 정보 삭제하였음.'
        else : 
            header['message'] = '삭제할 피드백 정보를 찾지 못했습니다.'
        
    except Exception as e:
        print('[SYSTEM][core_task][delete_feedback]', e)
        header['message'] = '피드백을 삭제하는 중 알 수 없는 오류 발생!'

    return json_data_list

def get_banned_user(json_data):
    json_data_list = []

    header = {}
    header['success'] = 'False'

    json_data_list.append(header)

    try:
        id = None
        ip = None
        
        if 'id' in json_data:
            id = json_data['id']
        
        if 'ip' in json_data:
            ip = json_data['ip']
        
        banned_users = fetch_banned_user(id=id, ip=ip)
        
        header['success'] = 'True'
        banned_users_data = {}
        if len(banned_users) > 0:
            banned_users_data['banned_users'] = serializers.serialize('json', banned_users)
            header['message'] = '밴 정보 로드하였음.'
        else : 
            banned_users_data['banned_users'] = serializers.serialize('json', [])
            header['message'] = '밴 정보가 없습니다.'
        json_data_list.append(banned_users_data)
        
    except Exception as e:
        print('[SYSTEM][core_task][get_banned_ip]', e)
        header['message'] = '밴 정보를 불러오는 중 알 수 없는 오류 발생!'

    return json_data_list

def ban_user(json_data):
    json_data_list = []

    header = {}
    header['success'] = 'False'

    json_data_list.append(header)

    try:
        # Banned_user 생성
        banned_user = models.BannedUser()
        banned_user.ip = json_data['ip']
        banned_user.reason = json_data['reason']

        banned_user.save()
        header['success'] = 'True'
        header['message'] = '해당 사용자를 Ban DB에 저장하는데 성공했습니다!'
        
    except Exception as e:
        print('[SYSTEM][core_task][ban_user]', e)
        header['message'] = '사용자를 Ban 하는 도중 알 수 없는 오류 발생!'

    return json_data_list

def unban_user(json_data):
    json_data_list = []

    header = {}
    header['success'] = 'False'

    json_data_list.append(header)

    try:
        banned_users = json_data['banned_users']

        unban_list = []
        for bu in banned_users:
            banned_user = fetch_banned_user(id=bu['pk'])[0]
            unban_list.append(banned_user)
        
        for bu in unban_list:
            bu.delete()

        header['success'] = 'True'
        header['message'] = '해당되는 사용자들을 Unban하였습니다!'
        
    except Exception as e:
        print('[SYSTEM][core_task][unban_user]', e)
        header['message'] = '사용자들을 Unban 하는 도중 알 수 없는 오류 발생!'

    return json_data_list

def is_banend_ip(request):
    '''
    밴 당했으면 True, 아니면 False 반환
    '''
    ip = request_util.get_client_ip(request)
    
    if ip:
        print('[REQUEST] Request from ' + str(ip))

        banned_users = fetch_banned_user(ip=ip)
        if len(banned_users) <= 0:
            return False, None
        else:
            print('[SYSTEM][core_task][check_banned_ip] ' + ip + ' is banned ip.')
            reason = banned_users[0].reason
    else:
        print('[SYSTEM][core_task][check_banned_ip] Failed to get client IP.')
        reason = '조회할 수 없는 IP'
    
    return True, reason