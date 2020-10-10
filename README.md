# Naver Blog Post Analyzer
네이버 블로그 게시글 분석기(Naver Blog Post Analyzer)

## 설치방법(Windows)
```
# 필수 pip 패키지 설치
python -m pip install -r .\requirements.txt

# torch 설치
python -m pip install torch==1.5.1+cu101 torchvision==0.6.1+cu101 -f https://download.pytorch.org/whl/torch_stable.html

# KoGPT2 설치
python -m pip install .\KoGPT2\

# crawler 디렉토리 내 constants.py 생성 (constants.py.bak을 constants.py로 바꾸거나 복사)
cp constants.py.bak constants.py

# constants.py 수정 (NaverAPI)
class NaverAPI(object):
    NAVER_CLIENT_ID = '자신의 네이버 API ID'
    NAVER_CLIENT_SECRET = '자신의 네이버 API SECRET'
```
