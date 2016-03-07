# coding=gbk
import logging
import time


def set_logger_name(file_name):
    print u'��־����:%s' % file_name
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                        datefmt='%Y-%m-%d %X',
                        filename=file_name,
                        filemode='w')

if __name__ == '__main__':
    set_logger_name(r'C:\Users\kai.li\PycharmProjects\GsCrawler\logs\2016-02-23\test1.txt')


