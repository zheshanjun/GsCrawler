# coding=gbk

import sys
import os
import datetime

page_load_timeout = 15
web_element_wait_timeout = 15
implicitly_wait_timeout = 15
max_try_times = 5
province = None


# ��ȡ��֤����ʱ����·��
def get_validate_image_save_path():
    return os.path.join(sys.path[0], '..\\data\\' + str(os.getpid()) + ".png")


# ��ȡ��������Profile�ļ�
def get_firefox_profile_path():
    return os.path.join(sys.path[0], "..\\conf\\FirefoxProfile")


# ��ȡ��־�ļ�·��
def get_log_path(process_identity):
    today = str(datetime.date.today())
    save_dir = os.path.join(sys.path[0], '..\\logs\\'+today);
    if not os.path.exists(save_dir):
        os.mkdir(save_dir)
    return os.path.join(sys.path[0], save_dir+'\\log_'+str(process_identity)+".txt")


if __name__ == '__main__':
    print get_validate_image_save_path()
    print get_log_path()
