import os, sys

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db.models import RatioType, DictionaryType, FeedbackType, BlogInfo, AnalyzedInfo, MultimediaRatio, Dictionary, Feedback, BannedUser

sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from constants import DBInfo

#데이터 베이스에 접속한다.
MYSQL_ADDRESS = 'mysql://' + DBInfo.USER + ':' + DBInfo.PASSWORD + '@' + DBInfo.HOST_IP + '/' + DBInfo.DATABASE_NAME + '?charset=utf8'
engine = create_engine(MYSQL_ADDRESS, pool_size=DBInfo.POOL_SIZE, pool_recycle=DBInfo.POOL_RECYCLE, max_overflow=DBInfo.POOL_MAX_OVERFLOW, convert_unicode=False)
 
# orm과의 매핑을 명시하는 함수를 선언한다.
Base = declarative_base()

def init():
    try:
        Base.metadata.create_all(engine)
        
        # 세션을 만들어서 연결시킨다.
        session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        
        pass
    except Exception as e:
        print(e)


def test_connection():
    try:
        Base.metadata.create_all(engine)
        
        # 세션을 만들어서 연결시킨다.
        sm = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        session = sm()  # 하나의 세션 생성
        
        # 위의 클래스,인스턴스 변수를 지킨 다음에
        tada = RatioType('8','testType')
        
        # 세션에 추가를 한다.
        # session.add(tada)
        # session.commit()

        # 조회
        queries = session.query(RatioType)
        entries = [dict(type=q.type, name=q.name) for q in queries.all()]
        print(entries)

        queries = session.query(DictionaryType)
        entries = [dict(type=q.type, name=q.name) for q in queries.all()]
        print(entries)
        
        queries = session.query(FeedbackType)
        entries = [dict(type=q.type, name=q.name) for q in queries.all()]
        print(entries)

        queries = session.query(BlogInfo)
        entries = [dict(blogId=q.blogId, logNo=q.logNo, url=q.url, title=q.title, body=q.body, lastUpdate=q.lastUpdate) for q in queries.all()]
        print(entries)

        queries = session.query(AnalyzedInfo)
        entries = [dict(blogId=q.blogId, logNo=q.logNo, loremPercentage=q.loremPercentage, tagSimilarity=q.tagSimilarity, lastAnalyze=q.lastAnalyze) for q in queries.all()]
        print(entries)

        queries = session.query(MultimediaRatio)
        entries = [dict(blogId=q.blogId, logNo=q.logNo, ratioType=q.ratioType, ratio=q.ratio) for q in queries.all()]
        print(entries)

        queries = session.query(Dictionary)
        entries = [dict(blogId=q.blogId, logNo=q.logNo, wordType=q.wordType, word=q.word) for q in queries.all()]
        print(entries)

        queries = session.query(Feedback)
        entries = [dict(blogId=q.blogId, logNo=q.logNo, feedbackId=q.feedbackId, ip=q.ip, feedbackType=q.feedbackType, message=q.message, date=q.date) for q in queries.all()]
        print(entries)

        queries = session.query(BannedUser)
        entries = [dict(ip=q.ip, bannedDate=q.bannedDate, reason=q.reason) for q in queries.all()]
        print(entries)

        pass
    except Exception as e:
        print(e)


