# 별개의 스레드에서 돌아야 함.
# 0. task들은 DB에 원하는 데이터가 없으면, 프로세스 매니저에게 요청한다.
# 1. 프로세스 매니저는 현재 큐에서 task가 원하는 일이 이미 수행중인지 체크한다.
# 2. 동일한 작업이 없다면 Queue에 할일을 추가한다.
# 3. 작업들을 처리하면서, 필요하면 Selenium Thread(Process)를 하나 만들어서 작업하기도 함.
# 4. 싱글톤으로 되어야함. 단순히 DB에서 정보를 get하는건 이 녀석을 거쳐갈 필요가 없음.

# 로직
# 0. TaskManager는 초기화와 동시에 _request_queue 생성 후 runner 실행.
# 1. 외부에서 TaskManager에게 add_task로 작업 요청
# 2. runner는 작업을 받으면, _running_task에 해당 task가 있는지 체크
# 3. 동일한 task가 없다면, _running_task에 넣고 작업 실행!

# from . import Task
import django
django.setup()
from ... import models

from multiprocessing import Process, Queue, Pool
from .task import Task, TaskType
from .bloginfo_task import bloginfo_task
from .keyword_task import keyword_task
from .analyze_task import analyze_task
from .multimedia_task import multimedia_task
from ..util import model_converter
from ..crawler.util import url_normalization, get_post_identifier_from_url

################################

def is_same_task(task1, task2):
    if task1._blog_id != task2._blog_id:
        return False
    if task1._log_no != task2._log_no:
        return False
    if task1._task_type != task2._task_type:
        return False
    return True

def task_to_callable(task):
    if task._task_type == TaskType.BLOG_INFO:
        return bloginfo_task
    if task._task_type == TaskType.KEYWORD:
        return keyword_task
    if task._task_type == TaskType.ANALYZE:
        return analyze_task
    if task._task_type == TaskType.MULTIMEDIA:
        return multimedia_task

##################################

def fetch_ratio_type(ratio_type_name):
    ratio_type = models.RatioType.objects.filter(name=ratio_type_name)[0]
    return ratio_type

def fetch_dictionary_type(dictionary_type_name):
    dictionray_type = models.DictionaryType.objects.filter(name=dictionary_type_name)[0]
    return dictionray_type

def fetch_dictionary(blog_info, dictionary_type_name):
    '''
    해당 블로그의 딕셔너리(django.model) list 반환
    '''
    dict_type = fetch_dictionary_type(dictionary_type_name)
    dicts = models.Dictionary.objects.filter(blog_info=blog_info, dictionary_type=dict_type)

    return list(dicts)

def fetch_blog_info(target_url):
    '''
    DB에 BlogInfo가 있으면 반환, 없으면 크롤러로 파싱하여
    DB에 BlogInfo를 저장하고 하이퍼링크, 태그를 Dictionary 테이블에 저장 후 반환
    '''
    blog_id, log_no = get_post_identifier_from_url(target_url)

    # DB에서 동일한 게시글이 존재하는지 조회. blog_id, log_no가 파싱되면 그걸로 탐색, 없으면 url로 탐색
    if blog_id and log_no:
        bloginfo_arr = models.BlogInfo.objects.filter(blog_id=blog_id, log_no=log_no)
    else:
        bloginfo_arr = models.BlogInfo.objects.filter(url=target_url)

    # DB에 블로그 정보가 없음
    if len(bloginfo_arr) <= 0:
        print('[SYSTEM][core_task] BlogInfo(' + target_url + ') does not exists in database!')

        task = Task(TaskType.BLOG_INFO, blog_id, log_no, target_url)
        result = bloginfo_task(task)
        blog_post = result[1]
        
        blog_info, hyperlink_list, tag_list = model_converter.blog_post_to_django_model(blog_post)

        # DB에 저장
        blog_info.save()
        print('[SYSTEM][core_task] BlogInfo(' + target_url + ') saved in database!')

        for hyperlink in hyperlink_list:
            hyperlink.save()
        print('[SYSTEM][core_task] hyperlink_list(' + target_url + ') saved in database!')

        for tag in tag_list:
            tag.save()
        print('[SYSTEM][core_task] tag_list(' + target_url + ') saved in database!')
    else:
        # DB에 BlogInfo가 존재하면 태그, 하이퍼링크, 키워드 가져옴
        blog_info = bloginfo_arr[0]
        tag_list = fetch_dictionary(blog_info, 'hashtag')
        hyperlink_list = fetch_dictionary(blog_info, 'hyperlink')

    return blog_info, tag_list, hyperlink_list

