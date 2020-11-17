import os, sys, re, string
import json, math, datetime
import requests
import urllib.request
import urllib.error
import urllib.parse

from . import blogpost, util
from bs4 import BeautifulSoup

NAVER_API_INFO = None

def init(naver_api_info):
    print('[SYSTEM][naverblogcrawler]Init constnats')
    global NAVER_API_INFO
    NAVER_API_INFO = naver_api_info

def is_constants_available():
    if not NAVER_API_INFO:
        print('[SYSTEM][naverblogcrawler]No NAVER_API_INFO')
        return False

    return True


def naver_blog_crawling(search_blog_keyword, display_count, sort_type, max_count=None):
    search_result_blog_page_count = get_blog_search_result_pagination_count(search_blog_keyword, display_count)
    return get_blog_post(search_blog_keyword, display_count, search_result_blog_page_count, sort_type, max_count)


def get_blog_search_result_pagination_count(search_blog_keyword, display_count):
    encode_search_keyword = urllib.parse.quote(search_blog_keyword)
    url = "https://openapi.naver.com/v1/search/blog?query=" + encode_search_keyword
    request = urllib.request.Request(url)

    if is_constants_available() == False:
        return

    request.add_header("X-Naver-Client-Id", NAVER_API_INFO.NAVER_CLIENT_ID)
    request.add_header("X-Naver-Client-Secret", NAVER_API_INFO.NAVER_CLIENT_SECRET)

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
    tag_list = []
    try:
        url = 'https://blog.naver.com/BlogTagListInfo.nhn?blogId=' + blog_id + '&logNoList=' + log_no
        received_json = requests.get(url).json()                    # Requests로 Json 요청 후 파싱
        if len(received_json) > 0 and len(received_json['taglist']) > 0:
            raw_tag_name = received_json['taglist'][0]['tagName']
            tag_name = urllib.parse.unquote(raw_tag_name)           # URL을 한글로 디코딩

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
    # 자동으로 get_text로 파싱하는 경우 개행문자가 잘 처리되지 않음.
    # 그래서 try로 수동 html 파싱으로 개행문자를 잘 잡아보려고 했음.
    # 이 경우 html 구조가 바뀌면 터질 위험이 높기에, 터지는 경우 get_text()로 그냥 통짜로 텍스트 긁어서 처리함.

    try:
        result = ""
        for elem in content:
            if 'Tag' in str(type(elem)):
                result += elem.get_text() + '\n'
            elif 'String' in str(type(elem)):
                result += str(elem) + '\n'
    except Exception as e:
        result = str(content.get_text())
        print('[naverblogcralwer] Failed to manual html parse while parse_entire_body\n', e)
    
    # 이스케이프 문자 다 띄어쓰기로 변경
    result = re.sub(r'(\u180B|\u200B|\u200C|\u200D|\u2060|\uFEFF|\xa0)+', '\n', result)

    # 줄바꿈 문자 처리
    result = re.sub(r'\n+', '\n', result)
    result = re.sub(r'(\n*\s+\n+|\n+\s+\n*)', '\n', result)
    result = re.sub(r'(\n\s|\s\n)', '\n', result)

    # 공백 여러개를 하나로
    result = re.sub(r'( |\t|\xa0)+', ' ', result)

    # 이모지 처리
    result = util.remove_emoji(result)
    result = result.strip()
    
    return result
        
            
# 하이퍼링크 목록을 반환
def parse_hyperlinks(content):
    try:
        result = []
        for node in content.find_all('a', href=True):
            if node['href'] != '#':
                hyperlink = node['href']
                
                # 중복 체크하고 리스트에 추가
                if hyperlink not in result:
                    result.append(hyperlink)
                        
        return result
    except Exception as e:
        print('[parse_hyperlinks] ERROR : ' , e)

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

        # 모바일이든, 일반url이든 postView url로 변경
        post_view_url = util.url_normalization(blog_post_url)

        # url로부터 블로그의 id와 게시물의 id(log_no)를 추출함.
        blog_id, log_no = util.get_post_identifier_from_url(post_view_url)

        # bs4로 html 파싱
        get_real_blog_post_content_soup = parse_entire_blog_post(post_view_url)
        
        # 본문과 태그의 부모 div의 id를 특정함
        body_identifier = parse_body_identifier(log_no)

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
            hyperlinks = parse_hyperlinks(main_content)       # 하이퍼링크 목록 추출
            tags = parse_tags(blog_id, log_no)                # 태그 추출(태그는 레이지로딩인거같아 파싱 불가. Json으로 따로 추출)

            return  blogpost.BlogPost(blog_id, log_no, blog_post_url, title, description, date, blog_name, hyperlinks, tags, body)
    else:
        print(blog_post_url + ' 는 네이버 블로그가 아니라 패스합니다')

# 네이버 API를 사용해서 파싱하는 메소드
def get_blog_post(search_blog_keyword, display_count, search_result_blog_page_count, sort_type, max_count=None):
    encode_search_blog_keyword = urllib.parse.quote(search_blog_keyword)

    if is_constants_available == False:
        return

    for i in range(1, search_result_blog_page_count + 1):
        url = "https://openapi.naver.com/v1/search/blog?query=" + encode_search_blog_keyword + "&display=" + str(
            display_count) + "&start=" + str(i) + "&sort=" + sort_type

        request = urllib.request.Request(url)
        
        request.add_header("X-Naver-Client-Id", NAVER_API_INFO.NAVER_CLIENT_ID)
        request.add_header("X-Naver-Client-Secret", NAVER_API_INFO.NAVER_CLIENT_SECRET)

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

    