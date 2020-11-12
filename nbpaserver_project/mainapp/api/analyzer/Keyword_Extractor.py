#N=명사류. 명사류만 추출하는 코드
from .textrank import KeywordSummarizer
from PyKomoran import Komoran, DEFAULT_MODEL

komoran = Komoran(DEFAULT_MODEL['LIGHT'])
def preprocess(sents):
    komoran = Komoran(DEFAULT_MODEL['LIGHT'])
    a = (komoran.get_plain_text(sents))
    return a

def komoran_tokenize(sent):
    words = sent.split()
    words = [w for w in words if ('/N' in w )]
    return words

# 분석할 글, top-k개 만큼 키워드 추출하여 단어/형태 (중요도) 리스트 반환
def analyze_keywords(sents, top_k=50):
    
    preprocessed_sents = preprocess(sents)

    sents_arr = []
    for sent in preprocessed_sents.split('\n'):
        sents_arr.append(sent.strip())

    keyword_extractor = KeywordSummarizer(
        tokenize = komoran_tokenize,
        window = -1,
        verbose = False
    )
    
    keywords = keyword_extractor.summarize(sents_arr, topk=top_k)
    return keywords