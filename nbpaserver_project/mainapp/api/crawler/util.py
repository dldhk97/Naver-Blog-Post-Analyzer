import os, csv
import requests

from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urlparse, parse_qs

# 'UTF-8'이 아닌, 'MS949'로 할 경우 엑셀에서 바로 열 수 있지만, 특정 문자(\u2027)가 포함된 경우 오류가 납니다.
CSV_ENCODING_TYPE = 'utf-8'

# URL 정규화(일반, 모바일 URL을 PostView URL로)
def url_normalization(url):
    # 모바일 url 일반 url로 변경
    if 'm.blog.naver.com' in url:
        normalizated_url = url.replace('m.blog.naver.com', 'blog.naver.com')
    else:
        normalizated_url = url
    
    parsed_url = urlparse(normalizated_url)
    if 'PostView.nhn' in parsed_url.path:
        return normalizated_url
    else :
        get_blog_post_content_code = requests.get(normalizated_url)
        get_blog_post_content_text = get_blog_post_content_code.text

        get_blog_post_content_soup = BeautifulSoup(get_blog_post_content_text, 'lxml')

        for link in get_blog_post_content_soup.select('iframe#mainFrame'):
            normalizated_url = "http://blog.naver.com" + link.get('src')
            return normalizated_url


# PostView URL에서 blog_id, log_no 추출
def get_post_identifier_from_url(post_view_url):
    try:
        parsed_url = urlparse(post_view_url)
        qs = parse_qs(parsed_url.query)
        blog_id = qs['blogId'][0]
        log_no = qs['logNo'][0]
        return blog_id, log_no

    except Exception as e:
        print('[SYSTEM][crawler][util] Failed to get_blog_identifier_from_url\n', e)
        return None, None

# 검색어, 결과 개수(옵션)를 주면 파싱해서 csv로 저장하는 메소드
def crawl_by_search_word(search_word, max_count=None):
    # blog_post_list = naverblogcrawler.naver_blog_crawling(search_word, 100, "sim", max_count)
    pass

    # if blog_post_list:
    #     print("텍스트 파일로 저장합니다")
    #     save_as_csv(search_word, blog_post_list)
    
# 경로를 주면 폴더를 생성하는 메소드
def create_directory(path):
    try:
        if not(os.path.isdir(path)):
            os.makedirs(os.path.join(path))
    except OSError as e:
        if e.errno != errno.EEXIST:
            print("Failed to create directory!!!!!")
            raise

# 파일명과 BlogPost 배열을 주면 csv파일로 저장하는 메소드
def save_as_csv(file_name_header, blog_post_list):
    now = datetime.today().strftime("%Y%m%d%H%M%S")
    save_path = os.getcwd() + os.sep + 'crawl' + os.sep
    create_directory(save_path)
    file_name = now + '-' + file_name_header + '.csv'

    try:
        f = open(save_path + file_name, 'w', newline='', encoding=CSV_ENCODING_TYPE)
        wr = csv.writer(f)
        wr.writerow(['blog_id', 'log_no', 'url', 'title', 'body', 'hyperlinks', 'tags'])
        for blog_post in blog_post_list:
            try:
                if blog_post:
                    renew_body = blog_post._body
                    print(renew_body)

                    hyperlink_list = ''
                    if blog_post._hyperlinks:
                        for link in blog_post._hyperlinks:
                            hyperlink_list += link + '\n'

                    tag_list = ''
                    if blog_post._tags:
                        for tag in blog_post._tags:
                            tag_list += tag + '\n'

                    wr.writerow([blog_post._blog_id, blog_post._log_no, blog_post._url, blog_post._title, renew_body, hyperlink_list, tag_list])
                    
                    print(blog_post._url + ' 저장 완료')
            except Exception as ex:
                print(ex)
        print('모든 게시물 저장 성공!')
        f.close
    except Exception as e:
        print("Failed to save text file : ")
        print(e)

    return
