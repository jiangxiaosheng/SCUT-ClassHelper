import os
import time
import hashlib
import datetime

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


if __name__ == '__main__':
    from config import *
    import datetime
    # dir = resources_base_dir + '201700'
    # file_dict = zip(os.listdir(dir), [resources_base_dir + filename for filename in os.listdir(dir)])
    # for k,v in file_dict:
    #     print(k, v)
    # print(os.path.join(dir, '123'))
    # print(file_extension('123.jpg'))
    # print(fileTime('D:\\test.txt'))
    time1 = time.localtime()
    #print(datetime.datetime.fromtimestamp(time1))
    print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    print(datetime.datetime.utcnow)
    print(type(localtime()))