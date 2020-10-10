import re
import json
import math
import datetime
import requests
import urllib.request
import urllib.error
import urllib.parse
import string
from bs4 import BeautifulSoup
from constants import NaverAPI
from blogpost import BlogPost
from pykospacing import spacing


def naver_blog_crawling(search_blog_keyword, display_count, sort_type, max_count=None):
    search_result_blog_page_count = get_blog_search_result_pagination_count(search_blog_keyword, display_count)
    return get_blog_post(search_blog_keyword, display_count, search_result_blog_page_count, sort_type, max_count)


def get_blog_search_result_pagination_count(search_blog_keyword, display_count):
    encode_search_keyword = urllib.parse.quote(search_blog_keyword)
    url = "https://openapi.naver.com/v1/search/blog?query=" + encode_search_keyword
    request = urllib.request.Request(url)

    request.add_header("X-Naver-Client-Id", NaverAPI.NAVER_CLIENT_ID)
    request.add_header("X-Naver-Client-Secret", NaverAPI.NAVER_CLIENT_SECRET)

    response = urllib.request.urlopen(request)
    response_code = response.getcode()

    if response_code is 200:
        response_body = response.read()
        response_body_dict = json.loads(response_body.decode('utf-8'))

        if response_body_dict['total'] == 0:
            blog_pagination_count = 0
        else:
            blog_pagination_total_count = math.ceil(response_body_dict['total'] / int(display_count))

            if blog_pagination_total_count >= 1000:
                blog_pagination_count = 1000
            else:
                blog_pagination_count = blog_pagination_total_count

            print("키워드 " + search_blog_keyword + "에 해당하는 포스팅 수 : " + str(response_body_dict['total']))
            print("키워드 " + search_blog_keyword + "에 해당하는 블로그 실제 페이징 수 : " + str(blog_pagination_total_count))
            print("키워드 " + search_blog_keyword + "에 해당하는 블로그 처리할 수 있는 페이징 수 : " + str(blog_pagination_count))

        return blog_pagination_count

# --------------------------------------------------

# 페이지 제목 추출
def parse_title_content(content):
    title = content.find_all('title', limit=1)
    if title:
        return title[0].string.replace(' : 네이버 블로그','')
    else:
        return content

# 게시글 타입별 본문 지정. 본문만 선택할 수 있으면 본문 노드 반환.
def parse_main_content(content):
    main = content.select('div.se-main-container')
    if main:
        return main[0]
    else:
        main = content.select('div.__se_component_area')
        if main:
            return main[0]
        else:
            return content

# 페이지 태그 추출
def parse_tags(blog_id, log_no):
    try:
        url = 'https://blog.naver.com/BlogTagListInfo.nhn?blogId=' + blog_id + '&logNoList=' + log_no
        received_json = requests.get(url).json()                    # Requests로 Json 요청 후 파싱
        if len(received_json) > 0 and len(received_json['taglist']) > 0:
            raw_tag_name = received_json['taglist'][0]['tagName']
            tag_name = urllib.parse.unquote(raw_tag_name)           # URL을 한글로 디코딩

            tag_list = []
            for tag in tag_name.split(','):
                tag_list.append(tag)
            return tag_list
    except Exception as e:
        print('[parse_tags][' + str(blog_id) + '/' + str(log_no) +'] ERROR : ' , e)

# 블로그 URL에서 logNo 추출
def parse_log_no(url):
    try:
        for s in url.split('&'):
            if s.startswith('logNo'):
                return s.split('=')[1]
    except Exception as e:
        print(e)
    return None

# 블로그 URL에서 blogId 추출
def parse_blog_id(url):
    for s in url.split('?'):
        if s.startswith('blogId'):
            return s.split('&')[0].split('=')[1]
    return 'Unknown'

# 본문 텍스트 추출
def parse_entire_body(content):
    result = str(content.get_text())

    # 공백 및 개행문자 정리
    result = re.sub(r'(\s|\u180B|\u200B|\u200C|\u200D|\u2060|\uFEFF)+', '', result)

    # 띄어쓰기 처리
    result = spacing(result)

    return result.strip()


# 하이퍼링크 목록을 반환
def parse_hyperlinks(content):
    try:
        result = []
        for node in content.find_all('a', href=True):
            if node['href'] != '#':
                hyperlink = node['href']
                result.append(hyperlink)
        return result
    except Exception as e:
        print('[parse_hyperlinks] ERROR : ' , e)


# 일반 url을 주면 blogId, logNo가 포함된 자세한 URL을 반환
def parse_real_blog_post_url(blog_post_url):
    get_blog_post_content_code = requests.get(blog_post_url)
    get_blog_post_content_text = get_blog_post_content_code.text

    get_blog_post_content_soup = BeautifulSoup(get_blog_post_content_text, 'lxml')

    for link in get_blog_post_content_soup.select('iframe#mainFrame'):
        real_blog_post_url = "http://blog.naver.com" + link.get('src')
        return real_blog_post_url

    # 이미 리얼 블로그 url인 경우 그대로 반환
    return blog_post_url

