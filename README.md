# Naver Blog Post Analyzer
네이버 블로그 게시글 분석기(Naver Blog Post Analyzer)

네이버 블로그 게시글 분석기의 서버입니다.

크롬 확장프로그램과 연동하여 네이버 블로그 게시글의 정보를 분석합니다.


## 설치방법(Windows)
```
# 필수 pip 패키지 설치
python -m pip install -r .\requirements.txt

# torch 설치(gpu/cpu 선택적 설치)

# cuda 사용
python -m pip install torch==1.5.1+cu101 -f https://download.pytorch.org/whl/torch_stable.html
# cpu 사용
python -m pip install torch==1.5.1+cpu -f https://download.pytorch.org/whl/torch_stable.html

# KoGPT2 설치
python -m pip install .\KoGPT2\

# constants.py 생성 (constants.py.bak을 constants.py로 바꾸거나 복사)
copy constants.py.bak constants.py

# constants.py 수정 (NaverAPI)
class NaverAPI(object):
    NAVER_CLIENT_ID = '자신의 네이버 API ID'
    NAVER_CLIENT_SECRET = '자신의 네이버 API SECRET'
    
class DB(object):
    HOST_IP = 'localhost'
    PORT = '3306'
    DATABASE_NAME = '데이터베이스 이름'
    USER = '사용자 이름'
    PASSWORD = '패스워드'
    pass
```
