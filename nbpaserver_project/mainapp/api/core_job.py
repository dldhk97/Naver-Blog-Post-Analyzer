from .crawler import naverblogcrawler, multimediacrawler
from .analyzer.Keyword_Extractor import analyze_keywords
from .analyzer.lorem_analyzer import get_distance, distance_describe
from .crawler import blogpost

MULTIMEDIA_RATIO_TYPES = ['image', 'imoticon', 'video', 'hyperlink', 'text', 'blank', 'etc']

def bloginfo_job(target_url):
    '''
    URL을 받으면 크롤링하여 BlogPost 객체로 반환
    '''
    blog_post = naverblogcrawler.pasre_blog_post(target_url)
    return blog_post

def keyword_job(blog_info):
    '''
    blog_info 객체를 받아 키워드 추출 후 문자열 리스트 반환
    '''
    keywords = analyze_keywords(blog_info.body, top_k=20)
    
    keyword_list = []
    for k in keywords:
        keyword = k[0]          # 단어/형태 모양으로 들어감
        keyword_list.append(keyword)

    return keyword_list

def analyze_job(blog_info):
    result = {}
    
    # 본문은 여러줄이지만, 일단 돌아갈 수 있게 첫줄만 분석. 여러줄 분석이 미구현이므로.
    first_line = str(blog_info.body).split('\n')[0]
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
        print('[SYSTEM][core_job][analyze_job] URL (' + blog_info.log_no +', ' + blog_info.log_no + ') failed to analysis!')

    return result

def multimedia_job(blog_info):
    # 셀레니움 크롤링 후 멀티미디어 비율을 저장한다.
    crawled_multimedia_ratios = multimediacrawler.get_multimedia(blog_info.url)

    # float 값만 있는 ratios 배열을 모델 배열로 바꾸면서, DB에는 저장한다.
    multimedia_ratios = []
    for i in range(len(crawled_multimedia_ratios)):

        value = crawled_multimedia_ratios[i]
        if value == 0:
            continue

        ratio = {}
        ratio['ratio'] = value
        ratio['ratio_type'] = MULTIMEDIA_RATIO_TYPES[i]
        multimedia_ratios.append(ratio)

    return multimedia_ratios