from ..analyzer.Keyword_Extractor import analyze_keywords

def keyword_task(task):
    '''
    body를 받아 키워드 추출 후 문자열 리스트 반환
    '''
    print('keyword_task started')

    keyword_list = []
    try:
        keywords = analyze_keywords(task._dict['body'], top_k=20)
        print('keyword_task analyzed done : ', str(len(keywords)))
        
        for k in keywords:
            keyword = k[0]          # 단어/형태 모양으로 들어감
            keyword_list.append(keyword)
            print(keyword)
        
    except Exception as e:
        print(e)

    return [task, keyword_list]
    
    

    