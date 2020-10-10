import os
import naverblogcrawler
import csv
from datetime import datetime
from multimediacrawler import get_multimedia

# 'UTF-8'이 아닌, 'MS949'로 할 경우 엑셀에서 바로 열 수 있지만, 특정 문자(\u2027)가 포함된 경우 오류가 납니다.
CSV_ENCODING_TYPE = 'utf-8'

# 검색어, 결과 개수(옵션)를ㅈ ㅜ면 파싱해서 csv로 저장하는 메소드
def crawl_by_search_word(search_word, max_count=None):
    blog_post_list = naverblogcrawler.naver_blog_crawling(search_word, 100, "sim", max_count)

    if blog_post_list:
        print("텍스트 파일로 저장합니다")
        save_as_csv(search_word, blog_post_list)

# 네이버 블로그 URL을 주면 해당 게시물을 파싱해서 csv로 저장하는 메소드
def crawl_single_post(url):
    blog_post_list = []

    blog_post = naverblogcrawler.pasre_blog_post(url)

    if blog_post:
        blog_post_list.append(blog_post)
    
    if blog_post_list:
        file_name_header = blog_post._blog_id + ' ' + blog_post._log_no

        print("텍스트 파일로 저장합니다")
        save_as_csv(file_name_header, blog_post_list)

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
        f = open(save_path + file_name, 'w', encoding=CSV_ENCODING_TYPE)
        wr = csv.writer(f)
        wr.writerow(['blog_id', 'log_no', 'url', 'title', 'body', 'hyperlinks', 'tags'])
        for blog_post in blog_post_list:
            try:
                if blog_post:
                    renew_body = blog_post._body.replace('\n',' ')   # 바디에 개행문자가 있으면 csv파일이 제대로 생성 안됨...

                    hyperlink_list = ''
                    if blog_post._hyperlinks:
                        for link in blog_post._hyperlinks:
                            hyperlink_list += link + ', '

                    tag_list = ''
                    if blog_post._tags:
                        for tag in blog_post._tags:
                            tag_list += tag + ', '

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

# Simple CLI에서 검색어로 크롤링 할 수 있게 해주는 메소드
def task_crawl_by_search_word():
    print('검색어 : ')
    search_word = input()
    if search_word is not None:
        print('크롤링할 포스트의 개수 : ')
        blog_post_count = input()
        try:
            if blog_post_count.isdigit:
                crawl_by_search_word(search_word, int(blog_post_count))
            else:
                print('크롤링할 포스트의 개수가 올바르지 않습니다.')
        except Exception as e:
            print(e)
    else:
        print('검색어가 올바르지 않습니다.')

# Simple CLI에서 블로그 URL로 크롤링 할 수 있게 해주는 메소드
def task_crawl_single_post():
    print('URL : ')
    url = input()
    if url is not None:
        crawl_single_post(url)
    else:
        print('URL이 올바르지 않습니다.')

def task_crawl_multimedia():
    print('URL : ')
    url = input()
    if url is not None:
        get_multimedia(url)
    else:
        print('URL이 올바르지 않습니다.')

# 간단한 CLI
def simple_cli():
    while True:
        try:
            print('1. 검색어로 크롤링')
            print('2. URL로 하나의 게시글 크롤링')
            print('3. URL로 하나의 게시글 멀티미디어 크롤링')
            print('4. 종료')
            user_input = input()

            if user_input is '1':
                task_crawl_by_search_word()
            elif user_input is '2':
                task_crawl_single_post()
            elif user_input is '3':
                task_crawl_multimedia()
            elif user_input is '4':
                break

        except Exception as e:
            print(e)

    print('종료합니다')

if __name__ == '__main__':
    simple_cli()