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

            response['success'] = 'True'
            response['message'] = '분석이 성공적으로 완료되었습니다!'
            
            response['tokens'] = str(tokens)
            response['lorem_percentage'] = str(lorem_percentage)
        else:
            response['message'] = '로렘 분석 실패. 오류가 발생했거나 문장이 너무 짧습니다.'

    except Exception as e:
        print('[SYSTEM][test_task] Error occured at lorem_analyze!\n', e)

    return response