import os, sys, json, time
import concurrent.futures
from django.db.models import Q
from django.core import serializers

from . import core_job
from .. import models
from .crawler.util import url_normalization, get_post_identifier_from_url
from .crawler import naverblogcrawler
from .util import model_converter
from functools import partial

def fetch_ratio_type(ratio_type_name):
    ratio_type = models.RatioType.objects.filter(name=ratio_type_name)[0]
    return ratio_type

def fetch_dictionary_type(dictionary_type_name):
    dictionray_type = models.DictionaryType.objects.filter(name=dictionary_type_name)[0]
    return dictionray_type

def fetch_dictionary(blog_info, dictionary_type_name):
    '''
    해당 블로그의 딕셔너리(django.model) list 반환
    '''
    dict_type = fetch_dictionary_type(dictionary_type_name)
    dicts = models.Dictionary.objects.filter(blog_info=blog_info, dictionary_type=dict_type)

    return list(dicts)

def fetch_blog_info(target_url):
    '''
    DB에 BlogInfo가 있으면 반환, 없으면 크롤러로 파싱하여
    DB에 BlogInfo를 저장하고 하이퍼링크, 태그를 Dictionary 테이블에 저장 후 반환
    '''
    blog_id, log_no = get_post_identifier_from_url(target_url)

    # DB에서 동일한 게시글이 존재하는지 조회. blog_id, log_no가 파싱되면 그걸로 탐색, 없으면 url로 탐색
    if blog_id and log_no:
        bloginfo_arr = models.BlogInfo.objects.filter(blog_id=blog_id, log_no=log_no)
    else:
        bloginfo_arr = models.BlogInfo.objects.filter(url=target_url)

    # DB에 블로그 정보가 없음
    if len(bloginfo_arr) <= 0:
        print('[SYSTEM][core_task] BlogInfo(' + target_url + ') does not exists in database!')

        blog_post = naverblogcrawler.pasre_blog_post(target_url)
        
        blog_info, hyperlink_list, tag_list = model_converter.blog_post_to_django_model(blog_post)

        # DB에 저장
        blog_info.save()
        print('[SYSTEM][core_task] BlogInfo(' + target_url + ') saved in database!')

        for hyperlink in hyperlink_list:
            hyperlink.save()
        print('[SYSTEM][core_task] hyperlink_list(' + target_url + ') saved in database!')

        for tag in tag_list:
            tag.save()
        print('[SYSTEM][core_task] tag_list(' + target_url + ') saved in database!')
    else:
        # DB에 BlogInfo가 존재하면 태그, 하이퍼링크, 키워드 가져옴
        blog_info = bloginfo_arr[0]
        tag_list = fetch_dictionary(blog_info, 'hashtag')
        hyperlink_list = fetch_dictionary(blog_info, 'hyperlink')

    return blog_info, tag_list, hyperlink_list



