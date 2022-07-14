HOST = '47.112.113.4'
PORT = '3306'
DATABASE = 'QUESTION'
USERNAME = 'samuel'
PASSWORD = 'Csk20000204sklejl'

DB_URI = "mysql+pymysql://{username}:{password}@{host}:{port}/{db}?charset=utf8".format(username=USERNAME,password=PASSWORD, host=HOST,port=PORT, db=DATABASE)

SQLALCHEMY_DATABASE_URI = DB_URI
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_ECHO = False
SQLALCHEMY_RECORD_QUERIES = False

# 问卷数据保存形式
SAVE_SQL = True
MAIL = True
LOCAL = True