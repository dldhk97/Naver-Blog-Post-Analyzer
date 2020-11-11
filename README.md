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

# 서버의 constants.py와 Admin Client의 constants.py 생성
nbpaserver_project\constants.py.bak을 참고하여 constants.py 생성
admin_client\constants.py.bak을 참고하여 constatns.py 생성

#---------------DB가 구축되지 않은 경우---------------

# DB 스키마를 생성한 후 아래 코드 실행.
# DB 테이블 구축
python .\nbpaserver_project\manage.py makemigrations
python .\nbpaserver_project\manage.py migrate

# Django 관리자 계정 생성
python .\nbpaserver_project\manage.py createsuperuser

#---------------실행---------------

# 서버 실행
python .\nbpaserver_project\manage.py runserver 8080 --noreload

# 관리자 클라이언트 실행
python .\admin_client\main.py
```
