from ..analyzer.lorem_analyzer import get_distance, distance_describe

def analyze_task(task):
    result = {}
    
    # 본문은 여러줄이지만, 일단 돌아갈 수 있게 첫줄만 분석. 여러줄 분석이 미구현이므로.
    first_line = str(task._dict['body']).split('\n')[0]
    try:
        result_tok_list, result_prob_list = get_distance(first_line)

        # 현재 정확한 확률을 못구하니까, 그냥 대충 확률 배열이 평균을 확률이라 한다.
        mean, variance, standard_deviation = distance_describe(result_prob_list)
        lorem_percentage = mean

        # 태그유사성은 미구현이므로 패스... 구현이 된다면 코드를 바꾸면 됨.
        tag_similarity = 0;

        result['lorem_percentage'] = lorem_percentage
        result['tag_similarity'] = tag_similarity
        
    except Exception as e:
        print('[SYSTEM][core_job][analyze_job] URL (' + task._log_no +', ' + task._log_no + ') failed to analysis!')

    return [task, result]