import torch, numpy, random, re
from .kogpt2.pytorch_kogpt2 import get_pytorch_kogpt2_model
from gluonnlp.data import SentencepieceTokenizer
from .kogpt2.utils import get_tokenizer

from konlpy.tag import Kkma
from konlpy.utils import pprint


VOCAB_SIZE = 50000

ZERO_CONVERGENCE_LIMIT = 0.025
MIN_SENTNCE_LENGTH = 20
SAMPLES_NUMBER = 3

REPEATING_TOKEN_KILL_LIMIT = 2

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

# 문장을 종결어미로 나눠서 반환
kkma = Kkma()
LONG_SENTNESE_CUTLINE = 100

# 커트라인보다 긴 문장은 꼬꼬마로 자르고, 작으면 아무것도 하지않음.
def sent_cutting(sent):
    if len(sent) > LONG_SENTNESE_CUTLINE:
        spltited_sent = kkma.sentences(sent)

        samples = []
        for s in spltited_sent:
            if len(s) >= MIN_SENTNCE_LENGTH:
                samples.append(s)

        if len(samples) > 0:
            return samples
    return None

# n개로 나눠 첫문장, 중간문장, 마지막문장을 반환
def head_tail_samples(lines):
    if len(lines) >= SAMPLES_NUMBER:
        splited_head = sent_cutting(lines[0])
        splited_mid = sent_cutting(lines[int(len(lines) / 2)])
        splited_tail = sent_cutting(lines[len(lines) - 1])

        head = splited_head[0] if splited_head else lines[0]
        mid = splited_mid[0] if splited_mid else lines[int(len(lines) / 2)]
        tail = splited_tail[0] if splited_tail else lines[len(lines) - 1]

        return [head, mid, tail]

    elif len(lines) == 2:
        # 개행이 제대로 이루어지지 않아서, 혹은 그냥 짧은 문장이면
        splited_head = sent_cutting(lines[0])
        splited_tail = sent_cutting(lines[1])

        head = splited_head[0] if splited_head else lines[0]
        tail = splited_tail[0] if splited_tail else lines[1]

        if splited_head and len(splited_head) >= 2:
            splited_mid = head_tail_samples(splited_head)
            for mid in splited_mid:
                if mid != head:
                    return [head, mid, tail]
        if splited_tail and len(splited_tail) >= 2:
            splited_mid = head_tail_samples(splited_tail)
            for mid in splited_mid:
                if mid != tail:
                    return [head, mid, tail]
        
        return [head, tail]

    else:
        splited = sent_cutting(lines[0])

        if splited:
            if len(splited) >= 2:
                return head_tail_samples(splited)
        
        return [lines[0], ]

# !?.,를 제외한 특수문자 제거
def remove_specials(sent):
    special_removed_sent = re.compile('[\{\}\[\]\/;:|\)*~`^\-_+<>@\#$%&\\\=\(\'\"]').sub('', sent)
    return special_removed_sent

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
        # 4 토큰 이상 연속인 녀석들만 본다.
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
    available_lines = []
    for s in sentence.split('\n'):
        sent = remove_specials(s).strip()
        if check_min_sentence_length == False:
            available_lines.append(sent)
        elif len(sent) >= MIN_SENTNCE_LENGTH:
            available_lines.append(sent)
    # 추출된 줄이 전혀 없으면 에러 반환
    if len(available_lines) <= 0:
        print('[SYSTEM][lorem_analyzer][get_lorem_percentage] Failed to analysis, No avaliable sents!')
        return -1, None

    # N개 샘플 추출
    samples = head_tail_samples(available_lines)
    samples_with_lorem = []
    
    for s in samples:
        text = s.strip()
        if len(text) <= 0:
            continue
        tok_prob_list = get_probablities(text)

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

    if lorem_probs:
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
