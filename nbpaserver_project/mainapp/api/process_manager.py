# 0. task들은 DB에 원하는 데이터가 없으면, 프로세스 매니저에게 요청한다.
# 1. 프로세스 매니저는 현재 큐에서 task가 원하는 일이 이미 수행중인지 체크한다.
# 2. 동일한 작업이 없다면 Queue에 할일을 추가한다.
# 3. 작업들을 처리하면서, 필요하면 Selenium Thread(Process)를 하나 만들어서 작업하기도 함.
# 4. 싱글톤으로 되어야함. 단순히 DB에서 정보를 get하는건 이 녀석을 거쳐갈 필요가 없음.

class ProcessManager():
    _instance = None
    _msg = None

    @classmethod
    def _getInstance(cls):
        return cls._instance

    @classmethod
    def instance(cls, *args, **kargs):
        cls._instance = cls(*args, **kargs)
        cls.instance = cls._getInstance
        return cls._instance

    def __init__(self):
        self._dict = {}

    def setitem(self, key, item):
        self._dict[key] = item

    def say_hi(self):
        if self._msg:
            print(self._msg)
        else:
            print('msg is none!')

    def set_hi(self, msg):
        self._msg = msg

