import os, platform
import string
from selenium import webdriver
from bs4 import BeautifulSoup
from naverblogcrawler import parse_log_no, parse_blog_id, parse_main_content, parse_real_blog_post_url, parse_body_identifier
from multimedia import MultiMedia

# 설치되어있는 크롬의 버전에 맞는 드라이버를 사용하십시오.
driver = None

def prepare_selenium():
    global driver
    options = webdriver.ChromeOptions()
    # options.add_argument('headless')

    driver_name = None
    if platform.system() == 'Linux':
        print('Platform is Linux')
        driver_name = 'chromedriver85_linux'
    else:
        print('Platform is Windows')
        driver_name = 'chromedriver85_win.exe'
    
    driver_path = os.getcwd() + os.sep + 'bin' + os.sep + driver_name

    print('Using this driver : ' + driver_path)

    driver = webdriver.Chrome(executable_path=driver_path, chrome_options=options)
    
    driver.implicitly_wait(3)

# 이미지 목록과 이모티콘 목록을 반환
def parse_images(blog_post_content):
    image_list = []
    imoticon_list = []
    
    for node in blog_post_content.find_elements_by_tag_name('img'):
        try:
            # 이미지 주소 추출
            src = node.get_attribute('src')
            if src is None:
                src = node.get_attribute('data-lazy-src')

            # 블랭크 gif인 경우 패스
            if 'https://ssl.pstatic.net/static/blank.gif' in src:
                continue
            # 섬네일인 경우 패스
            elif 'http://blogpfthumb.phinf.naver.net/' in src:
                continue

            width = node.size['width']
            height = node.size['height']

            # 네이버 이모티콘인경우 이모티콘 리스트에 추가
            if 'storep-phinf.pstatic.net' in src:
                imoticon_list.append(MultiMedia('imoticon', src, width, height))
            else:
                image_list.append(MultiMedia('image', src, width, height))

        except Exception as e:
            print('[parse_images] ERROR : ' , e)
        
    return image_list, imoticon_list

# 비디오 목록 추출(유튜브 or 네이버TV)
def parse_videos(blog_post_content):
    video_list = []

    # 유튜브 잡기
    for node in blog_post_content.find_elements_by_tag_name('iframe'):
        try:
            if 'www.youtube.com' in node.get_attribute('src'):
                src = node.get_attribute('src')
                width = node.size['width']
                height = node.size['height']

                video_list.append(MultiMedia('video', src, width, height))
        except Exception as e:
            print('[parse_videos(Y)] ERROR : ' , e)

    # 네이버 잡기
    nodes = blog_post_content.find_elements_by_tag_name('canvas')
    for node in nodes:
        try:
            parent = node.find_element_by_xpath('..').get_attribute('innerHTML')
            width = node.size['width']
            height = node.size['height']

            s = str(parent)

            # 네이버 동영상 URL은 html에 안나타나는듯, cavas 중 크기가 0 이상인것을 영상 목록에 추가함.
            if width > 0 and height > 0:
                video_list.append(MultiMedia('video', s, width, height))
        except Exception as e:
            print('[parse_videos(N)] ERROR : ' , e)

    return video_list

def get_multimedia(blog_post_url):
    # 네이버 블로그인 경우만 처리함.
    if 'blog.naver.com' not in blog_post_url:
        print(blog_post_url + ' 는 네이버 블로그가 아니라 패스합니다')
        return

    try:
        if driver is None:
            # 셀레니움 드라이버 준비
            prepare_selenium()

        # 일반 url에서 bs4로 log_no, blog_id가 포함된 real_blog_post_url을 추출
        real_blog_post_url = parse_real_blog_post_url(blog_post_url)

        # 리얼 블로그 주소를 셀레니움으로 파싱
        driver.get(real_blog_post_url)
        
        # 게시물 번호 추출 후 본문 식별자 파악
        log_no = parse_log_no(real_blog_post_url)
        body_identifier = parse_body_identifier(log_no).split('#')[1]

        # 본문 파싱
        blog_post_content = driver.find_element_by_id(body_identifier)

        # 이미지와 이모티콘 파싱
        images, imos = parse_images(blog_post_content)

        # 비디오 파싱
        videos = parse_videos(blog_post_content)
        print('parse done')

        # print code
        print('[images(', len(images), ')]' )
        for i in images:
            print(i)
        print('[imoticons(', len(imos), ')]' )
        for im in imos:
            print(im)
        print('[videos(', len(videos), ')]' )
        for v in videos:
            print(v)

    except Exception as e:
        print('Multimedia parse failed : ')
        print(e)