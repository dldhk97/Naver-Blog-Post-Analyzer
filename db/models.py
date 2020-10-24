from sqlalchemy import Column, Integer, String, DateTime, Text, Float
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class RatioType(Base):
    __tablename__ = 'ratiotype'

    type = Column(Integer, primary_key=True)
    name = Column(String(45))

    def __init__(self, type, name):

        self.type = type
        self.name = name

    def __repr__(self):
        return "<RatioType('%d', '%s')>" % (self.type, self.name)

class DictionaryType(Base):
    __tablename__ = 'dictionarytype'
 
    type = Column(Integer, primary_key=True)
    name = Column(String(45))

    def __init__(self, type, name):

        self.type = type
        self.name = name

    def __repr__(self):
        return "<DictionaryType('%d', '%s')>" % (self.type, self.name)

class FeedbackType(Base):
    __tablename__ = 'feedbacktype'
 
    type = Column(Integer, primary_key=True)
    name = Column(String(45))

    def __init__(self, type, name):

        self.type = type
        self.name = name

    def __repr__(self):
        return "<FeedbackType('%d', '%s')>" % (self.type, self.name)

class BlogInfo(Base):
    __tablename__ = 'bloginfo'
 
    blogId = Column(String(45), primary_key=True)
    logNo = Column(String(45), primary_key=True)
    url = Column(Text(4294000000))
    title = Column(Text(4294000000))
    body = Column(Text(4294000000))
    lastUpdate = Column(DateTime)

    def __init__(self, blogId, logNo, url, title, body, lastUpdate):
        self.blogId = blogId
        self.logNo = logNo
        self.url = url
        self.title = title
        self.body = body
        self.lastUpdate = lastUpdate

    def __repr__(self):
        return "<BlogInfo('%s', '%s', '%s', '%s', '%s', '%s')>" % (self.blogId, self.logNo, self.url, self.title, self.body, self.lastUpdate)

class AnalyzedInfo(Base):
    __tablename__ = 'analyzedinfo'

    analyzedInfoId = blogId = Column(Integer, primary_key=True)
    blogId = Column(String(45), primary_key=True)
    logNo = Column(String(45), primary_key=True)
    loremPercentage = Column(Float)
    tagSimilarity = Column(Float)
    lastAnalyze = Column(DateTime)

    def __init__(self, analyzedInfoId, blogId, logNo, loremPercentage, tagSimilarity, lastAnalyze):
        self.analyzedInfoId = analyzedInfoId
        self.blogId = blogId
        self.logNo = logNo
        self.loremPercentage = loremPercentage
        self.tagSimilarity = tagSimilarity
        self.lastAnalyze = lastAnalyze

    def __repr__(self):
        return "<AnalyzedInfo('%d', '%s', '%s', '%d', '%d', '%s')>" % (self.analyzedInfoId, self.blogId, self.logNo, self.loremPercentage, self.tagSimilarity, self.lastAnalyze)

class MultimediaRatio(Base):
    __tablename__ = 'multimediaRatio'

    ratioType = Column(Integer, primary_key=True)
    analyzedInfoId = blogId = Column(Integer, primary_key=True)
    blogId = Column(String(45), primary_key=True)
    logNo = Column(String(45), primary_key=True)
    ratio = Column(Float)

    def __init__(self, ratioType, analyzedInfoId, blogId, logNo, ratio):

        self.ratioType = ratioType
        self.analyzedInfoId = analyzedInfoId
        self.blogId = blogId
        self.logNo = logNo
        self.ratio = ratio

    def __repr__(self):
        return "<MultimediaRatio('%d', '%d', '%s', '%d', '%f')>" % (self.ratioType, self.analyzedInfoId, self.blogId, self.logNo, self.ratio)

class Dictionary(Base):
    __tablename__ = 'dictionary'

    dictionaryId = Column(Integer, primary_key=True)
    blogId = Column(String(45), primary_key=True)
    logNo = Column(String(45), primary_key=True)
    wordType = Column(Integer)
    word = Column(String(45))

    def __init__(self, dictionaryId, blogId, logNo, wordType, word):

        self.dictionaryId = dictionaryId
        self.blogId = blogId
        self.logNo = logNo
        self.wordType = wordType
        self.word = word

    def __repr__(self):
        return "<Dictionary('%d', '%s', '%s', '%d', '%s')>" % (self.dictionaryId, self.blogId, self.logNo, self.wordType, self.word)

class Feedback(Base):
    __tablename__ = 'feedback'

    feedbackId = Column(Integer, primary_key=True)
    blogId = Column(String(45), primary_key=True)
    logNo = Column(String(45), primary_key=True)
    ip = Column(String(45))
    feedbackType = Column(Integer)
    message = Column(Text(4294000000))
    date = Column(DateTime)

    def __init__(self, feedbackId, blogId, logNo, ip, feedbackType, message, date):

        self.feedbackId = feedbackId
        self.blogId = blogId
        self.logNo = logNo
        self.ip = ip
        self.feedbackType = feedbackType
        self.message = message
        self.date = date

    def __repr__(self):
        return "<Feedback('%d', '%s', '%s', '%s', '%d', '%s', '%s')>" % ( self.feedbackId, self.blogId, self.logNo, self.ip, self.feedbackType, self.message, self.date)


class BannedUser(Base):
    __tablename__ = 'banneduser'
    
    ip = Column(String(45), primary_key=True)
    bannedDate = Column(DateTime)
    reason = Column(Text(4294000000))

    def __init__(self, ip, bannedDate, reason):

        self.ip = ip
        self.bannedDate = bannedDate
        self.reason = reason

    def __repr__(self):
        return "<BannedUser('%s', '%s', '%s')>" % (self.ip, self.bannedDate, self.reason)