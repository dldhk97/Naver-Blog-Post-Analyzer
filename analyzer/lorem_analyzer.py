import torch
import numpy
from kogpt2.pytorch_kogpt2 import get_pytorch_kogpt2_model
from gluonnlp.data import SentencepieceTokenizer
from kogpt2.utils import get_tokenizer

MAX_WORD_LEN = 100	# 2번, 문장 생성 기능시 무한루프 방지용 최대단어개수

model = None
vocab = None
tok = None

def load_module():
    global model, vocab, tok
    tok_path = get_tokenizer()
    model, vocab = get_pytorch_kogpt2_model()
    tok = SentencepieceTokenizer(tok_path,  num_best=0, alpha=0)
    print('KoGPT2 모듈 로드됨')


def org_craete_sent(sent):
    global model, vocab, tok
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

# MAGIC! (NEW)
def get_distance(sentence):
    global model, vocab, tok
    cnt = 1
    distance_list = []
    splited = tok(sentence)
    toked = splited[:1]   # 첫 녀석을 일단 토큰화
    # print(toked)

    # 두번째 녀석부터 한번씩 word 변수에 담아 반복
    for word in splited[1:]:
        input_ids = torch.tensor([vocab[vocab.bos_token],]  + vocab[toked]).unsqueeze(0)  # 예측
        pred = model(input_ids)[0]

        # 연관성이 높은 순으로 vocab을 뒤지는데, 다음 녀석이 존재하는지 찾는다.
        distance = 0
        # print(torch.argsort(pred, axis=-1, descending=True)[0])
        for vocab_idx in torch.argsort(pred, axis=-1, descending=True)[0][cnt]:
            # 연관성 순 인덱스와, 다음 단어의 인덱스가 같다면, 거리(1위로 부터의 거리)를 구하고 반복 종료
            if vocab_idx == vocab[word]:
                # print(word + ' of distance : ' + str(distance))
                # print(vocab_idx)
                distance_list.append(distance)
                break
            distance += 1   # 두 인덱스가 다르면 거리 +1
        cnt += 1          # 다음 단어를 분석하기위해 cnt +1

        toked = splited[:cnt] # 분석할 문장에 다음 단어를 추가한다. (단지 -> 단지 이번에는)
        # print(toked)

    return distance_list  # 거리가 저장된 배열 반환

# 거리 배열, 평균값, 분산, 표준편차 자동으로 내기
def distance_describe(distances):
    print('')
    print('거리 배열 : ' + str(distances))
    # 평균값 내보기
    print('평균값 : ' + str(numpy.mean(distances)))
    # 분산 내보기
    print('분산 : ' + str(numpy.var(distances)))
    # 표준편차 구하기
    print('표준편차 : ' + str(numpy.std(distances)))
    print('')