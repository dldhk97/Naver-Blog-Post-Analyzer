import torch, numpy, random, re
from .kogpt2.pytorch_kogpt2 import get_pytorch_kogpt2_model
from gluonnlp.data import SentencepieceTokenizer
from .kogpt2.utils import get_tokenizer

from konlpy.tag import Kkma
from konlpy.utils import pprint

kkma = Kkma()

VOCAB_SIZE = 50000

ZERO_CONVERGENCE_LIMIT = 0.025
SAMPLES_NUMBER = 3

REPEATING_TOKEN_KILL_LIMIT = 2
MAX_SENTNESE_LENGTH = 100
MIN_SENTNCE_LENGTH = 20

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
    result_list = []
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

                result_list.append([word, prob])
                
                did_you_find = True
                break

        if not did_you_find:
            print('I cant find. ' + word)
            pass
        
        cnt += 1          # 다음 단어를 분석하기위해 cnt +1

        toked = splited[:cnt] # 분석할 문장에 다음 단어를 추가한다. (단지 -> 단지 이번에는)
        # print(toked)

    return result_list

# n개 랜덤 추출
def randomize_samples(lines, n):
    random_samples = random.sample(lines, n)
    return random_samples

# 문장 배열을 받아 꼬꼬마로 잘라 여러 배열로 만듬.
def split_by_kkma(sent_list, check_min_sentence_length=True):
    result_list = []

    # 분석가능한 문장이 3개도 안되면
    if len(sent_list) < 3:
        # 각 문장들을 꼬꼬마로 자른다.
        for sent in sent_list:
            spltited_sent = kkma.sentences(sent)
            # 잘린 문장들을 저장한다.
            for s in spltited_sent:
                if check_min_sentence_length:
                    if len(s) > MIN_SENTNCE_LENGTH:
                        result_list.append(s)
                else:
                    result_list.append(s)
    
    # 분석가능한 문장이 많으면?
    else:
        for sent in sent_list:
            # 최대길이보다 문장이 길면 자른다.
            if len(sent) > MAX_SENTNESE_LENGTH:
                spltited_sent = kkma.sentences(sent)
                for s in spltited_sent:
                    if check_min_sentence_length:
                        if len(s) > MIN_SENTNCE_LENGTH:
                            result_list.append(s)
                    else:
                        result_list.append(s)
            elif check_min_sentence_length: 
                if len(sent) > MIN_SENTNCE_LENGTH:
                    result_list.append(sent)
            else:
                result_list.append(sent)

    return result_list

def head_mid_tail_sampling(sent_list):
    # 3개 이하면 걍 그걸 샘플로 쓰게함.
    if len(sent_list) <= 3:
        return sent_list
    
    head_index = 0
    mid_index = int(len(sent_list) / 2)
    tail_index = len(sent_list) - 1

    # 첫, 마지막 줄로부터 몇문장 떨어질 것인가?
    edge_weight = 2

    if head_index + edge_weight < mid_index:
        head_index += edge_weight

    if tail_index - edge_weight > mid_index:
        tail_index -= edge_weight

    head = sent_list[head_index]
    mid = sent_list[mid_index]
    tail = sent_list[tail_index]
    

    return [head, mid, tail]


# !?.,를 제외한 특수문자 제거
def remove_specials(sent):
    special_removed_sent = re.compile('[\{\}\[\]\/;:|\)*~`^\-_+<>@\#$%&\\\=\(\'\"]').sub('', sent)
    return special_removed_sent

def remove_english_only(sents):
    result = []
    for sent in sents:
        if not re.compile('^[a-zA-Z0-9._# -\:]*$').match(sent):
            result.append(sent)
    return result

# 연속적으로 제로 컨버전스 이상인 녀석들을 그룹화
def group_sequential_over_convergence(tok_prob_list):
    # 확률 배열을 돌면서
    group_list = []
    need_new_group = True
    
    for i in range(len(tok_prob_list)):
        tok = tok_prob_list[i][0]
        prob = tok_prob_list[i][1]

        # 제로 컨버전스보다 크면 그룹에 넣는다.
        if prob > ZERO_CONVERGENCE_LIMIT:
            if need_new_group:
                new_group = []

                # 확률이 확 뛰는 놈 앞에있는 녀석도 그룹일 확률이 높다.
                if i > 0:
                    prev_tok = tok_prob_list[i-1][0]
                    prev_prob = tok_prob_list[i-1][1]
                    new_group.append([prev_tok, prev_prob])
                
                new_group.append([tok, prob])
                group_list.append(new_group)
                need_new_group = False
            else:
                prev_group = group_list[len(group_list) - 1]
                prev_group.append([tok, prob])

                # TEST, 반복그룹이 너무 커지면 짜른다.
                if len(prev_group) > 2:
                    need_new_group = True
        else:
            # 제로 컨버전스보다 작으면 새 그룹을 만들어야 한다. 그룹이 끊겼으니까.
            need_new_group = True
            
    return group_list

