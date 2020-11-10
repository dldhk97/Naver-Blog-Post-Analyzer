import torch
import numpy
from .kogpt2.pytorch_kogpt2 import get_pytorch_kogpt2_model
from gluonnlp.data import SentencepieceTokenizer
from .kogpt2.utils import get_tokenizer

from sklearn.preprocessing import MinMaxScaler


MAX_WORD_LEN = 100	# 2번, 문장 생성 기능시 무한루프 방지용 최대단어개수

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
        print('[SYSTEM][Analyzer] Load module before use gpt2.')
        return None

    cnt = 1
    distance_list = []
    splited = tok(sentence)
    toked = splited[:1]   # 첫 녀석을 일단 토큰화
    print(toked)

    # 두번째 녀석부터 한번씩 word 변수에 담아 반복
    for word in splited[1:]:
        input_ids = torch.tensor([vocab[vocab.bos_token],]  + vocab[toked]).unsqueeze(0)  # 예측
        pred = model(input_ids)[0]
        
        probs = torch.nn.functional.softmax(pred, dim=-1)
        k = 50000
        top_k = torch.topk(probs, k=k)

        # print(top_k)
        
        prob_arr = top_k[0]
        tok_arr = top_k[1]

        did_you_find = False
        for i in range(k):
            cur_tok_idx = tok_arr[0][cnt][i]
            
            prob_1 = prob_arr[0][cnt][i].item()

            if cur_tok_idx == vocab[word]:
                print(word)
                print(format(prob_1, "10.6%"))
                did_you_find = True
                break

        if not did_you_find:
            print('I cant find. ' + word)


        # # 연관성이 높은 순으로 vocab을 뒤지는데, 다음 녀석이 존재하는지 찾는다.
        # distance = 0
        # ye1 = vocab.idx_to_token[3918]
        # yey = vocab.idx_to_token[104]
        # # print(torch.argsort(pred, axis=-1, descending=True)[0])
        
        # for vocab_idx in torch.argsort(pred, axis=-1, descending=True)[0][cnt]:
        #     # 연관성 순 인덱스와, 다음 단어의 인덱스가 같다면, 거리(1위로 부터의 거리)를 구하고 반복 종료
        #     print(vocab_idx)
        #     if vocab_idx == vocab[word]:
        #         # print(word + ' of distance : ' + str(distance))
                
        #         distance_list.append(distance)
        #         break
        #     distance += 1   # 두 인덱스가 다르면 거리 +1
        
        cnt += 1          # 다음 단어를 분석하기위해 cnt +1

        toked = splited[:cnt] # 분석할 문장에 다음 단어를 추가한다. (단지 -> 단지 이번에는)
        # print(toked)

    return distance_list  # 거리가 저장된 배열 반환

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