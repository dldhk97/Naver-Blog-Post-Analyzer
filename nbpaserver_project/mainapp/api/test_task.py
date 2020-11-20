from .analyzer import lorem_analyzer
from .crawler import naverblogcrawler
from .crawler.util import url_normalization
from .task.task_manager import fetch_blog_info

# 관리자에게 문장을 받아 로렘 분석함.
def lorem_analyze(json_data):
    response = {}
    response['task_type'] = 'lorem_analyze'
    response['success'] = 'False'
    response['message'] = '글 분석 도중 오류가 발생했습니다!'

    try:
        # 사용자에게 문장을 받습니다. 여러 줄일 수 있으며 개행은 \n으로 되어있습니다.
        sents = json_data['sents']

        # 로렘 분석하여 확률 구함
        lorem_percentage, samples = lorem_analyzer.get_lorem_percentage(sents, False)

        if lorem_percentage > -1:
            # 토큰화된 문장 배열 얻음.
            tokens = lorem_analyzer.tokenize(sents)      

            response['success'] = 'True'
            response['message'] = '분석이 성공적으로 완료되었습니다!'
            
            response['tokens'] = str(tokens)
            response['lorem_percentage'] = str(lorem_percentage)
            
            # 각 샘플에 대해서 토큰, 확률배열도 가져옴
            i = 1
            for s in samples:
                sample_org = s.split(')')[1].strip()
                token_arr, prob_arr = lorem_analyzer.get_probablities(sample_org)
                current = 'sample_' + str(i) 
                response[current] = samples[i - 1]
                response[current + '_tokens'] = token_arr
                response[current + '_probs'] = prob_arr
                i += 1
        else:
            response['message'] = '로렘 분석 실패. 오류가 발생했거나 문장이 너무 짧습니다.'

    except Exception as e:
        print('[SYSTEM][test_task] Error occured at lorem_analyze!\n', e)

    return response

def analyze_post_body(json_data):
    response = {}
    response['task_type'] = 'lorem_analyze'
    response['success'] = 'False'

    try:
        org_url = json_data['url']
        target_url = url_normalization(org_url)

        # URL 정규화에 실패한 경우
        if not target_url:
            print(org_url + ' 은 제한된 블로그이거나, 비공개 게시글이입니다.')
            response['message'] = org_url + ' 은 제한된 블로그이거나, 비공개 게시글이입니다.'
            return response
        
        blog_info, tag_list, hyperlink_list = fetch_blog_info(target_url)

        if blog_info is None:
            print('[SYSTEM][test_task][analyze_blog_body] Failed to fetch blog_info!')

        # 로렘 분석하여 확률 구함
        lorem_percentage, samples = lorem_analyzer.get_lorem_percentage(blog_info.body)

        if lorem_percentage > -1:

            response['success'] = 'True'
            response['message'] = '분석이 성공적으로 완료되었습니다!'
            response['lorem_percentage'] = str(lorem_percentage)
            
            # 각 샘플에 대해서 토큰, 확률배열도 가져옴
            i = 1
            for s in samples:
                sample_org = s.split(')')[1].strip()
                token_arr, prob_arr = lorem_analyzer.get_probablities(sample_org)
                current = 'sample_' + str(i) 
                response[current] = samples[i - 1]
                response[current + '_tokens'] = token_arr
                response[current + '_probs'] = prob_arr
                i += 1
        else:
            response['message'] = '게시글 분석에 실패하였습니다. 본문이 없는 게시글이거나 본문이 너무 짧습니다!'
            
    except Exception as e:
        print('[SYSTEM][test_task] Error occured at analyze_post_body!\n', e)
        response['message'] = '게시글 분석 도중 오류가 발생했습니다!'

    return response