# 반복되는 문장이 있으면 잡아서 확률을 떨어뜨린다.
def repeating_sent_killer(tok_prob_list):
    # 전체 토큰을 한줄로 만든다.
    full_tok_sent = ''
    for tup in tok_prob_list:
        full_tok_sent += tup[0]

    # 연속적으로 제로 컨버전스 이상이면, 무언가 이상함. 문장이 반복되고 있는지 확인해봐야함.
    over_convergences = group_sequential_over_convergence(tok_prob_list)

    kill_target_index = []
    for group in over_convergences:
        # n 토큰 이상 연속인 녀석들만 본다.
        if len(group) >= REPEATING_TOKEN_KILL_LIMIT:
            # 그룹화된 토큰을 한줄로 만든다.
            toks = ''
            for tup in group:
                toks += tup[0]

            # 그룹화된 토큰이 전체 토큰 중 한번보다 많이 나오면(여러번 나왔다는 소리) 조정대상에 등록
            cnt = full_tok_sent.count(toks)
            if cnt > 1:
                # 전체 토큰을 돌면서, 일치하는 녀석들은 다 확률을 낮춘다.
                group_index = 0
                for i in range(len(tok_prob_list)):
                    tok = tok_prob_list[i][0]
                    group_tok = group[group_index][0]
                    
                    if tok == group_tok:
                        group_index += 1
                        if group_index >= len(group):
                            for j in range(group_index):
                                kill_target_index.append(i - j)
                            group_index = 0
                    else:
                        if group_index >= REPEATING_TOKEN_KILL_LIMIT:
                            for j in range(group_index):
                                kill_target_index.append(i - j)
                        group_index = 0

    # 조정 대상들의 확률을 조정
    for index in kill_target_index:        
        tok_prob_list[index][1] = ZERO_CONVERGENCE_LIMIT
            
    return tok_prob_list

def get_lorem_percentage(sentence, check_min_sentence_length=True):
    if len(sentence.strip()) <= 0:
        print('[SYSTEM][lorem_analyzer][get_lorem_percentage] Failed to analysis, Empty sentence!')
        return -1, None

    lorem_probs = []

    # 개행으로 최소 문자수보다 많은 줄만 추출하고, 특수문자 제거
    available_sent_list = []
    for s in sentence.split('\n'):
        sent = remove_specials(s).strip()
        if check_min_sentence_length == False:
            available_sent_list.append(sent)
        elif len(sent) >= MIN_SENTNCE_LENGTH:
            available_sent_list.append(sent)
    # 추출된 줄이 전혀 없으면 에러 반환
    if len(available_sent_list) <= 0:
        print('[SYSTEM][lorem_analyzer][get_lorem_percentage] Failed to analysis, No avaliable sents!')
        return -1, None

    # 문장이 길면 꼬꼬마로 자름.
    splited_sent_list = split_by_kkma(available_sent_list, check_min_sentence_length)
    
    # 영어만 있는 문장은 제외함.
    english_only_removed = remove_english_only(splited_sent_list)

    # 헤드 미드 테일로 3가지 샘플 추출
    samples = head_mid_tail_sampling(english_only_removed)
    samples_with_lorem = []
    
    for s in samples:
        text = s.strip()
        if len(text) <= 0:
            continue
        tok_prob_list = get_probablities(text)
        
        if len(tok_prob_list) <= 0:
            continue

        # 반복되는 문장을 잡는다.
        tok_prob_list = repeating_sent_killer(tok_prob_list)

        zero_convergence = []
        for i in range(len(tok_prob_list)):
            tok = tok_prob_list[i][0]
            prob = tok_prob_list[i][1]
            if prob <= ZERO_CONVERGENCE_LIMIT:
                zero_convergence.append([tok, prob])

        len_probs = len(tok_prob_list)
        len_zero_convergence = len(zero_convergence)
        lorem_prob = len_zero_convergence / len_probs

        # 정규화(1~0.5의 값만 대부분 나오기에, 0.5미만면 0.5으로 고정하고, (x-0.5)*2를 하여 1~0의 값을 갖게함.)
        prob = lorem_prob if lorem_prob > 0.5 else 0.5
        prob = (prob - 0.5) * 2
        lorem_probs.append(prob)
        samples_with_lorem.append('(' + str(round(prob, 3)) + ') ' + s)

    if lorem_probs and len(lorem_probs) > 0:
        lorem_percentage = numpy.mean(lorem_probs)
        return lorem_percentage, samples_with_lorem

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
