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

        # 로렘 분석하여 확률 구함
        lorem_percentage = lorem_analyzer.get_lorem_percentage(sents)

        if lorem_percentage > -1:
            # 토큰화된 문장 배열 얻음.
            tokens = lorem_analyzer.tokenize(sents)

            # 현재 정확한 확률을 못구하니까, 그냥 대충 확률 배열이 평균을 확률이라 한다.
            # mean, variance, standard_deviation = lorem_analyzer.distance_describe(result_prob_list)
            # lorem_percentage = mean            

            response['success'] = 'True'
            response['message'] = '분석이 성공적으로 완료되었습니다!'
            
            response['tokens'] = str(tokens)
            response['distances'] = str(0)
            response['mean'] = str(0)
            response['variance'] = str(0)
            response['standard_deviation'] = str(0)
            response['lorem_percentage'] = str(lorem_percentage)
        else:
            response['message'] = '거리 배열 분석 실패. 오류가 발생했거나 모델이 준비되어 있지 않습니다.'

    except Exception as e:
        print('[SYSTEM][test_task] Error occured at lorem_analyze!\n', e)

    return response