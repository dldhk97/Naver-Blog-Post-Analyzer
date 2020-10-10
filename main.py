from analyzer import analyzer
def run():
    print('Naver-Blog-Post_Analyzer server started')
    pass

def printMenu():
    print('1. 모듈 로드')
    print('2. 원본 문장 생성')
    print('3. 부자연스러움 분석')
    print('4. 종료')

def console():
    while True:
        printMenu()
        user_input = input('메뉴 선택 : ')
        if user_input == '1':
            analyzer.load_module()

        elif user_input == '2':
            user_word = input('단어 입력 : ')
            created_sent = analyzer.org_craete_sent(user_word)
            print('생성된 문장 : ')
            print(created_sent)
        
        elif user_input == '3':
            user_sent = input('문장 입력 : ')
            distances = analyzer.magic(user_sent)
            analyzer.magic_describe(user_sent, distances)

        elif user_input == '4':
            break

if __name__ == '__main__':
    print('테스트 서버 시작')
    print('모듈 자동 로드')
    analyzer.load_module()
    console()
    print('테스트 서버 종료')

if __name__ == '__main__':
    run()