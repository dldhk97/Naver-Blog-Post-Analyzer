import os, platform, time
import string

from selenium import webdriver
from bs4 import BeautifulSoup
from . import naverblogcrawler, multimedia, util


# 설치되어있는 크롬의 버전에 맞는 드라이버를 사용하십시오.
driver = None

def prepare_selenium():
    global driver
    options = webdriver.ChromeOptions()
    # options.add_argument('--start-maximized') # 창의 크기를 최대로
    # options.add_argument('headless')          # 윈도우 창이 표시되지 않는 헤드리스 모드

    driver_name = None
    if platform.system() == 'Linux':
        print('Platform is Linux')
        driver_name = 'chromedriver85_linux'
    else:
        print('Platform is Windows')
        driver_name = 'chromedriver87_win.exe'
    
    driver_path = os.getcwd() + os.sep + 'nbpaserver_project' + os.sep + 'mainapp' + os.sep + 'api' + os.sep + 'crawler' + os.sep + 'bin' + os.sep + driver_name

    print('Using this driver : ' + driver_path)

    driver = webdriver.Chrome(executable_path=driver_path, chrome_options=options)
    
    driver.implicitly_wait(5)

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
            # 영상의 섬네일?
            elif src.startswith('data:image/'):
                print('WARNING! This image seems video thumbnail.')     # 중복연산 회피
                # print(src)
                continue
            
            width = node.size['width']
            height = node.size['height']

            # 크기가 0이면 패스
            if width * height <= 0:
                continue

            # 네이버 이모티콘인경우 이모티콘 리스트에 추가
            if 'storep-phinf.pstatic.net' in src:
                imoticon_list.append(multimedia.MultiMedia('imoticon', src, width, height))
            else:
                image_list.append(multimedia.MultiMedia('image', src, width, height))

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

                video_list.append(multimedia.MultiMedia('video', src, width, height))
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
                video_list.append(multimedia.MultiMedia('video', s, width, height))
        except Exception as e:
            print('[parse_videos(N)] ERROR : ' , e)

    return video_list

def parse_hyperlink(blog_post_content):
    hyperlink_list = []

    # 하이퍼링크 잡기
    for node in blog_post_content.find_elements_by_tag_name('a'):
        try:
            c = node.get_attribute('class')
            #if 'se-oglink' in c:

            width = node.size['width']
            height = node.size['height']
            if width * height <= 0:
                continue

            src = node.get_attribute('href')

            # 네이버 지도 패스
            if "openstreetmap.org/copyright" in src:
                continue
            
            # 네이버 블로그 패스
            if "blog.naver.com" in src:
                continue
            
            # 하이퍼링크인데 텍스트가 없다? 그럼 하위에 이미지가 있다면 이미지로 취급(중복연산 회피)
            if not (node.text and node.text.strip()):
                if len(node.find_elements_by_tag_name('img')) > 0:
                    print('WARNING! This hyperlink seems image.')
                    continue

            hyperlink_list.append(multimedia.MultiMedia('hyperlink', src, width, height))
        except Exception as e:
            print('[parse_etc] ERROR : ' , e)

    return hyperlink_list

# 기타 iframe 목록 추출(인스타그램 영상, 광고 )
def parse_etc(blog_post_content):
    etc_list = []

    # iframe 잡기, 유튜브는 제외
    for node in blog_post_content.find_elements_by_tag_name('iframe'):
        try:
            if 'www.youtube.com' in node.get_attribute('src'):
                continue
            
            src = node.get_attribute('src')
            width = node.size['width']
            height = node.size['height']

            etc_list.append(multimedia.MultiMedia('etc', src, width, height))
        except Exception as e:
            print('[parse_etc] ERROR : ' , e)

    return etc_list

