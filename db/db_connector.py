import os, sys
import mysql

# 상위폴더의 모듈 임포트
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
import constants

conn = None

def test_connection():
    try:
        conn = mysql.connector.connect(host=constants.DB.HOST_IP, port=constants.DB.PORT, database=constants.DB.DATABASE_NAME, user=constants.DB.USER, password=constants.DB.PASSWORD)

        mysql_cursor = conn.cursor(dictionary=True)

        query_executor(mysql_cursor, 'image', 'unknown')

        for row in mysql_cursor:
            print('aaa is : ' + str(row['type']))

        mysql_cursor.close()

        pass
    except Exception as e:
        print(e)


def query_executor(cursor, param1, param2):
    sql = 'select * from nbpadb.ratiotype where `name` = %s or `name` = %s ;'
    
    cursor.execute(sql, (param1, param2))

    pass


