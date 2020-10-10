import os, platform, time
import string
from selenium import webdriver
from bs4 import BeautifulSoup
from . import naverblogcrawler
from . import multimedia

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
            if 'se-oglink' in c:
                src = node.get_attribute('href')
                width = node.size['width']
                height = node.size['height']

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


# 게시글 타입별 본문 지정. 본문만 선택할 수 있으면 본문 노드 반환.(Selenium)
def parse_main_content(content):
    main = content.find_element_by_class_name('se-main-container')
    if main:
        return main
    else:
        main = content.find_element_by_class_name('__se_component_area')
        if main:
            return main
        else:
            return content

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
        real_blog_post_url = naverblogcrawler.parse_real_blog_post_url(blog_post_url)

        # 리얼 블로그 주소를 셀레니움으로 파싱
        driver.get(real_blog_post_url)
        
        # 게시물 번호 추출 후 본문 식별자 파악
        log_no = naverblogcrawler.parse_log_no(real_blog_post_url)
        body_identifier = naverblogcrawler.parse_body_identifier(log_no).split('#')[1]

        # 본문 파싱
        blog_post_content = driver.find_element_by_id(body_identifier)
        main_content = parse_main_content(blog_post_content)

        time.sleep(2)
        # 본문 크기 구하기
        content_height = main_content.size['height']
        content_width = main_content.size['width']

        # 이미지와 이모티콘 파싱
        images, imos = parse_images(main_content)

        # 비디오 파싱
        videos = parse_videos(main_content)

        # hyperlink 파싱
        hyperlinks = parse_hyperlink(main_content)

        # iframe 파싱
        etcs = parse_etc(main_content)

        print('parse done')

        # 본문의 전체 크기(사실 제목이랑 )
        print('content_height', content_height)
        print('content_width', content_width)
        entire_content_pixel = content_height * content_width

        # 멀티미디어의 종류별 수, URL 및 가로세로 길이  표시, 그리고 pixel수의 합 구하기
        print('[images(', len(images), ')]' )
        entire_images_pixel = 0
        for i in images:
            entire_images_pixel += i._width * i._height
        entire_images_ratio = entire_images_pixel / entire_content_pixel

        print('[imoticons(', len(imos), ')]' )
        entire_imos_pixel = 0
        for im in imos:
            entire_imos_pixel += im._width * im._height
        entire_imos_ratio = entire_imos_pixel / entire_content_pixel

        print('[videos(', len(videos), ')]' )
        entire_videos_pixel = 0
        for v in videos:
            entire_videos_pixel += v._width * v._height
        entire_videos_ratio = entire_videos_pixel / entire_content_pixel

        print('[hyperlink(', len(hyperlinks), ')]' )
        entire_hyperlinks_pixel = 0
        for h in hyperlinks:
            entire_hyperlinks_pixel += h._width * h._height
        entire_hyperlinks_ratio = entire_hyperlinks_pixel / entire_content_pixel

        print('[etcs(', len(etcs), ')]' )
        entire_etcs_pixel = 0
        for e in etcs:
            entire_etcs_pixel += e._width * e._height
        entire_etcs_ratio = entire_etcs_pixel / entire_content_pixel

        # 멀티미디어 종류별 비율 구하기
        if entire_images_pixel is not 0:
            print('이미지의 비율 : ', str(round(entire_images_ratio, 3) * 100), '%')
        if entire_imos_pixel is not 0:
            print('이모티콘의 비율 : ', str(round(entire_imos_ratio, 3) * 100), '%')
        if entire_videos_pixel is not 0:
            print('비디오의 비율 : ', str(round(entire_videos_ratio, 3) * 100), '%')
        if entire_hyperlinks_ratio is not 0:
            print('하이퍼링크 비율 : ', str(round(entire_hyperlinks_ratio, 3) * 100), '%')
        if entire_etcs_ratio is not 0:
            print('기타 비율 : ', str(round(entire_etcs_ratio, 3) * 100), '%')

        # 번외, 그럼 공백 및 텍스트의 비율은?
        left_pixel = entire_content_pixel - entire_images_pixel - entire_imos_pixel - entire_videos_pixel - entire_hyperlinks_pixel - entire_etcs_pixel
        print('텍스트 및 공백의 비율 : ', str(round(left_pixel / entire_content_pixel, 3) * 100 ), '%')
        pass

    except Exception as e:
        print('Multimedia parse failed : ')
        print(e)