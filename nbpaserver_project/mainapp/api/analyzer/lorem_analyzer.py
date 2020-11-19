import torch, numpy, random, re
from .kogpt2.pytorch_kogpt2 import get_pytorch_kogpt2_model
from gluonnlp.data import SentencepieceTokenizer
from .kogpt2.utils import get_tokenizer

from konlpy.tag import Kkma
from konlpy.utils import pprint


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
                # print(word + '(' + str(format(prob, "10.6%")).strip() + ')')

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

# n개 랜덤 추출
def randomize_samples(lines, n):
    random_samples = random.sample(lines, n)
    return random_samples

# 문장을 종결어미로 나눠서 반환
kkma = Kkma()
def split_kkma(sents):
    text_s = kkma.sentences(sents)
    return text_s

# n개로 나눠 첫문장, 중간문장, 마지막문장을 반환
def head_tail_samples(lines):
    if len(lines) >= SAMPLES_NUMBER:
        head = lines[0]
        mid = lines[int(len(lines) / 2)]
        tail = lines[len(lines) - 1]

        spltited_head = split_kkma(head)
        spltited_mid = split_kkma(mid)
        spltited_tail = split_kkma(tail)
        
        real_head = spltited_head[0]
        real_mid = spltited_mid[0]
        real_tail = spltited_tail[len(spltited_tail) - 1]

        return [real_head, real_mid, real_tail]
    else:
        # 개행이 제대로 이루어지지 않아서, 혹은 그냥 짧은 문장이면
        # 긴~ 문장인데 개행이 안된 경우 종결어미로 나눴을 때 여러 문장이 나오므로, 다시 head_tail_samples 사용.
        splited_head = split_kkma(lines[0])
        if len(splited_head) >= SAMPLES_NUMBER:
            return head_tail_samples(splited_head)

        # 마지막 문장에 대해서 다시 head_tail_samples 실행
        spltied_tail = split_kkma(lines[len(lines) - 1])
        if len(spltied_tail) >= SAMPLES_NUMBER:
            return head_tail_samples(spltied_tail)

        if splited_head[0] == spltied_tail[0]:
            return [splited_head[0]]
        
        # 답없으면 그냥 첫녀석 마지막녀석 2놈만 반환
        return [splited_head[0], spltied_tail[0]]

# !?.,를 제외한 특수문자 제거
def remove_specials(sent):
    special_removed_sent = re.compile('[\{\}\[\]\/;:|\)*~`^\-_+<>@\#$%&\\\=\(\'\"]').sub('', sent)
    return special_removed_sent

def get_lorem_percentage(sentence):
    lorem_probs = []

    # 개행으로 최소 문자수보다 많은 줄만 추출하고, 특수문자 제거
    available_lines = []
    for s in sentence.split('\n'):
        sent = remove_specials(s)
        if len(sent) >= MIN_SENTNCE_LENGTH:
            available_lines.append(sent)
    # 추출된 줄이 전혀 없으면 에러 반환
    if len(available_lines) <= 0:
        return -1

    # N개 샘플 추출
    # samples = randomize_samples(available_lines, SAMPLES_NUMBER)
    samples = head_tail_samples(available_lines)
    
    for s in samples:
        if len(s) <= 0:
            continue
        result_tok_list, result_prob_list = get_probablities(s)
        zero_convergence = []
        for i in range(len(result_tok_list)):
            tok = result_tok_list[i]
            prob = result_prob_list[i]
            if prob <= ZERO_CONVERGENCE_LIMIT:
                zero_convergence.append([tok, prob])

        len_probs = len(result_prob_list)
        len_zero_convergence = len(zero_convergence)
        lorem_prob = len_zero_convergence / len_probs

        # 정규화(1~0.5의 값만 대부분 나오기에, 0.5미만면 0.5으로 고정하고, (x-0.5)*2를 하여 1~0의 값을 갖게함.)
        prob = lorem_prob if lorem_prob > 0.5 else 0.5
        prob = (prob - 0.5) * 2
        lorem_probs.append(prob)

    if lorem_probs:
        lorem_percentage = numpy.mean(lorem_probs)
        return lorem_percentage, samples

    return -1, None

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