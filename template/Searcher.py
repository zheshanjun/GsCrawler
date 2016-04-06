# coding=gbk

import os
import subprocess
import sys

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait

import SysConfig
from logger import *


class Searcher(object):

    driver = None
    start_url = None
    exist_iframe = False
    code_input_box = None
    code_input_box_xpath = None
    code_submit_button = None
    code_submit_button_xpath = None
    validate_image = None
    validate_image_xpath = None
    validate_input_box = None
    validate_input_box_xpath = None
    validate_submit_button = None
    validate_submit_button_xpath = None
    tab_list = None
    tab_list_xpath = None
    plugin_path = None
    cur_name = None
    cur_code = None
    start_page_handle = None
    load_func_dict = {}
    table_dict = {}
    table_config_file = os.path.join(sys.path[0], '../conf/GsTables.xml')
    province = None

    def __init__(self):
        self.load_func_dict[u'�Ǽ���Ϣ'] = self.load_dengji
        self.load_func_dict[u'������Ϣ'] = self.load_beian
        self.load_func_dict[u'������Ѻ�Ǽ���Ϣ'] = self.load_dongchandiyadengji
        self.load_func_dict[u'������Ѻ��Ϣ'] = self.load_dongchandiyadengji
        self.load_func_dict[u'��Ȩ���ʵǼ���Ϣ'] = self.load_guquanchuzhidengji
        self.load_func_dict[u'����������Ϣ'] = self.load_xingzhengchufa
        self.load_func_dict[u'��Ӫ�쳣��Ϣ'] = self.load_jingyingyichang
        self.load_func_dict[u'����Υ����Ϣ'] = self.load_yanzhongweifa
        self.load_func_dict[u'�������Ϣ'] = self.load_chouchajiancha
        self.load_func_dict[u'������Ϣ'] = self.load_jiben
        self.load_func_dict[u'�ɶ���Ϣ'] = self.load_gudong
        self.load_func_dict[u'�����Ϣ'] = self.load_biangeng
        self.load_func_dict[u'��Ҫ��Ա��Ϣ'] = self.load_zhuyaorenyuan
        self.load_func_dict[u'��֧������Ϣ'] = self.load_fenzhijigou
        self.load_func_dict[u'������Ϣ'] = self.load_qingsuan
        self.load_func_dict[u'�μӾ�Ӫ�ļ�ͥ��Ա����'] = self.load_jiatingchengyuan     # Modified by Jing

    # ��ʼ�������
    def build_driver(self):
        """

        :rtype: int
        """
        pass

    def set_config(self):
        """
        ���ò�ѯ����������Ϣ��������Ҫ��xpath����֤��ʶ����
        """
        pass

    # �ȴ���ҳ�������
    def wait_for_load_start_url(self):
        """

        :rtype: int
        """
        pass

    # ���빤��ע���룬���ز�ѯ״̬��������ֱ����ݲ����ڴ˷��������
    def search(self, name):
        self.cur_name = name
        self.submit_search_request()
        self.enter_detail_page()
        self.parse_detail_page()
        self.driver.close()
        self.driver.switch_to.window(self.start_page_handle)

    # ʶ����֤��
    def recognize_validate_code(self, validate_path):
        cmd = self.plugin_path + " " + validate_path
        print cmd
        process = subprocess.Popen(cmd.encode('GBK', 'ignore'), stdout=subprocess.PIPE)
        process_out = process.stdout.read()
        answer = process_out.split('\r\n')[6].strip()
        print 'answer: '+answer
        os.remove(validate_path)
        return answer

    def submit_search_request(self):
        self.code_input_box.clear()  # ��������
        self.code_input_box.send_keys(self.cur_name)  # �����ѯ����
        self.code_submit_button.click()  # ���������ť
        self.validate_image = self.driver.find_element_by_xpath(self.validate_image_xpath)  # ��λ��֤��ͼƬ
        self.validate_input_box = self.driver.find_element_by_xpath(self.validate_input_box_xpath)  # ��λ��֤�������
        self.validate_submit_button = self.driver.find_element_by_xpath(self.validate_submit_button_xpath)  # ��λ��֤���ύ��ť
        validate_image_save_path = SysConfig.get_validate_image_save_path()  # ��ȡ��֤�뱣��·��
        self.download_validate_image(self.validate_image, validate_image_save_path)  # ��ͼ��ȡ��֤��
        validate_code = self.recognize_validate_code(validate_image_save_path)  # ʶ����֤��
        self.validate_input_box.clear()  # �����֤�������
        self.validate_input_box.send_keys(validate_code)  # ������֤��
        self.validate_submit_button.click()  # �����������֤�뵯����

    def enter_detail_page(self):
        pass

    def get_driver_pid(self):
        return None

    def parse_detail_page(self):
        self.tab_list = self.driver.find_elements_by_xpath(self.tab_list_xpath)
        for tab in self.tab_list:
            tab_text = tab.text
            logging.info(u"����%s ..." % tab_text)
            if tab.get_attribute('class') != 'current':
                tab.click()
            self.load_func_dict[tab_text]()
            logging.info(u"����%s�ɹ�" % tab_text)

    # ������֤�뵽����
    def download_validate_image(self):
        pass

    # ����ҳ��������ʱ�䣬���������ʱ�䣬ҳ����Ȼδ������ɣ�����ʱ����
    def set_timeout_config(self):
        # pass
        self.driver.set_page_load_timeout(SysConfig.page_load_timeout)
        self.driver.implicitly_wait(SysConfig.implicitly_wait_timeout)

    def wait_for_element(self, xpath, seconds):
        return WebDriverWait(self.driver, seconds).\
            until(expected_conditions.presence_of_element_located((By.XPATH, xpath)))

    # ���صǼ���Ϣ
    def load_dengji(self):
        pass

    # ���ر�����Ϣ
    def load_beian(self):
        pass

    # ���ض�����Ѻ�Ǽ���Ϣ
    def load_dongchandiyadengji(self):
        pass

    # ���ع�Ȩ���ʵǼ���Ϣ
    def load_guquanchuzhidengji(self):
        pass

    # ��������������Ϣ
    def load_xingzhengchufa(self):
        pass

    # ���ؾ�Ӫ�쳣��Ϣ
    def load_jingyingyichang(self):
        pass

    # ��������Υ����Ϣ
    def load_yanzhongweifa(self):
        pass

    # ���س������Ϣ
    def load_chouchajiancha(self):
        pass

    # ���ػ�����Ϣ
    def load_jiben(self, table_element):
        pass

    # ���عɶ���Ϣ
    def load_gudong(self, table_element):
        pass

    # ���ر����Ϣ
    def load_biangeng(self, table_element):
        pass

    # ������Ҫ��Ա��Ϣ
    def load_zhuyaorenyuan(self, table_element):
        pass

    # ���زμӾ�Ӫ�ļ�ͥ��Ա����
    def load_jiatingchengyuan(self, table_element):      # Modified by Jing
        pass
    
    # ���ط�֧������Ϣ
    def load_fenzhijigou(self, table_element):
        pass

    # ����������Ϣ
    def load_qingsuan(self):
        pass

if __name__ == '__main__':
    s = Searcher()
    s.load_table_config()
