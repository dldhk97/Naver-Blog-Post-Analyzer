from ..analyzer.Keyword_Extractor import analyze_keywords

EXCEPT_TAG = ['NNB', 'NR', 'NP']

def keyword_task(task):
    '''
    body를 받아 키워드 추출 후 문자열 리스트 반환
    '''
    print('keyword_task started')

    keyword_list = []
    try:
        keywords = analyze_keywords(task._dict['body'], top_k=50)
        if not keywords:
            print('키워드 분석을 하였으나, 문서 길이가 너무 짧거나 분석할 수 없는 문서(' + task._blog_id + ', ' + task._log_no + ')')
            keywords = [['분석불가/ERR', ]]
        
        print('keyword_task analyzed done : ', str(len(keywords)))
        
        for k in keywords:
            # 의존명사인 경우 제외함.
            keyword = k[0]
            if keyword.split('/')[1] not in EXCEPT_TAG:
                keyword_list.append(keyword)
                print(keyword, ' appended.')
            else:
                print(keyword, ' excepted.')

        # 추출된 키워드가 없을 경우
        if len(keyword_list) <= 0:
            keyword_list.append('키워드없음/EER')
        
    except Exception as e:
        print('[keyword_task]', e)

    return [task, keyword_list]
    
    

    