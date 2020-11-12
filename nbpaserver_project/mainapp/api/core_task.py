import os, sys
import json

from django.db.models import Q
from django.core import serializers
from .. import models
from .crawler.util import crawl_single_post, blog_post_to_model
from .analyzer.lorem_analyzer import get_distance, distance_describe
from .analyzer.Keyword_Extractor import analyze_keywords
from .crawler import multimediacrawler


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

# 분석, 키워드 추출 등 핵심 메소드
def get_analyzed_info(json_array):
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

            # 모바일 페이지면 일반 페이지로 url 변경
            if 'm.blog.naver.com' in target_url:
                target_url = target_url.replace('m.blog.naver.com', 'blog.naver.com')
                
            # url에서 blog_id와 log_no 추출
            parsed_blog_id, parsed_log_no = parse_blog_identifiers(target_url)
            
            # DB에서 동일한 게시글이 존재하는지 조회. blog_id, log_no가 파싱되면 그걸로 탐색, 없으면 url로 탐색
            if parsed_blog_id and parsed_log_no:
                bloginfo_arr = models.BlogInfo.objects.filter(blog_id=parsed_blog_id, log_no=parsed_log_no)
            else:
                bloginfo_arr = models.BlogInfo.objects.filter(url=target_url)

            # DB에 없는 신규 게시글이라면 파싱하여 DB에 저장.
            # BlogInfo는 생성될 때 Dictionary들(태그, 하이퍼링크)가 함께 생성되므로, Dictioanry테이블에서도 로드/저장해야 함.
            if len(bloginfo_arr) <= 0:
                print('[SYSTEM][core_task] BlogInfo(' + parsed_blog_id +', ' + parsed_log_no + ') does not exists in database!')
                blog_post = crawl_single_post(target_url)

                # 크롤러의 blog_post 객체를 BlogInfo 객체와 2개의 dictionary 객체배열로 변환함.
                blog_info, hyperlink_dicts, tag_dicts = blog_post_to_model(blog_post)

                # DB에 저장
                blog_info.save()
                print('[SYSTEM][core_task] BlogInfo(' + parsed_blog_id +', ' + parsed_log_no + ') saved in database!')

                for hyperlink in hyperlink_dicts:
                    hyperlink.save()
                print('[SYSTEM][core_task] hyperlink_dicts(' + parsed_blog_id +', ' + parsed_log_no + ') saved in database!')

                for tag in tag_dicts:
                    tag.save()
                print('[SYSTEM][core_task] tag_dicts(' + parsed_blog_id +', ' + parsed_log_no + ') saved in database!')
            else:
                # DB에 BlogInfo가 존재하면 태그, 하이퍼링크, 키워드 가져옴
                blog_info = bloginfo_arr[0]
                
                dict_type_tag = models.DictionaryType.objects.filter(name='hashtag')[0]
                tag_dicts = models.Dictionary.objects.filter(blog_info=blog_info, dictionary_type=dict_type_tag)

                dict_type_hyperlink = models.DictionaryType.objects.filter(name='hyperlink')[0]
                hyperlink_dicts = models.Dictionary.objects.filter(blog_info=blog_info, dictionary_type=dict_type_hyperlink)
            
            ###
            # 여기부턴 처리가 오래걸려서, 느리면 스레드 나누던지 해야할듯? 키워드 추출 알고리즘 & 로렘분석 & 멀티미디어 분석이 필요함.
            # 너무 코드가 길다. 함수로 나누자. 끔찍한 코드가 만들어지고 있음.
            ###

            # 키워드가 DB에 존재하는지 체크함.
            dict_type_keyword = models.DictionaryType.objects.filter(name='keyword')[0]
            keyword_dicts = models.Dictionary.objects.filter(blog_info=blog_info, dictionary_type=dict_type_keyword)

            # 키워드가 없으면 분석 시도
            if len(keyword_dicts) <= 0:
                keyword_dicts = []
                print('[SYSTEM][core_task] keyword_dicts(' + parsed_blog_id +', ' + parsed_log_no + ') does not exists in database!')
                keywords = analyze_keywords(blog_info.body, top_k=20)
                for k in keywords:
                    keyword = models.Dictionary()
                    keyword.blog_info = blog_info
                    keyword.dictionary_type = models.DictionaryType.objects.filter(name='keyword')[0]
                    keyword.word = k[0]         # 단어/형태 모양으로 들어감
                    keyword_dicts.append(keyword)

                # 따로 for문 도는 이유는 키워드 목록이 만들어지는 도중에 터지면, 아예 DB에 저장하지 않게 하기 위함.
                for k in keyword_dicts:
                    k.save()

                print('[SYSTEM][core_task] keyword_dicts(' + parsed_blog_id +', ' + parsed_log_no + ') saved in database!')

            # DB에서 분석 정보가 있는지 검사한다.
            analyzedinfo_arr = models.AnalyzedInfo.objects.filter(blog_info=blog_info)
            
            # 분석 정보가 없으면 로렘, 태그유사성 분석한다.
            if len(analyzedinfo_arr) <= 0:
                print('[SYSTEM][core_task] AnalyzedInfo(' + parsed_blog_id +', ' + parsed_log_no + ') does not exists in database!')
                
                # 본문은 여러줄이지만, 일단 돌아갈 수 있게 첫줄만 분석. 여러줄 분석이 미구현이므로.
                first_line = str(blog_info.body).split('\n')[0]
                try:
                    result_tok_list, result_prob_list = get_distance(first_line)
                except Exception as e:
                    print('[SYSTEM][core_task] AnalyzedInfo(' + parsed_blog_id +', ' + parsed_log_no + ') failed to analysis!')
                    json_data_list[0]['message'] = '분석 도중 오류가 발생했습니다!'
                    return json_data_list
                
                # 현재 정확한 확률을 못구하니까, 그냥 대충 확률 배열이 평균을 확률이라 한다.
                mean, variance, standard_deviation = distance_describe(result_prob_list)
                lorem_percentage = mean

                # 태그유사성은 미구현이므로 패스... 구현이 된다면 코드를 바꾸면 됨.
                tag_similarity = 0;

                # AnalyzedInfo 객체 생성하여 DB에 저장
                analyzed_info = models.AnalyzedInfo()
                analyzed_info.blog_info = blog_info
                analyzed_info.lorem_percentage = lorem_percentage
                analyzed_info.tag_similarity = tag_similarity
                    
                # DB에 저장!
                analyzed_info.save()
                print('[SYSTEM][core_task] AnalyzedInfo(' + parsed_blog_id +', ' + parsed_log_no + ') saved in database!')
            else:
                # DB에 분석 정보가 존재한다면 가져옴
                analyzed_info = analyzedinfo_arr[0]
                
            # DB에서 멀티미디어 정보가 있는지 검사한다.
            multimedia_ratios = models.MultimediaRatio.objects.filter(blog_info=blog_info)

            # 멀티미디어 정보가 없으면 멀티미디어 정보 분석한다.
            if len(multimedia_ratios) <= 0:
                print('[SYSTEM][core_task] MultimediaInfo(' + parsed_blog_id +', ' + parsed_log_no + ') does not exists in database!')
                
                # 셀레니움 크롤링 후 멀티미디어 비율을 저장한다.
                crawled_multimedia_ratios = multimediacrawler.get_multimedia(target_url)
                ratio_type_name_arr = ['image', 'imoticon', 'video', 'hyperlink', 'text', 'blank', 'etc', 'unknown']

                # float 값만 있는 ratios 배열을 모델 배열로 바꾸면서, DB에는 저장한다.
                multimedia_ratios = []
                for i in range(len(crawled_multimedia_ratios)):
                    if crawled_multimedia_ratios[i]:
                        multimedia_ratio = models.MultimediaRatio()
                        multimedia_ratio.blog_info = blog_info
                        multimedia_ratio.ratio = crawled_multimedia_ratios[i]
                        
                        ratio_type = models.RatioType.objects.filter(name=ratio_type_name_arr[i])[0]
                        multimedia_ratio.ratio_type = ratio_type
                        multimedia_ratio.save()
                        multimedia_ratios.append(multimedia_ratio)

                print('[SYSTEM][core_task] MultimediaInfo(' + parsed_blog_id +', ' + parsed_log_no + ') saved in database!')

            # 한 URL에 대해 모든 분석 혹은 로드를 마쳤음. 메모리 안에 해당 게시글의 모든 정보가 존재함.
            # 수집한 녀석들을 Json으로 바꾼다.
            # 클라이언트에게 줘야할 녀석들은, BlogInfo, Dictionary, AnalyzedInfo, MultimediaRatio임.
            data = {}
            data['blog_info'] = serializers.serialize('json', [blog_info, ])
            data['analyzed_info'] = serializers.serialize('json', [analyzed_info, ])

            data['tags'] = serializers.serialize('json', tag_dicts)
            data['hyperlinks'] = serializers.serialize('json', hyperlink_dicts)
            data['keywords'] = serializers.serialize('json', keyword_dicts)
            data['multimedia_ratios'] = serializers.serialize('json', multimedia_ratios)

            json_data_list.append(data)
        except Exception as e:
            print('[SYSTEM][core_task] AnalyzedInfo(' + target_url + ') failed to get_analyzed_info\n', e)

    if len(json_data_list) > 1:
        json_data_list[0]['success'] = 'True'
        json_data_list[0]['message'] = '게시물 분석 정보 로드하였음.'

    return json_data_list

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