import requests, json
import constants

def load_module():
    HOST_IP = constants.ServerInfo.CONNECTION_INFO['default']['HOST']
    HOST_PORT = constants.ServerInfo.CONNECTION_INFO['default']['PORT']
    
    PARAMETER = 'request/admin/model/load'

    HOST_URL = 'http://' + HOST_IP + ':' + HOST_PORT + '/' + PARAMETER

    try:
        admin_id = input('ID:')
        admin_pw = input('PW:')
        
        data = {}
        data['id'] = admin_id
        data['pw'] = admin_pw
        
        json_data = json.dumps(data)
        
        response = requests.post(HOST_URL, data=json_data)

        if response.status_code == 200 or response.status_code == 200:
            json_array = json.loads(response.text)
            print('hi')
            pass
    except Exception as e:
        print('[SYSTEM][core_task]Failed to load_module.\n', e)
    

def org_create_sent():
    user_word = input('단어 입력 : ')
    # created_sent = lorem_analyzer.org_craete_sent(user_word)
    print('생성된 문장 : ')
    # print(created_sent)

def get_distance():
    user_sent = input('문장 입력 : ')
    # distances = lorem_analyzer.get_distance(user_sent)
    # mean, variance, standard_deviation = lorem_analyzer.distance_describe(distances)

    # distances_with_token = lorem_analyzer.distances_with_token(user_sent, distances)
    print('')
    print('토큰 : ')
    # print(str(distances_with_token[0]))
    # print(str(distances_with_token[1]))
    # 평균값 내보기
    # print('평균값 : ' + str(mean))
    # 분산 내보기
    # print('분산 : ' + str(variance))
    # 표준편차 구하기
    # print('표준편차 : ' + str(standard_deviation))
    # print('')

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