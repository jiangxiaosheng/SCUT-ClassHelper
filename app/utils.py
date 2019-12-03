import os
import time
import hashlib
import datetime
import pymysql

from . import message_db
from config import *


#判断path下是否存在指定文件file，目前不支持递归判断
def file_exists(file, dir):
    if file in os.listdir(dir):
        return True
    else:
        return False

#递归删除文件夹
def remove_dir(dir):
    dir = dir.replace('\\', '/')
    if os.path.isdir(dir):
        for p in os.listdir(dir):
            remove_dir(os.path.join(dir, p))
        if (os.path.exists(dir)):
            os.rmdir(dir)
    else:
        if os.path.exists(dir):
            os.remove(dir)


#获取文件后缀名
def file_extension(file):
  return os.path.splitext(file)[1]


#获取文件时间属性
def fileTime(file):
    return (
        time.ctime(os.path.getatime(file)), #访问时间
        time.ctime(os.path.getmtime(file)), #创建时间
        time.ctime(os.path.getctime(file)) #修改时间
    )


#md5散列
def md5(data):
    data = data.encode('utf-8')
    return hashlib.md5(data).hexdigest()


#获取本地时间，格式如下
def localtime():
    time_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    return datetime.datetime.strptime(time_str,"%Y-%m-%d %H:%M:%S")


#在mysql数据库中创建一个课程聊天室的聊天记录表
#course_id：课程id
def create_message_table(course_id):
    table_name = 'course' + str(course_id) + '_message'
    cursor = message_db.cursor()

    sql = """CREATE TABLE IF NOT EXISTS %s (
            id INT PRIMARY KEY AUTO_INCREMENT,
             user_id  VARCHAR(10) NOT NULL,
             body TEXT,
             type ENUM("text", "image") DEFAULT "text",
             url VARCHAR(25),
             timestamp DATETIME)""" % table_name

    cursor.execute(sql)

#删除某个课程的mysql表
def drop_messsage_table(course_id):
    table_name = 'course' + str(course_id) + '_message'
    cursor = message_db.cursor()

    sql = """DROP TABLE %s""" % table_name

    cursor.execute(sql)


#添加数据库记录
#message为json格式，有content和user_id字段
#TODO:目前还不支持发送图片
def insert_message(course_id, message):
    table_name = 'course' + str(course_id) + '_message'
    cursor = message_db.cursor()

    sql = """INSERT INTO %s(user_id, body, timestamp)
        VALUES
        (%s, '%s', '%s')""" % (table_name, message['user_id'], message['content'], localtime())

    try:
        cursor.execute(sql)
        message_db.commit()
    except:
        message_db.rollback()


def get_chat_history(course_id, count=100):
    #message_db = pymysql.connect("localhost", DevelopmentConfig.MYSQL_USERNAME, DevelopmentConfig.MYSQL_PASSWORD,'SCUT_ClassHelper')
    table_name = 'course' + str(course_id) + '_message'
    cursor = message_db.cursor()

    sql = """SELECT user_id,body,timestamp
    from %s
    order by `timestamp` desc""" % str(table_name)

    cursor.execute(sql)
    result = cursor.fetchall()
    if len(result) < count:
        return result
    else:
        return result[: count]


if __name__ == '__main__':
    #create_message_table(2)
    get_chat_history(1)