# text 목록 추출
def parse_text(blog_post_content):
    text_list = []

    # 텍스트 잡기 p
    for node in blog_post_content.find_elements_by_tag_name("p"):       # span으로 하면 순수히 글자의 크기를 잡고, p로 잡으면 한줄 통째로 잡음
        try:
            src = node.text
            if src and src.strip():
                width = node.size['width']
                height = node.size['height']
                text_list.append(multimedia.MultiMedia('text', src, width, height))
                # print(src)

        except Exception as e:
            print('[parse_etc] ERROR : ' , e)

    # 틀딱 블로그는 td로 잡아야하드라. 코드가 너무 비효율적인데, xpath로 or 연산했을때 일반 블로그에서 이상하게 되어버려서, 틀 페이지 아닌 페이지 따로 돌려야할듯.
    if not text_list:
        for node in blog_post_content.find_elements_by_tag_name("td"):
            try:
                src = node.text
                if src and src.strip():
                    width = node.size['width']
                    height = node.size['height']
                    text_list.append(multimedia.MultiMedia('text', src, width, height))
                    print(src)

            except Exception as e:
                print('[parse_etc] ERROR : ' , e)

    return text_list


# 게시글 타입별 본문 지정. 본문만 선택할 수 있으면 본문 노드 반환.(Selenium)
def parse_main_content(content):
    try:
        return content.find_element_by_class_name('se-main-container')
    except Exception as e:
        print('parse_main_content:: Cannot find se-main-container')
    
    try:
        return content.find_element_by_class_name('__se_component_area')
    except Exception as e:
        print('parse_main_content:: Cannot find __se_component_area')

    return content

# 멀티미디어 비율 계산
def calc_ratio(multimedia_list, entire_content_pixel):
    entire_multimedia_pixel = 0

    for meida in multimedia_list:
        entire_multimedia_pixel += meida._width * meida._height
    ratio = entire_multimedia_pixel / entire_content_pixel

    return ratio


def get_multimedia(blog_post_url):
    # 네이버 블로그인 경우만 처리함.
    if 'blog.naver.com' not in blog_post_url:
        print(blog_post_url + ' 는 네이버 블로그가 아니라 패스합니다')
        return

    try:
        if driver is None:
            # 셀레니움 드라이버 준비
            prepare_selenium()

        # 일반 url에서 bs4로 log_no, blog_id가 포함된 post_view_url 추출
        post_view_url = util.url_normalization(blog_post_url)

        # 리얼 블로그 주소를 셀레니움으로 파싱
        driver.get(post_view_url)
        
        # 게시물 번호 추출 후 본문 식별자 파악
        blog_id, log_no = util.get_post_identifier_from_url(post_view_url)
        body_identifier = naverblogcrawler.parse_body_identifier(log_no).split('#')[1]

        # 본문 파싱
        blog_post_content = driver.find_element_by_id(body_identifier)
        main_content = parse_main_content(blog_post_content)

        time.sleep(1)

        # 본문 크기 구하기
        content_height = main_content.size['height']
        content_width = main_content.size['width']

        # html에서 멀티미디어 객체 리스트 뽑아내기
        images, imos = parse_images(main_content)
        videos = parse_videos(main_content)             # 느림
        hyperlinks = parse_hyperlink(main_content)
        etcs = parse_etc(main_content)                  # 느림
        texts = parse_text(main_content)                # 조금 느림

        print('parse done')

        # 본문의 전체 크기
        entire_content_pixel = content_height * content_width

        # 멀티미디어의 종류별 수, URL 및 가로세로 길이  표시, 그리고 pixel수의 합 구하기
        entire_images_ratio = calc_ratio(images, entire_content_pixel)
        entire_imos_ratio = calc_ratio(imos, entire_content_pixel)
        entire_videos_ratio = calc_ratio(videos, entire_content_pixel)
        entire_hyperlinks_ratio = calc_ratio(hyperlinks, entire_content_pixel)
        entire_etcs_ratio = calc_ratio(etcs, entire_content_pixel)
        entire_texts_ratio = calc_ratio(texts, entire_content_pixel)
        blanks_ratio = 1 - entire_images_ratio - entire_imos_ratio - entire_videos_ratio - entire_hyperlinks_ratio - entire_etcs_ratio - entire_texts_ratio

        # 이미지, 이모티콘, 비디오, 하이퍼링크, 기타(iframe), 텍스트, 공백 비율 반환
        result_arr = [entire_images_ratio, entire_imos_ratio, entire_videos_ratio, entire_hyperlinks_ratio, entire_texts_ratio, blanks_ratio, entire_etcs_ratio]
        return result_arr

    except Exception as e:
        print('[SYSTEM][multimediacrawler] Multimedia parse failed\n', e)