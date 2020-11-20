from ..analyzer.lorem_analyzer import get_lorem_percentage, distance_describe

def analyze_task(task):
    result = {}
    
    # 본문은 여러줄이지만, 일단 돌아갈 수 있게 첫줄만 분석. 여러줄 분석이 미구현이므로.
    sents = str(task._dict['body'])
    try:
        lorem_percentage, samples = get_lorem_percentage(sents)
        print('lorem_percentage : ', str(lorem_percentage) + ' (' + task._url + ')')

        # 태그유사성은 미구현이므로 패스... 구현이 된다면 코드를 바꾸면 됨.
        tag_similarity = 0;

        result['lorem_percentage'] = lorem_percentage
        result['tag_similarity'] = tag_similarity
        if samples:
            result['sample_1'] = samples[0]
            result['sample_2'] = samples[1] if len(samples) > 1 else ''
            result['sample_3'] = samples[2] if len(samples) > 2 else ''
        else:
            result['sample_1'] = ''
            result['sample_2'] = ''
            result['sample_3'] = ''
        
    except Exception as e:
        print('[SYSTEM][analyze_task][analyze_job] ' + task._blog_id +', ' + task._log_no + ' failed to analysis! URL(' + task._url + ')\n', e)

    return [task, result]