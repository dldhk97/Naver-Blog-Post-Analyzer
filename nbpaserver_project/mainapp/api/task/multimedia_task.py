from ..crawler import multimediacrawler

MULTIMEDIA_RATIO_TYPES = ['image', 'imoticon', 'video', 'hyperlink', 'text', 'blank', 'etc']

def multimedia_task(task):
    # 셀레니움 크롤링 후 멀티미디어 비율을 저장한다.
    crawled_multimedia_ratios = multimediacrawler.get_multimedia(task._dict['url'])

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

    return [task, multimedia_ratios]