import os, csv
from datetime import datetime

CSV_ENCODING_TYPE = 'utf-8'

# 경로를 주면 폴더를 생성하는 메소드
def create_directory(path):
    try:
        if not(os.path.isdir(path)):
            os.makedirs(os.path.join(path))
    except OSError as e:
        if e.errno != errno.EEXIST:
            print("Failed to create directory!!!!!")
            raise

# 파일명과 BlogPost 배열을 주면 csv파일로 저장하는 메소드
def save_as_csv(feedback_list, save_directory):
    now = datetime.today().strftime("%Y%m%d%H%M%S")
    
    if save_directory:
        save_path = save_directory
    else:
        save_path = os.getcwd() + os.sep + 'feedbacks' + os.sep
    
    create_directory(save_path)
    file_name = 'Feedback - ' + now  + '.csv'

    try:
        f = open(save_path + file_name, 'w', newline='', encoding=CSV_ENCODING_TYPE)
        wr = csv.writer(f)

        ## 여기서부터 feedback 저장하게 바꿔라 TODO!!!
        wr.writerow(['pk', 'blog_info', 'ip', 'feedback_type', 'message', 'created_at'])
        for feedback in feedback_list:
            try:
                if feedback:
                    pk = feedback['pk']
                    feedback_fields = feedback['fields']
                    blog_info = feedback_fields['blog_info']
                    ip = feedback_fields['ip']
                    feedback_type = feedback_fields['feedback_type']
                    message = feedback_fields['message']
                    created_at = feedback_fields['created_at']
                    
                    wr.writerow([pk, blog_info, ip, feedback_type, message, created_at])
                    
                    print(str(pk) + ' 저장 완료')
            except Exception as ex:
                print(ex)
        print('모든 피드백을 저장하였습니다! (경로 : ' + save_path + file_name + ')')
        f.close
    except Exception as e:
        print("Failed to save csv file : ", e)

    return