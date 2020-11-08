import os, sys
import json

from django.db.models import Q
from .. import models
from .crawler.naver_blog_post_crawler import crawl_single_post

# 파라미터가 없는 url에서 blog_id, log_no 추출하기
def parse_blog_identifiers(url):
    try:
        splited = url.split('/')
        blog_id = splited[3]
        log_no = splited[4]
        return blog_id, log_no

    except Exception as e:
        print(e)
    
    return None, None

# 크롤러에서 사용하는 BlogPost 객체를 BlogInfo, Dictionary배열로 분리하여 DB에 저장
def save_blog_post(blog_post):
    try:
        # BlogInfo 객체 생성하여 DB에 저장
        blog_info = models.BlogInfo()
        blog_info.blog_id = blog_post._blog_id
        blog_info.log_no = blog_post._log_no
        blog_info.url = blog_post._url
        blog_info.title = blog_post._title
        blog_info.body = blog_post._body
        blog_info.save()

        # 하이퍼링크 객체 생성하여 DB에 저장
        for l in blog_post._hyperlinks:
            hyperlink = models.Dictionary()
            hyperlink.blog_info = blog_info
            hyperlink.dictionary_type = models.DictionaryType.objects.filter(name='hyperlink')[0]
            hyperlink.word = l
            hyperlink.save()

        # 태그 객체 생성하여 DB에 저장
        for t in blog_post._tags:
            tag = models.Dictionary()
            tag.blog_info = blog_info
            tag.dictionary_type = models.DictionaryType.objects.filter(name='hashtag')[0]
            tag.word = t
            tag.save()

    except Exception as e:
        print('[SYSTEM][core_task]save_blog_post failed to save.\n' + blog_info.title + ', ' + blog_info.url, e)


# 분석, 키워드 추출 등 핵심 메소드
def get_analyzed_info(json_array):

    # 받아온 url 목록을 순차 탐색
    for json_obj in json_array:
        target_url = json_obj['url']

        # url에서 blog_id와 log_no 추출
        parsed_blog_id, parsed_log_no = parse_blog_identifiers(target_url)
        
        # DB에서 동일한 게시글이 존재하는지 조회. blog_id, log_no가 파싱되면 그걸로 탐색, 없으면 url로 탐색
        if parsed_blog_id and parsed_log_no:
            bloginfo_arr = models.BlogInfo.objects.filter(blog_id=parsed_blog_id, log_no=parsed_log_no)
        else:
            bloginfo_arr = models.BlogInfo.objects.filter(url=target_url)

        # DB에 없는 신규 게시글이라면 파싱하여 DB에 저장
        if len(bloginfo_arr) <= 0:
            print('[SYSTEM][core_task]BlogInfo not exists!')
            blog_post = crawl_single_post(target_url)       # beautifulsoup로 크롤링하면 제목, 본문 외에도 태그, 하이퍼링크 등이 파싱됨.
            
            save_blog_post(blog_post)
            print('[SYSTEM][core_task]' + blog_post._title + ' saved!')
        
        # 분석

    return {'item':'hoho', 'value':'42'}

def json_to_bloginfo(json_array):
    
    # JSON 배열을 BlogInfo 배열로 바꾸기
    bloginfo_arr = []
    for json_obj in json_array:
        info = models.BlogInfo()
        info.blog_id = json_obj['blog_id']
        info.log_no = json_obj['log_no']
        info.url = json_obj['url']
        info.title = json_obj['title']
        info.body = json_obj['body']

        print(str(info))
    
        bloginfo_arr.append(info)

    pass