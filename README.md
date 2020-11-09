# Naver Blog Post Analyzer
네이버 블로그 게시글 분석기(Naver Blog Post Analyzer)

크롬 확장프로그램과 연동하여 네이버 블로그 게시글의 정보를 분석합니다.

Django 서버와 관리자용 콘솔 클라이언트로 구성되어 있습니다.


## 설치방법(Windows)
```
# 필수 pip 패키지 설치
python -m pip install -r .\requirements.txt

# torch 설치(gpu/cpu 선택적 설치)

# cuda 사용
python -m pip install torch==1.5.1+cu101 -f https://download.pytorch.org/whl/torch_stable.html
# cpu 사용
python -m pip install torch==1.5.1+cpu -f https://download.pytorch.org/whl/torch_stable.html

# constants.py 생성 (constants.py.bak을 constants.py로 바꾸거나 복사)
copy constants.py.bak constants.py

# constants.py 수정 (NaverAPI)
class NaverAPI(object):
    NAVER_CLIENT_ID = '네이버 API ID'
    NAVER_CLIENT_SECRET = '네이버 API SECRET'

class DBInfo(object):
    DATABASE_INFO = {
        'default' : {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'DB 스키마 이름',
            'USER': '유저 이름',
            'PASSWORD': '패스워드',
            'HOST': '주소',
            'PORT': '포트',
        }
    }

# DB 스키마가 없는 경우 DB구축
python .\nbpaserver_project\manage.py makemigrations
python .\nbpaserver_project\manage.py migrate

# Django 관리자 계정 생성
python .\nbpaserver_project\manage.py createsuperuser
```