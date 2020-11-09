import requests, json
import constants

HOST_IP = constants.ServerInfo.CONNECTION_INFO['default']['HOST']
HOST_PORT = constants.ServerInfo.CONNECTION_INFO['default']['PORT']
HOST_URL_HEAD = 'http://' + HOST_IP + ':' + HOST_PORT

def authorization(admin_id, admin_pw):
    HOST_URL = HOST_URL_HEAD + '/request/admin/test/authorization'

    try:
        data = {}
        data['id'] = admin_id
        data['pw'] = admin_pw
        
        json_data = json.dumps(data)
        
        response = requests.post(HOST_URL, data=json_data)

        if response.status_code == 200 or response.status_code == 200:
            json_data = json.loads(response.text)
            if json_data['success'] == 'True':
                return True
            else:    
                print('[SERVER]', json_data['message'])
                return False

        print('[CLEINT][core_task] Response error occured')
    except Exception as e:
        print('[CLEINT][core_task] Authorization exception occured.\n', e)

def load_module():
    HOST_URL = HOST_URL_HEAD + '/request/admin/model/load'

    try:        
        response = requests.get(HOST_URL)

        if response.status_code == 200 or response.status_code == 200:
            json_data = json.loads(response.text)
            print('[SERVER]', json_data['message'])
    except Exception as e:
        print('[CLEINT][core_task]Failed to load_module.\n', e)

def lorem_analyze():
    HOST_URL = HOST_URL_HEAD + '/request/admin/test/lorem_analyze'
    
    try:
        # 현재 한 줄만 분석이 가능하므로, 여러 문장을 전송해도 한 문장만 분석합니다.
        line_cnt = input('몇줄짜리 글입니까? : ')
        print('글을 입력하세요 : ')
        sents = ""
        for s in range(int(line_cnt)):
            sents += input() + '\n'

        data = {}
        data['sents'] = sents
        
        json_data = json.dumps(data)
        
        response = requests.post(HOST_URL, data=json_data)

        if response.status_code == 200 or response.status_code == 200:
            json_data = json.loads(response.text)
            if json_data['success'] == 'True':
                print('')
                print('토큰 : ')
                print(json_data['distances'])
                print(json_data['tokens'])
                print('평균값 : ' + json_data['mean'])
                # 분산 내보기
                print('분산 : ' + json_data['variance'])
                # 표준편차 구하기
                print('표준편차 : ' + json_data['standard_deviation'])
                print('')

                return True
            else:    
                print('[SERVER]', json_data['message'])
                return False

        print('[CLEINT][core_task] Response error occured')
    except Exception as e:
        print('[CLEINT][core_task] Lorem_analyze exception occured.\n', e)

def crawl_by_search_word():
    search_word = input('검색어 : ')
    if search_word is not None:
        blog_post_count = input('크롤링할 포스트의 개수 : ')
        try:
            if blog_post_count.isdigit:
                # naver_blog_post_crawler.crawl_by_search_word(search_word, int(blog_post_count))
                pass 
            else:
                print('크롤링할 포스트의 개수가 올바르지 않습니다.')
        except Exception as e:
            print(e)
    else:
        print('검색어가 올바르지 않습니다.')

def crawl_single_post():
    url = input('URL : ')
    if url is not None:
        # naver_blog_post_crawler.crawl_single_post(url)
        pass 
    else:
        print('URL이 올바르지 않습니다.')

def crawl_multimedia():
    url = input('URL : ')
    if url is not None:
        # images_ratio, imos_ratio, videos_ratio, hyperlinks_ratio, etcs_ratio, texts_ratio, blanks_ratio = multimediacrawler.get_multimedia(url)
        
        # 멀티미디어 종류별 비율 표시
        # print('이미지의 비율 : ', str(round(images_ratio, 3) * 100), '%')
        # print('이모티콘의 비율 : ', str(round(imos_ratio, 3) * 100), '%')
        # print('비디오의 비율 : ', str(round(videos_ratio, 3) * 100), '%')
        # print('하이퍼링크 비율 : ', str(round(hyperlinks_ratio, 3) * 100), '%')
        # print('기타(iframe) 비율 : ', str(round(etcs_ratio, 3) * 100), '%')
        # print('텍스트 비율 : ', str(round(texts_ratio, 3) * 100), '%')
        # print('공백 비율 : ', str(round(blanks_ratio, 3) * 100), '%')
        pass
    else:
        print('URL이 올바르지 않습니다.')

def test_db_connection():
    # db_connector.test_connection()
    pass