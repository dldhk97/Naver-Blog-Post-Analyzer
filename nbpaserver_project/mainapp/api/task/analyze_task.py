from ..analyzer.lorem_analyzer import get_lorem_percentage, distance_describe

def analyze_task(task):
    result = {}
    
    # 본문은 여러줄이지만, 일단 돌아갈 수 있게 첫줄만 분석. 여러줄 분석이 미구현이므로.
    sents = str(task._dict['body'])
    try:
        lorem_percentage = get_lorem_percentage(sents)
        print('lorem_percentage : ', lorem_percentage)

        # 태그유사성은 미구현이므로 패스... 구현이 된다면 코드를 바꾸면 됨.
        tag_similarity = 0;

        result['lorem_percentage'] = lorem_percentage
        result['tag_similarity'] = tag_similarity
        
    except Exception as e:
        print('[SYSTEM][core_job][analyze_job] URL (' + task._log_no +', ' + task._log_no + ') failed to analysis!')

    return [task, result]