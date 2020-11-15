import requests, json
import constants

HOST_IP = constants.ServerInfo.CONNECTION_INFO['default']['HOST']
HOST_PORT = constants.ServerInfo.CONNECTION_INFO['default']['PORT']
HOST_URL_HEAD = 'http://' + HOST_IP + ':' + HOST_PORT + '/request/'

def authorization(admin_id, admin_pw):
    url = HOST_URL_HEAD + 'admin/test/authorization'

    try:
        data = {}
        data['id'] = admin_id
        data['pw'] = admin_pw
        
        json_data = json.dumps(data)
        
        response = requests.post(url, data=json_data)

        if response.status_code == 200 or response.status_code == 201:
            json_data = json.loads(response.text)
            if json_data['success'] == 'True':
                return True
            else:    
                print('[SERVER]', json_data['message'])
                return False

        print('[CLEINT][core_task] Authorization failed! Status_code is not 200 or 201!')
    except Exception as e:
        print('[CLEINT][core_task] Exception occured at authorization\n', e)

def load_module():
    url = HOST_URL_HEAD + 'admin/model/load'

    try:        
        response = requests.get(url)

        if response.status_code == 200 or response.status_code == 201:
            json_data = json.loads(response.text)
            print('[SERVER]', json_data['message'])
            return True

        print('[CLEINT][core_task] Load_module failed! Status_code is not 200 or 201!')
    except Exception as e:
        print('[CLEINT][core_task] Failed to load_module.\n', e)

def lorem_analyze():
    url = HOST_URL_HEAD + 'admin/test/lorem_analyze'
    
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
        
        response = requests.post(url, data=json_data)

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

        print('[CLEINT][core_task] Lorem_analyze error occured! Status_code is not 200 or 201!')
    except Exception as e:
        print('[CLEINT][core_task] Lorem_analyze exception occured.\n', e)

def crawl_by_search_word():
    url = HOST_URL_HEAD + 'admin/test/crawlbysearchword'

    try:
        search_word = input('검색어 : ')
        if search_word is None:
            print('검색어가 올바르지 않습니다.')
            return

        blog_post_count = input('크롤링할 포스트의 개수 : ')
        if not blog_post_count.isdigit:
            print('크롤링할 포스트의 개수가 올바르지 않습니다.')
            return

        data = {}
        data['search_word'] = search_word
        data['blog_post_count'] = blog_post_count
        
        json_data = json.dumps(data)
        
        response = requests.post(url, data=json_data)
        
        if response.status_code == 200 or response.status_code == 200:
            json_data = json.loads(response.text)
            if json_data['success'] == 'True':
                pass
            else:    
                print('[SERVER]', json_data['message'])

        print('[CLEINT][core_task] Crawl_by_search_word error occured! Status_code is not 200 or 201!')
    except Exception as e:
        print('[CLEINT][core_task] Crawl_by_search_word exception occured.\n', e)
        

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

def print_blog_entire_info(blog_info, analyzed_info, multimedia_ratios, tags, hyperlinks, keywords):
    blog_info = blog_info['fields']
    print(blog_info)

    analyzed_info = analyzed_info['fields']
    print(analyzed_info)

    for multimedia_ratio in multimedia_ratios:
        mr = multimedia_ratio['fields']
        print(mr)

    for tag in tags:
        t = tag['fields']
        print(t)

    for hyperlink in hyperlinks:
        h = hyperlink['fields']
        print(h)

    for keyword in keywords:
        k = keyword['fields']
        print(k)

    pass

def get_analyzed_info():
    url = HOST_URL_HEAD + 'admin/test/getanalyzedinfo'
    
    try:
        # url 목록 전송
        line_cnt = input('url의 개수는? : ')

        print('url : ')
        data_list = []

        for _ in range(int(line_cnt)):
            data = {}
            data['url'] = input()
            data_list.append(data)
        
        json_data = json.dumps(data_list)
        
        response = requests.post(url, data=json_data)

        if response.status_code == 200 or response.status_code == 200:
            blog_entire_info_arr = json.loads(response.text)

            header_data = blog_entire_info_arr[0]
                
            if header_data['success'] == 'True':
                
                for info in blog_entire_info_arr[1:]:
                    blog_info = json.loads(info['blog_info'])[0]
                    analyzed_info = json.loads(info['analyzed_info'])[0]
                    multimedia_ratios = json.loads(info['multimedia_ratios'])
                    
                    tags = json.loads(info['tags'])
                    hyperlinks = json.loads(info['hyperlinks'])
                    keywords = json.loads(info['keywords'])
                    
                    print_blog_entire_info(blog_info, analyzed_info, multimedia_ratios, tags, hyperlinks, keywords)
                    

                return True
            else:    
                print('[SERVER]', header_data['message'])
                return False

        print('[CLEINT][core_task] get_analyzed_info error occured! Status_code is not 200 or 201!')
    except Exception as e:
        print('[CLEINT][core_task] get_analyzed_info exception occured.\n', e)

def get_keywords():
    url = HOST_URL_HEAD + 'user/keyword/get'
    
    try:
        # url 목록 전송
        line_cnt = input('url의 개수는? : ')

        print('url : ')
        data_list = []

        for _ in range(int(line_cnt)):
            data = {}
            data['url'] = input()
            data_list.append(data)
        
        json_data = json.dumps(data_list)
        
        response = requests.post(url, data=json_data)

        if response.status_code == 200 or response.status_code == 200:
            blog_entire_info_arr = json.loads(response.text)

            header_data = blog_entire_info_arr[0]
                
            if header_data['success'] == 'True':
                
                for info in blog_entire_info_arr[1:]:
                    keywords = json.loads(info['keywords'])
                    
                    for keyword in keywords:
                        k = keyword['fields']
                        print(k)

                return True
            else:    
                print('[SERVER]', header_data['message'])
                return False

        print('[CLEINT][core_task] get_analyzed_info error occured! Status_code is not 200 or 201!')
    except Exception as e:
        print('[CLEINT][core_task] get_analyzed_info exception occured.\n', e)

def get_bloginfo():
    url = HOST_URL_HEAD + 'user/bloginfo/get'
    
    try:
        # url 목록 전송
        line_cnt = input('url의 개수는? : ')

        print('url : ')
        data_list = []

        for _ in range(int(line_cnt)):
            data = {}
            data['url'] = input()
            data_list.append(data)
        
        json_data = json.dumps(data_list)
        
        response = requests.post(url, data=json_data)

        if response.status_code == 200 or response.status_code == 200:
            blog_entire_info_arr = json.loads(response.text)

            header_data = blog_entire_info_arr[0]
                
            if header_data['success'] == 'True':
                
                for info in blog_entire_info_arr[1:]:
                    blog_info = json.loads(info['blog_info'])[0]
                    blog_info = blog_info['fields']
                    print(blog_info)

                return True
            else:    
                print('[SERVER]', header_data['message'])
                return False

        print('[CLEINT][core_task] get_analyzed_info error occured! Status_code is not 200 or 201!')
    except Exception as e:
        print('[CLEINT][core_task] get_analyzed_info exception occured.\n', e)