# 분석, 키워드 추출 등 핵심 메소드
def fetch_entire_info_from_urls(json_array):
    '''
    클라이언트에게 url 목록을 받으면 해당 게시글의 모든 정보(BlogInfo, AnalyzedInfo, tag, 를 반환함.
    '''
    json_data_list = []

    header_data = {}
    header_data['success'] = 'False'
    header_data['message'] = '게시글 분석 정보를 불러오는 중 오류 발생!'

    json_data_list.append(header_data)

    # 받아온 url 목록을 순차 탐색
    for json_obj in json_array:
        try:
            target_url = json_obj['url']

            # 블로그 게시글이 아니면 패스
            if 'blog.naver.com' not in target_url:
                continue

            target_url = url_normalization(target_url)
            
            blog_info, tag_list, hyperlink_list = fetch_blog_info(target_url)

            if blog_info is None:
                print('[SYSTEM][core_task][fetch_entire_info_from_urls] Failed to fetch blog_info!')
                continue
            
            ###
            # 여기부턴 처리가 오래걸려서, 느리면 스레드 나누던지 해야할듯? 키워드 추출 알고리즘 & 로렘분석 & 멀티미디어 분석이 필요함.
            # 너무 코드가 길다. 함수로 나누자. 끔찍한 코드가 만들어지고 있음.
            # 키워드추출, 로렘분석, 멀티미디어 비율 분석을 멀테프로세스로 처리
            ###
            
            start_time = time.time()

            keyword_future = None
            analyzed_info_future = None
            multimedia_future = None

            # 테이블 조회하고 정보가 없으면 작업 목록에 추가함.
            keyword_list = fetch_dictionary(blog_info, 'keyword')
            analyzedinfo_list = list(models.AnalyzedInfo.objects.filter(blog_info=blog_info))
            multimedia_ratio_list = list(models.MultimediaRatio.objects.filter(blog_info=blog_info))

            with concurrent.futures.ThreadPoolExecutor() as executor:
                if len(keyword_list) <= 0:
                    print('[SYSTEM][core_task] Keywords(' + blog_info.blog_id +', ' + blog_info.log_no + ') does not exists in database!')
                    keyword_future = executor.submit(core_job.keyword_job, blog_info)
                if len(analyzedinfo_list) <= 0:
                    print('[SYSTEM][core_task] AnalyzedInfo(' + blog_info.blog_id +', ' + blog_info.log_no + ') does not exists in database!')
                    analyzed_info_future = executor.submit(core_job.analyze_job, blog_info)
                else:
                    analyzed_info = analyzedinfo_list[0]
                if len(multimedia_ratio_list) <= 0:
                    print('[SYSTEM][core_task] MultimediaInfo(' + blog_info.blog_id +', ' + blog_info.log_no + ') does not exists in database!')
                    multimedia_future = executor.submit(core_job.multimedia_job, blog_info)

            # 멀티프로세싱이 끝나면, 각 정보들을 DB에 넣을 수 있게 모델 변환 후 저장
            if keyword_future:
                keyword_list = []
                for word in keyword_future.result():
                    dict_type = fetch_dictionary_type('keyword')
                    converted_keyword = model_converter.dictionary_to_django_model(blog_info, word, dict_type)
                    converted_keyword.save()
                    keyword_list.append(converted_keyword)
                if len(keyword_list) > 0:
                    print('[SYSTEM][core_task] Keywords(' + blog_info.blog_id +', ' + blog_info.log_no + ') saved in database!')

            if analyzed_info_future:
                if analyzed_info_future.result() != {}:
                    analyzed_info = analyzed_info_future.result()
                    converted_analyzed_info = model_converter.analyzed_info_to_django_model(blog_info, analyzed_info['lorem_percentage'], analyzed_info['tag_similarity'])
                    converted_analyzed_info.save()
                    analyzed_info = converted_analyzed_info
                    print('[SYSTEM][core_task] AnalyzedInfo(' + blog_info.blog_id +', ' + blog_info.log_no + ') saved in database!')

            if multimedia_future:
                multimedia_ratio_list = []
                for ratio in multimedia_future.result():
                    ratio_type = fetch_ratio_type(ratio['ratio_type'])
                    converted_ratio = model_converter.multimedia_ratio_to_django_model(blog_info, ratio['ratio'], ratio_type)
                    converted_ratio.save()
                    multimedia_ratio_list.append(converted_ratio)
                if len(multimedia_ratio_list) > 0:
                    print('[SYSTEM][core_task] MultimediaInfo(' + blog_info.blog_id +', ' + blog_info.log_no + ') saved in database!')
                
            print("%s"%(time.time()-start_time))

            # 한 URL에 대해 모든 분석 혹은 로드를 마쳤음. 메모리 안에 해당 게시글의 모든 정보가 존재함.
            # 수집한 녀석들을 Json으로 바꾼다.
            # 클라이언트에게 줘야할 녀석들은, BlogInfo, Dictionary, AnalyzedInfo, MultimediaRatio임.
            data = {}
            
            data['blog_info'] = serializers.serialize('json', [blog_info, ])
            data['analyzed_info'] = serializers.serialize('json', [analyzed_info, ])

            data['tags'] = serializers.serialize('json', tag_list)
            data['hyperlinks'] = serializers.serialize('json', hyperlink_list)
            data['keywords'] = serializers.serialize('json', keyword_list)
            data['multimedia_ratios'] = serializers.serialize('json', multimedia_ratio_list)

            json_data_list.append(data)
        except Exception as e:
            print('[SYSTEM][core_task][fetch_entire_info_from_urls] AnalyzedInfo(' + target_url + ') failed to fetch_entire_info_from_urls.\n', e)
            pass

    if len(json_data_list) > 1:
        json_data_list[0]['success'] = 'True'
        json_data_list[0]['message'] = '게시물 분석 정보 로드하였음.'

    return json_data_list
    