# 리얼 URL을 주면 전체 html 반환
def parse_entire_blog_post(real_blog_post_url):
    get_real_blog_post_content_code = requests.get(real_blog_post_url)
    get_real_blog_post_content_text = get_real_blog_post_content_code.text

    get_real_blog_post_content_soup = BeautifulSoup(get_real_blog_post_content_text, 'lxml')
    return get_real_blog_post_content_soup

# log_no를 주면 본문 식별자 반환
def parse_body_identifier(log_no):
    if log_no:
        body_identifier = 'div#post-view' + log_no
    else:
        body_identifier = 'div#postViewArea'
    return body_identifier

# 한 블로그에 대하여 파싱하는 메소드
def pasre_blog_post(blog_post_url, api_response_item=None):
    # 네이버 블로그인 경우만 처리함.
    if 'blog.naver.com' in blog_post_url:

        real_blog_post_url = parse_real_blog_post_url(blog_post_url)

        get_real_blog_post_content_soup = parse_entire_blog_post(real_blog_post_url)

        # 본문과 태그의 부모 div의 id를 특정함
        log_no = parse_log_no(real_blog_post_url)
        body_identifier = parse_body_identifier(log_no)
        
        # blogId 구하기(blogId + log_no로 URL이 없어도 만들어낼 수 있어서 추출하여 저장함)
        blog_id = parse_blog_id(real_blog_post_url)

        for blog_post_content in get_real_blog_post_content_soup.select(body_identifier):
            main_content = parse_main_content(blog_post_content)
            remove_html_tag = re.compile('<.*?>')

            # API를 안거치고 파싱하는경우 제목, 설명, 날짜, 블로그명을 직접 파싱해야함
            if api_response_item is not None:
                description = re.sub(remove_html_tag, '',
                                            api_response_item['description'])
                date = datetime.datetime.strptime(api_response_item['postdate'],
                                                                "%Y%m%d").strftime("%y.%m.%d")
                blog_name = api_response_item['bloggername']
            else:
                # 부가 정보들인데 아직 필요없어서 파싱 코드 없음
                description = 'UNKNOWN'
                date = 'UNKNOWN'
                blog_name = 'UNKNOWN'

            title = parse_title_content(get_real_blog_post_content_soup)
            body = parse_entire_body(main_content)            # 본문 텍스트 추출
            # images = parse_images(main_content)               # 이미지 목록 추출
            hyperlinks = parse_hyperlinks(main_content)       # 하이퍼링크 목록 추출
            # videos = parse_videos(main_content)               # 비디오 목록 추출(유튜브 or 네이버TV)
            tags = parse_tags(blog_id, log_no)                # 태그 추출(태그는 레이지로딩인거같아 파싱 불가. Json으로 따로 추출)

            current_blog_post = BlogPost(blog_id, log_no, blog_post_url, title, description, date, blog_name, hyperlinks, tags, body)
            return current_blog_post
    else:
        print(blog_post_url + ' 는 네이버 블로그가 아니라 패스합니다')

# 네이버 API를 사용해서 파싱하는 메소드
def get_blog_post(search_blog_keyword, display_count, search_result_blog_page_count, sort_type, max_count=None):
    encode_search_blog_keyword = urllib.parse.quote(search_blog_keyword)

    for i in range(1, search_result_blog_page_count + 1):
        url = "https://openapi.naver.com/v1/search/blog?query=" + encode_search_blog_keyword + "&display=" + str(
            display_count) + "&start=" + str(i) + "&sort=" + sort_type

        request = urllib.request.Request(url)

        request.add_header("X-Naver-Client-Id", NaverAPI.NAVER_CLIENT_ID)
        request.add_header("X-Naver-Client-Secret", NaverAPI.NAVER_CLIENT_SECRET)

        response = urllib.request.urlopen(request)
        response_code = response.getcode()

        if response_code is 200:
            response_body = response.read()
            response_body_dict = json.loads(response_body.decode('utf-8'))

            blog_post_list = []

            # 최대 개수가 정해지지 않았다면 모든 검색결과를 크롤링한다
            if max_count is None:
                max_count = len(response_body_dict['items'])

            for j in range(1, max_count + 1):
                try:
                    api_response_item = response_body_dict['items'][j]
                    blog_post_url = api_response_item['link'].replace("amp;", "")

                    current_blog_post = pasre_blog_post(blog_post_url, api_response_item)
                    
                    if current_blog_post:
                        blog_post_list.append(current_blog_post)
                        print(blog_post_url + ' 파싱완료 (' + str(j) + '/' + str(max_count) + ')')
                except Exception as e:
                    print('파싱 도중 에러발생 : ')
                    print(e)
                    j += 1
            
            # 파싱 완료 시 게시물 목록이 있으면 반환
            print("파싱 완료!")
            if blog_post_list:
                return blog_post_list

    