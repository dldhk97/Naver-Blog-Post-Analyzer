# simple_cli를 사용하여 서버와 통신하는 프로그램
# 관리자용 메소드를 사용할 수도 있고, 확장프로그램이 만들어지지 않았기에 디버깅용으로 사용.
# AJAX Request를 통해 서버와 통신함.

import simple_cli

if __name__ == '__main__':
    print('Naver Blog Post Analyzer : Admin Client')

    exit_code = -1
    
    # 관리자 인증
    if simple_cli.admin_authorization():
    
        exit_code = simple_cli.main_loop(simple_cli.MENU_DICTS)
    else:
        print('관리자 인증에 실패하였습니다.')
        exit_code = 0;

    if exit_code == 0:
        print('정상적으로 종료합니다.')
    else:
        print('비정상적인 종료입니다.')