#######################

RUNNING_TASK = []

def save_model(task, result):
    # 멀티프로세싱이 끝나면, 각 정보들을 DB에 넣을 수 있게 모델 변환 후 저장
    if task._task_type == TaskType.BLOG_INFO:
        return

    try:
        # blog_info_task = Task(TaskType.BLOG_INFO, task._blog_id, task._log_no, task._url)
        blog_info, hyperlink_list, tag_list = fetch_blog_info(task._url)
    except Exception as e:
        print('[process][save_model] Failed to bloginfo_task\n', e)

    try:
        if task._task_type == TaskType.KEYWORD:
            keyword_list = []
            for word in result:
                dict_type = fetch_dictionary_type('keyword')
                converted_keyword = model_converter.dictionary_to_django_model(blog_info, word, dict_type)
                converted_keyword.save()
                keyword_list.append(converted_keyword)
            if len(keyword_list) > 0:
                print('[SYSTEM][core_task] Keywords(' + blog_info.blog_id +', ' + blog_info.log_no + ') saved in database!')
        elif task._task_type == TaskType.ANALYZE:
            if result != {}:
                analyzed_info = result
                converted_analyzed_info = model_converter.analyzed_info_to_django_model(blog_info, analyzed_info['lorem_percentage'], analyzed_info['tag_similarity'])
                converted_analyzed_info.save()
                analyzed_info = converted_analyzed_info
                print('[SYSTEM][core_task] AnalyzedInfo(' + blog_info.blog_id +', ' + blog_info.log_no + ') saved in database!')
        elif task._task_type == TaskType.MULTIMEDIA:
            multimedia_ratio_list = []
            for ratio in result:
                ratio_type = fetch_ratio_type(ratio['ratio_type'])
                converted_ratio = model_converter.multimedia_ratio_to_django_model(blog_info, ratio['ratio'], ratio_type)
                converted_ratio.save()
                multimedia_ratio_list.append(converted_ratio)
            if len(multimedia_ratio_list) > 0:
                print('[SYSTEM][core_task] MultimediaInfo(' + blog_info.blog_id +', ' + blog_info.log_no + ') saved in database!')
    except Exception as e:
        print('[process][save_model] Failed to save\n', e)
        

def task_callback(result_tuple):
    print('task finished')
    task = result_tuple[0]
    result = result_tuple[1]
    print(result)

    # 여기서 DB에 저장해야함.
    save_model(task, result)

    remove_target = None
    for t in RUNNING_TASK:
        if is_same_task(task, t):
            remove_target = t
    
    if remove_target:
        RUNNING_TASK.remove(remove_target)
        print('Task (' + str(task) + ') removed from queue')

def runner(request_queue):
    print('runner run!')

    pool = Pool(processes=4)

    while True:
        try:
            print('runner wating!')
            requested_task = request_queue.get()
            
            # Check if same task exists.
            same_task_exists = False
            for task in RUNNING_TASK:
                if is_same_task(requested_task, task):
                    same_task_exists = True
                    print('same task already running!')
                    break
            
            if not same_task_exists:

                callable_task = task_to_callable(requested_task)
                pool.apply_async(callable_task, (requested_task, ), callback=task_callback)
                RUNNING_TASK.append(requested_task)

                print('data found to be processed: {}'.format(requested_task))
    
        except Exception as e:
            print(e)


class TaskManager():
    _instance = None

    @classmethod
    def _getInstance(cls):
        return cls._instance

    @classmethod
    def instance(cls, *args, **kargs):
        cls._instance = cls(*args, **kargs)
        cls.instance = cls._getInstance
        return cls._instance

    def __init__(self):
        self._request_queue = Queue()
        self._main_process = Process(target=runner, args=(self._request_queue,))
        self._main_process.start()

    def add_task(self, task):
        self._request_queue.put(task)
        pass
        