def lookup_keywords(json_array):
    json_data_list = []

    header_data = {}
    header_data['success'] = 'False'
    header_data['message'] = '키워드 정보를 불러오는 중 오류 발생!'

    json_data_list.append(header_data)

    # 받아온 url 목록을 순차 탐색
    for json_obj in json_array:
        try:
            target_url = json_obj['url']

            # 블로그 게시글이 아니면 패스
            if 'blog.naver.com' not in target_url:
                continue

            target_url = url_normalization(target_url)
            
            blog_info, tag_list, hyperlink_list = fetch_blog_info(target_url)

            if blog_info is None:
                print('[SYSTEM][core_task][fetch_entire_info_from_urls] Failed to fetch blog_info!')
                continue
        
            keyword_future = None

            # 테이블 조회하고 정보가 없으면 작업 목록에 추가함.
            keyword_list = fetch_dictionary(blog_info, 'keyword')

            with concurrent.futures.ThreadPoolExecutor() as executor:
                if len(keyword_list) <= 0:
                    print('[SYSTEM][core_task] Keywords(' + blog_info.blog_id +', ' + blog_info.log_no + ') does not exists in database!')
                    keyword_future = executor.submit(core_job.keyword_job, blog_info)

            # 멀티프로세싱이 끝나면, 각 정보들을 DB에 넣을 수 있게 모델 변환 후 저장
            if keyword_future:
                keyword_list = []
                for word in keyword_future.result():
                    dict_type = fetch_dictionary_type('keyword')
                    converted_keyword = model_converter.dictionary_to_django_model(blog_info, word, dict_type)
                    converted_keyword.save()
                    keyword_list.append(converted_keyword)
                if len(keyword_list) > 0:
                    print('[SYSTEM][core_task] Keywords(' + blog_info.blog_id +', ' + blog_info.log_no + ') saved in database!')

            data = {}
            
            data['keywords'] = serializers.serialize('json', keyword_list)

            json_data_list.append(data)
        except Exception as e:
            print('[SYSTEM][core_task][fetch_entire_info_from_urls] AnalyzedInfo(' + target_url + ') failed to fetch_entire_info_from_urls.\n', e)
            pass

    if len(json_data_list) > 1:
        json_data_list[0]['success'] = 'True'
        json_data_list[0]['message'] = '키워드 정보 로드하였음.'

    return json_data_list

def get_keywords(json_array):
    json_data_list = []

    header_data = {}
    header_data['success'] = 'False'
    header_data['message'] = '키워드 정보를 불러오는 중 오류 발생!'

    json_data_list.append(header_data)

    # 받아온 url 목록을 순차 탐색
    for json_obj in json_array:
        try:
            target_url = json_obj['url']

            # 블로그 게시글이 아니면 패스
            if 'blog.naver.com' not in target_url:
                continue

            target_url = url_normalization(target_url)
            
            blog_info, tag_list, hyperlink_list = fetch_blog_info(target_url)

            if blog_info is None:
                print('[SYSTEM][core_task][fetch_entire_info_from_urls] Failed to fetch blog_info!')
                continue
        
            keyword_future = None

            # 테이블 조회하고 정보가 없으면 작업 목록에 추가함.
            keyword_list = fetch_dictionary(blog_info, 'keyword')

            with concurrent.futures.ThreadPoolExecutor() as executor:
                if len(keyword_list) <= 0:
                    print('[SYSTEM][core_task] Keywords(' + blog_info.blog_id +', ' + blog_info.log_no + ') does not exists in database!')
                    keyword_future = executor.submit(core_job.keyword_job, blog_info)

            # 멀티프로세싱이 끝나면, 각 정보들을 DB에 넣을 수 있게 모델 변환 후 저장
            if keyword_future:
                keyword_list = []
                for word in keyword_future.result():
                    dict_type = fetch_dictionary_type('keyword')
                    converted_keyword = model_converter.dictionary_to_django_model(blog_info, word, dict_type)
                    converted_keyword.save()
                    keyword_list.append(converted_keyword)
                if len(keyword_list) > 0:
                    print('[SYSTEM][core_task] Keywords(' + blog_info.blog_id +', ' + blog_info.log_no + ') saved in database!')

            data = {}
            
            data['keywords'] = serializers.serialize('json', keyword_list)

            json_data_list.append(data)
        except Exception as e:
            print('[SYSTEM][core_task][fetch_entire_info_from_urls] AnalyzedInfo(' + target_url + ') failed to fetch_entire_info_from_urls.\n', e)
            pass

    if len(json_data_list) > 1:
        json_data_list[0]['success'] = 'True'
        json_data_list[0]['message'] = '키워드 정보 로드하였음.'

    return json_data_list

    
def get_bloginfo(json_array):
    json_data_list = []

    header_data = {}
    header_data['success'] = 'False'
    header_data['message'] = '블로그 정보를 불러오는 중 오류 발생!'

    json_data_list.append(header_data)

    # 받아온 url 목록을 순차 탐색
    for json_obj in json_array:
        try:
            target_url = json_obj['url']

            # 블로그 게시글이 아니면 패스
            if 'blog.naver.com' not in target_url:
                continue

            target_url = url_normalization(target_url)
            
            blog_info, tag_list, hyperlink_list = fetch_blog_info(target_url)

            if blog_info is None:
                print('[SYSTEM][core_task][fetch_entire_info_from_urls] Failed to fetch blog_info!')
                continue

            data = {}
            
            data['blog_info'] = serializers.serialize('json', [blog_info, ])

            json_data_list.append(data)
        except Exception as e:
            print('[SYSTEM][core_task][fetch_entire_info_from_urls] AnalyzedInfo(' + target_url + ') failed to fetch_entire_info_from_urls.\n', e)
            pass

    if len(json_data_list) > 1:
        json_data_list[0]['success'] = 'True'
        json_data_list[0]['message'] = '블로그 정보 로드하였음.'

    return json_data_list

    
