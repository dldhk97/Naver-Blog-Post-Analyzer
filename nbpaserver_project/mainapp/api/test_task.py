from .analyzer import lorem_analyzer

# 사용자에게 문장을 받아 로렘 분석함.
def lorem_analyze(json_data):
    response = {}
    response['task_type'] = 'admin_analyzesents'
    response['success'] = 'False'
    response['message'] = '글 분석 도중 오류가 발생했습니다!'

    try:
        # 사용자에게 문장을 받습니다. 여러 줄일 수 있으며 개행은 \n으로 되어있습니다.
        sents = json_data['sents']

        # 현재 한 문장만 분석이 가능하므로, 제일 첫 줄만 분석합니다.
        sent = sents.split('\n')[0]

        # 로렘 분석하여 랭킹(거리) 구함
        distances = lorem_analyzer.get_distance(sent)
        if distances:
            # 토큰화된 문장 배열 얻음.
            tokens = lorem_analyzer.tokenize(sent)

            # 평균, 분산, 표준편차를 구함.
            mean, variance, standard_deviation = lorem_analyzer.distance_describe(distances)

            response['success'] = 'True'
            response['message'] = '분석이 성공적으로 완료되었습니다!'
            
            response['distances'] = str(distances)
            response['tokens'] = str(tokens)
            response['mean'] = str(mean)
            response['variance'] = str(variance)
            response['standard_deviation'] = str(standard_deviation)
        else:
            response['message'] = '거리 배열 분석 실패. 오류가 발생했거나 모델이 준비되어 있지 않습니다.'

    except Exception as e:
        print('[SYSTEM][auth_task] Error occured!', e)

    return response