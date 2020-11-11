from .analyzer import lorem_analyzer
from .crawler import naverblogcrawler

# 사용자에게 문장을 받아 로렘 분석함.
def lorem_analyze(json_data):
    response = {}
    response['task_type'] = 'lorem_analyze'
    response['success'] = 'False'
    response['message'] = '글 분석 도중 오류가 발생했습니다!'

    try:
        # 사용자에게 문장을 받습니다. 여러 줄일 수 있으며 개행은 \n으로 되어있습니다.
        sents = json_data['sents']

        # 현재 한 문장만 분석이 가능하므로, 제일 첫 줄만 분석합니다.
        sent = sents.split('\n')[0]

        # 로렘 분석하여 랭킹(거리) 구함
        result_tok_list, result_prob_list = lorem_analyzer.get_distance(sent)
        if result_prob_list:
            # 토큰화된 문장 배열 얻음.
            tokens = lorem_analyzer.tokenize(sent)

            # 평균, 분산, 표준편차를 구함.
            # mean, variance, standard_deviation = lorem_analyzer.distance_describe(distances)

            response['success'] = 'True'
            response['message'] = '분석이 성공적으로 완료되었습니다!'
            
            response['tokens'] = str(result_tok_list)
            response['distances'] = str(result_prob_list)
            response['mean'] = '평균스'
            response['variance'] = '분산스'
            response['standard_deviation'] = '표준편차스'
        else:
            response['message'] = '거리 배열 분석 실패. 오류가 발생했거나 모델이 준비되어 있지 않습니다.'

    except Exception as e:
        print('[SYSTEM][test_task] Error occured at lorem_analyze!\n', e)

    return response

# 사용자에게 검색어, 게시글 개수를 받아 크롤링함
def crawl_by_search_word(json_data):
    response = {}
    response['task_type'] = 'crawl_by_search_word'
    response['success'] = 'False'
    response['message'] = '크롤링 도중 오류가 발생하였습니다!'

    try:
        search_word = json_data['search_word']
        blog_post_count = json_data['blog_post_count']

        blog_post_list = naverblogcrawler.naver_blog_crawling(search_word, 100, "sim", blog_post_count)

        if blog_post_list:
            response['success'] = 'False'
            for blog_post in blog_post_list:
                blog_post
                pass

    except Exception as e:
        print('[SYSTEM][test_task] Error occured at crawl_by_search_word!\n', e)
        pass