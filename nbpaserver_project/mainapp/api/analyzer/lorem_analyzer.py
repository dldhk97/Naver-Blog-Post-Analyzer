import torch, numpy, random
from .kogpt2.pytorch_kogpt2 import get_pytorch_kogpt2_model
from gluonnlp.data import SentencepieceTokenizer
from .kogpt2.utils import get_tokenizer

from sklearn.preprocessing import MinMaxScaler

VOCAB_SIZE = 50000

ZERO_CONVERGENCE_LIMIT = 0.05
MIN_SENTNCE_LENGTH = 10
SAMPLES_NUMBER = 3

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


# Analyze get probablities vector
def get_probablities(sentence):
    global model, vocab, tok

    if model is None:
        load_module()

    cnt = 1
    result_tok_list = []
    result_prob_list = []
    splited = tok(sentence)

    # 토큰이 너무 많으면 자른다...
    splited = splited[:100]

    toked = splited[:1]   # 첫 녀석을 일단 토큰화
    # print(toked)

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
            pass
        
        cnt += 1          # 다음 단어를 분석하기위해 cnt +1

        toked = splited[:cnt] # 분석할 문장에 다음 단어를 추가한다. (단지 -> 단지 이번에는)
        # print(toked)

    return result_tok_list, result_prob_list  # 거리가 저장된 배열 반환

def get_lorem_percentage(sentence):
    lorem_probs = []

    # 개행으로 최소 문자수보다 많은 줄만 추출
    available_lines = []
    for s in sentence.split('\n'):
        if len(s) >= MIN_SENTNCE_LENGTH:
            available_lines.append(s)
    # 추출된 줄이 전혀 없으면 에러 반환
    if len(available_lines) <= 0:
        return -1

    # N개 랜덤 추출
    if len(available_lines) >= SAMPLES_NUMBER:
        random_samples = random.sample(available_lines, SAMPLES_NUMBER)
    else:
        random_samples = available_lines
    
    for s in random_samples:
        if len(s) <= 0:
            continue
        print('[lorem_analyzer] get_probablities started')
        result_tok_list, result_prob_list = get_probablities(s)
        print('[lorem_analyzer] get_probablities done')
        zero_convergence = []
        for i in range(len(result_tok_list)):
            tok = result_tok_list[i]
            prob = result_prob_list[i]
            if prob <= ZERO_CONVERGENCE_LIMIT:
                zero_convergence.append([tok, prob])

        len_probs = len(result_prob_list)
        len_zero_convergence = len(zero_convergence)
        # print('총 토큰 수 : ' + str(len_probs))
        # print('총 zero_convergence 수 : ' + str(len_zero_convergence))
        lorem_prob = len_zero_convergence / len_probs
        lorem_probs.append(lorem_prob)

    if lorem_probs:
        lorem_percentage = numpy.mean(lorem_probs)
        return lorem_percentage
    return -1

# 거리 배열, 평균값, 분산, 표준편차 내기
def distance_describe(probs):
    # 평균값 내보기
    mean = numpy.mean(probs)
    # 분산 내보기
    variance = numpy.var(probs)
    # 표준편차 구하기
    standard_deviation = numpy.std(probs)

    return mean, variance, standard_deviation

# 문장을 주면 토큰화한 문장의 배열 반환(외부호출용)
def tokenize(sentence):
    return tok(sentence)