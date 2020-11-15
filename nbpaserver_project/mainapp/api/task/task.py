from enum import Enum

class TaskType(Enum):
    BLOG_INFO = 1
    KEYWORD = 2
    ANALYZE = 3
    MULTIMEDIA = 4

class Task:
    def __init__(self, task_type, blog_id, log_no, url):
        self._task_type = task_type
        self._blog_id = blog_id
        self._log_no = log_no
        self._url = url
        self._dict = {}
        