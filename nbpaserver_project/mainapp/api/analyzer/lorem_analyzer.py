import torch
import numpy
from .kogpt2.pytorch_kogpt2 import get_pytorch_kogpt2_model
from gluonnlp.data import SentencepieceTokenizer
from .kogpt2.utils import get_tokenizer

from sklearn.preprocessing import MinMaxScaler


MAX_WORD_LEN = 100	# 2번, 문장 생성 기능시 무한루프 방지용 최대단어개수
VOCAB_SIZE = 50000

model = None
vocab = None
tok = None

def load_module():
    global model, vocab, tok

    if not model or not vocab:
        model, vocab = get_pytorch_kogpt2_model()

    if not tok:
        tok_path = get_tokenizer()
        tok = SentencepieceTokenizer(tok_path,  num_best=0, alpha=0)


def org_craete_sent(sent):
    global model, vocab, tok
    
    if model is None:
        print('[SYSTEM][Analyzer] Load module before use gpt2.')
        return None

    toked = tok(sent)
    cnt = 0
    while 1:
        input_ids = torch.tensor([vocab[vocab.bos_token],]  + vocab[toked]).unsqueeze(0)
        pred = model(input_ids)[0]
        gen = vocab.to_tokens(torch.argmax(pred, axis=-1).squeeze().tolist())[-1]
        if gen == '</s>':
            break
        elif cnt == MAX_WORD_LEN:
            print('MAX_WORD_LEN ERROR')
            break
        sent += gen.replace('▁', ' ')
        toked = tok(sent)
        cnt += 1
    return sent

# Analyze lorem and get distance(rank) vector
def get_distance(sentence):
    global model, vocab, tok

    if model is None:
        load_module()

    cnt = 1
    result_tok_list = []
    result_prob_list = []
    splited = tok(sentence)
    toked = splited[:1]   # 첫 녀석을 일단 토큰화
    print(toked)

    # 두번째 녀석부터 한번씩 word 변수에 담아 반복
    for word in splited[1:]:
        input_ids = torch.tensor([vocab[vocab.bos_token],]  + vocab[toked]).unsqueeze(0)  # 예측
        pred = model(input_ids)[0]
        
        probs = torch.nn.functional.softmax(pred, dim=-1)
        k = VOCAB_SIZE
        top_k = torch.topk(probs, k=k)

        # print(top_k)
        
        prob_arr = top_k[0]
        tok_arr = top_k[1]

        did_you_find = False
        for i in range(k):
            cur_tok_idx = tok_arr[0][cnt][i]
            
            prob = prob_arr[0][cnt][i].item()

            if cur_tok_idx == vocab[word]:
                print(word + '(' + str(format(prob, "10.6%")).strip() + ')')

                result_tok_list.append(word)
                result_prob_list.append(prob)
                
                did_you_find = True
                break

        if not did_you_find:
            print('I cant find. ' + word)
        
        cnt += 1          # 다음 단어를 분석하기위해 cnt +1

        toked = splited[:cnt] # 분석할 문장에 다음 단어를 추가한다. (단지 -> 단지 이번에는)
        # print(toked)

    return result_tok_list, result_prob_list  # 거리가 저장된 배열 반환

# 거리 배열, 평균값, 분산, 표준편차 내기
def distance_describe(distances):
    # 평균값 내보기
    mean = numpy.mean(distances)
    # 분산 내보기
    variance = numpy.var(distances)
    # 표준편차 구하기
    standard_deviation = numpy.std(distances)

    return mean, variance, standard_deviation

# 문장을 주면 토큰화한 문장의 배열 반환(외부호출용)
def tokenize(sentence):
    return tok(sentence)