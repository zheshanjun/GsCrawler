# coding=gbk
import os
import sys
import traceback

from selenium import common
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

import template.SysConfig as SysConfig
from template.DBClient import database_client_cursor
from template.DataModel import DataModel
from template.FirefoxSearcher import FirefoxSearcher
from template.Tables import *
from template.UnknownColumnException import UnknownColumnException
from template.UnknownTableException import UnknownTableException
from template.logger import *


class NingXiaFirefoxSearcher(FirefoxSearcher):

    def __init__(self):
        super(NingXiaFirefoxSearcher, self).__init__()
        # ���ĳ������Ϣȱ�ٱ�ע��
        chouchajiancha_template.column_list.pop()
        self.start_page_handle_bak = None
        self.detail_page_handle = None
        self.search_model = None
        self.result_model = None

    # ����ҳ��Ԫ��xpath����������
    def set_config(self):
        self.start_url = 'http://gsxt.ngsh.gov.cn/ECPS/index.jsp'
        self.code_input_box_xpath = ".//input[@id='selectValue']"
        self.code_submit_button_xpath = '/html/body/form/div[3]/div/div[2]/div/div[2]/div[2]/a'
        self.validate_image_xpath = ".//img[@id='verificationCode1']"
        self.validate_input_box_xpath = '/html/body/div[2]/div/div/ul/li[3]/div[2]/input'
        self.validate_submit_button_xpath = '/html/body/div[2]/div/div/ul/li[4]/a'
        self.tab_list_xpath = '/html/body/div[2]/div[2]/div/div[1]/ul/li'
        self.plugin_path = os.path.join(sys.path[0], r'..\ocr\ningxia.bat')
        self.province = u'���Ļ���������'

    def build_driver(self):
        build_result = 0
        profile = webdriver.FirefoxProfile(SysConfig.get_firefox_profile_path())
        self.driver = webdriver.Firefox(firefox_profile=profile)
        self.set_timeout_config()
        for i in xrange(SysConfig.max_try_times):
            if self.wait_for_load_start_url():
                break
            else:
                if i == SysConfig.max_try_times:
                    build_result = 1
        return build_result

    # ��ѯ����
    def search(self, name):
        self.cur_name = name
        self.search_model = DataModel(name, self.province)
        try:
            if not self.get_ip_status():
                # IP������update_status��4
                self.search_model.set_update_status(4)
            else:
                self.submit_search_request()
                self.get_search_result()
                if self.search_model.update_status == 1:
                    result_list = self.driver.find_elements_by_xpath("/html/body/form/div/div/dl/div")
                    for result in result_list:
                        self.driver.execute_script("arguments[0].style=''", result)
                        org_name = result.find_element_by_xpath("dt/a").text
                        self.cur_code = result.find_element_by_xpath("dd/span").text
                        # print org_name, self.cur_code
                        self.result_model = DataModel(org_name, self.province)
                        self.result_model.set_code(self.cur_code)
                        sql_1 = "select EnterpriseName from Registered_Info where RegistrationNo='%s'" % org_name
                        database_client_cursor.execute(sql_1)
                        res_1 = database_client_cursor.fetchone()
                        if res_1:
                            print u'%s�Ѹ���' % org_name
                        else:
                            self.result_model.set_update_status(1)
                            result.find_element_by_xpath("dt/a").click()
                            self.detail_page_handle = self.driver.window_handles[-1]
                            self.driver.switch_to.window(self.detail_page_handle)
                            try:
                                self.parse_detail_page()
                            except (UnknownTableException, UnknownColumnException):
                                # δ֪������������update_status��8
                                self.result_model.set_update_status(8)
                            print "*******************************************"+self.driver.current_window_handle
                            self.driver.close()

                            self.driver.switch_to.window(self.start_page_handle)
                            if self.search_model.name == self.result_model.name:
                                self.search_model.set_code(self.cur_code)
                            else:
                                sql_2 = "update GsSrc set %s where orgName='%s'" % (self.result_model, self.result_model.name)
                                database_client_cursor.execute(sql_2)
                                sql_3 = "select @@rowcount"
                                database_client_cursor.execute(sql_3)
                                res_3 = database_client_cursor.fetchone()
                                if int(res_3[0]) == 0:
                                    sql_4 = "insert into GsSrc(%s) values(%s)" % (self.result_model.get_cols(), self.result_model.get_vals())
                                    database_client_cursor.execute(sql_4)
        except Exception:
            # δ֪�쳣��update_status��3
            traceback.print_exc()
            self.search_model.set_update_status(3)
        self.switch_to_search_page()
        return self.search_model

    def switch_to_search_page(self):
        for handle in self.driver.window_handles:
            if handle != self.start_page_handle_bak:
                self.driver.switch_to.window(handle)
                self.driver.close()
        if self.start_page_handle_bak:
            self.driver.switch_to.window(self.start_page_handle_bak)
            self.start_page_handle = self.start_page_handle_bak
        else:
            self.build_driver()

    def switch_to_result_page(self):
        pass

    def get_search_result(self):
        if not self.get_ip_status():
            return 4
        search_result = self.driver.find_element_by_xpath('/html/body/form/div/div/dl')
        result_text = search_result.text.strip()
        if result_text == '':
            logging.info(u'��ѯ���0��')
            self.search_model.set_update_status(0)
        else:
            self.search_model.set_update_status(1)

    # �ύ��ѯ����
    def submit_search_request(self):
        self.start_page_handle_bak = None
        self.code_input_box = self.driver.find_element_by_xpath(self.code_input_box_xpath)
        self.code_submit_button = self.driver.find_element_by_xpath(self.code_submit_button_xpath)
        self.code_input_box.clear()  # ��������
        self.code_input_box.send_keys(self.cur_name)  # �����ѯ����
        ActionChains(self.driver).key_down(Keys.SHIFT).perform()
        self.code_submit_button.click()
        ActionChains(self.driver).key_up(Keys.SHIFT).perform()
        self.start_page_handle_bak = self.driver.window_handles[-1]
        validate_image_save_path = SysConfig.get_validate_image_save_path()  # ��ȡ��֤�뱣��·��
        for i in range(SysConfig.max_try_times):
            try:
                self.validate_image = self.driver.find_element_by_xpath(self.validate_image_xpath)  # ��λ��֤��ͼƬ
                self.download_validate_image(self.validate_image, validate_image_save_path)  # ��ͼ��ȡ��֤��
                validate_code = self.recognize_validate_code(validate_image_save_path)  # ʶ����֤��
                self.validate_input_box.clear()  # �����֤�������
                self.validate_input_box.send_keys(validate_code)  # ������֤��
                self.validate_submit_button.click()  # �����������֤�뵯����
                self.driver.switch_to.alert.accept()
                time.sleep(1)
            except common.exceptions.NoAlertPresentException:
                break
        logging.info(u"�ύ��ѯ����ɹ�")

    # �ж�IP�Ƿ񱻽�
    def get_ip_status(self):
        body_text = self.driver.find_element_by_xpath("/html/body").text
        if body_text.startswith(u'���ķ��ʹ���Ƶ��'):
            return False
        else:
            return True

    # �ж�������ʼҳ�Ƿ���سɹ� {0:�ɹ�, 1:ʧ��}
    def wait_for_load_start_url(self):
        load_result = True
        try:
            self.driver.get(self.start_url)
            self.start_page_handle = self.driver.current_window_handle
        except common.exceptions.TimeoutException:
            pass
        return load_result

    # ��������ҳ ����int�� {0����ѯ�޽����1����ѯ�н���ҽ���ɹ���4��IP������9������ʧ��}
    # def enter_detail_page(self):
    #     res = 9
    #     if not self.get_ip_status():
    #         return 4
    #     search_result = self.driver.find_element_by_xpath('/html/body/form/div/div/dl')
    #     result_text = search_result.text.strip()
    #     if result_text == '':
    #         logging.info(u'��ѯ���0��')
    #         res = 0
    #     else:
    #         info_list = result_text.split('\n')
    #         company_name = info_list[0]
    #         company_abstract = info_list[1]
    #         self.cur_code = search_result.find_element_by_xpath('div/dd/span[1]').text.strip()
    #         # print 'cur_code:' + self.cur_code
    #         # print 'company_name:'+company_name
    #         # print 'company_abstract:'+company_abstract
    #         detail_link = self.driver.find_element_by_xpath('/html/body/form/div/div/dl/div/dt/a')
    #         detail_link.click()
    #         self.detail_page_handle = self.driver.window_handles[-1]
    #         self.driver.close()
    #         res = 1
    #         self.driver.switch_to.window(self.detail_page_handle)
    #         logging.info(u"��������ҳ�ɹ�")
    #     return res

    # ���صǼ���Ϣ
    def load_dengji(self):
        table_iframe_list = self.driver.find_elements_by_xpath(".//div[@id='jibenxinxi']/iframe")
        for table_iframe in table_iframe_list:
            self.driver.switch_to.frame(table_iframe)
            table_element_list = self.driver.find_elements_by_xpath("/html/body/table")
            table_element = table_element_list[0]
            table_desc_element = table_element.find_element_by_xpath("tbody/tr/th")
            table_desc = table_desc_element.text.split('\n')[0].strip()
            if table_desc not in self.load_func_dict:
                raise UnknownTableException(self.cur_code, table_desc)
            logging.info(u"����%s ..." % table_desc)
            self.load_func_dict[table_desc](table_iframe)
            self.driver.switch_to.default_content()
            logging.info(u"����%s�ɹ�" % table_desc)

    # ���ػ�����Ϣ
    def load_jiben(self, table_iframe):
        jiben_template.delete_from_database(self.cur_code)
        table_element = self.driver.find_element_by_xpath("/html/body/table[1]")
        tr_element_list = table_element.find_elements_by_xpath('tbody/tr')
        values = {}
        for tr_element in tr_element_list[1:]:
            th_element_list = tr_element.find_elements_by_xpath('th')
            td_element_list = tr_element.find_elements_by_xpath('td')
            if len(th_element_list) == len(td_element_list):
                col_nums = len(th_element_list)
                for i in range(col_nums):
                    col = th_element_list[i].text.strip()
                    val = td_element_list[i].text.strip()
                    if col != u'':
                        values[col] = val
        values[u'ʡ��'] = self.province
        jiben_template.insert_into_database(self.cur_code, values)

    # ���عɶ���Ϣ
    def load_gudong(self, table_iframe):
        gudong_template.delete_from_database(self.cur_code)
        table_element = self.driver.find_element_by_xpath("/html/body/table[1]")
        if len(table_element.find_elements_by_xpath("tbody/tr")) > 2:
            last_index_element = self.driver.find_element_by_xpath('/html/body/table[2]/tbody/tr/th/a[last()-1]')
            index_element_list_length = int(last_index_element.text.strip())
            for i in range(index_element_list_length):
                if i > 0:
                    index_element = self.driver.find_element_by_xpath('/html/body/table[2]/tbody/tr/th/a[%d]' % (i+1))
                    index_element.click()
                    table_element = self.driver.find_element_by_xpath("/html/body/table[1]")
                tr_element_list = table_element.find_elements_by_xpath('tbody/tr')
                for tr_element in tr_element_list[2:]:
                    td_element_list = tr_element.find_elements_by_xpath('td')
                    values = []
                    for td in td_element_list:
                        val = td.text.strip()
                        if val == u'����':
                            values.append(td.find_element_by_xpath('a').get_attribute('href'))
                            td.find_element_by_xpath('a').click()
                            values.extend(self.load_gudong_detail())
                            self.driver.switch_to.frame(table_iframe)
                        else:
                            values.append(val)
                    values.extend((len(gudong_template.column_list) - len(values))*[''])
                    gudong_template.insert_into_database(self.cur_code, values)

    def load_gudong_detail(self):
        self.driver.switch_to.window(self.driver.window_handles[-1])
        td_element_list = self.driver.find_elements_by_xpath("/html/body/div[2]/div/table/tbody/tr[4]/td")
        values = []
        for td in td_element_list[1:]:
            values.append(td.text.strip())
        self.driver.close()
        self.driver.switch_to.window(self.detail_page_handle)
        return values

    # ���ر����Ϣ
    def load_biangeng(self, table_iframe):
        biangeng_template.delete_from_database(self.cur_code)
        table_element = self.driver.find_element_by_xpath("/html/body/table[1]")
        if len(table_element.find_elements_by_xpath("tbody/tr")) > 2:
            last_index_element = self.driver.find_element_by_xpath('/html/body/table[2]/tbody/tr/th/a[last()-1]')
            index_element_list_length = int(last_index_element.text.strip())
            for i in range(index_element_list_length):
                if i > 0:
                    index_element = self.driver.find_element_by_xpath('/html/body/table[2]/tbody/tr/th/a[%d]' % (i+1))
                    index_element.click()
                    table_element = self.driver.find_element_by_xpath("/html/body/table[1]")
                tr_element_list = table_element.find_elements_by_xpath('tbody/tr')
                for tr_element in tr_element_list[2:]:
                    td_element_list = tr_element.find_elements_by_xpath('td')
                    values = []
                    for td in td_element_list:
                        val = td.text.strip()
                        if val.endswith(u'����'):
                            td.find_element_by_xpath('div/a').click()
                        val = td.text.strip()
                        values.append(val[:-4].strip())
                    biangeng_template.insert_into_database(self.cur_code, values)

    # ���ر����Ϣ
    def load_beian(self):
        table_iframe_list = self.driver.find_elements_by_xpath(".//div[@id='beian']/iframe")
        for table_iframe in table_iframe_list:
            self.driver.switch_to.frame(table_iframe)
            table_element_list = self.driver.find_elements_by_xpath("/html/body/table")
            table_element = table_element_list[0]
            table_desc_element = table_element.find_element_by_xpath("tbody/tr/th")
            table_desc = table_desc_element.text.split('\n')[0].strip()
            if table_desc not in self.load_func_dict:
                raise UnknownTableException(self.cur_code, table_desc)
            logging.info(u"����%s ..." % table_desc)
            self.load_func_dict[table_desc](table_iframe)
            self.driver.switch_to.default_content()
            logging.info(u"����%s�ɹ�" % table_desc)

    # ������Ҫ��Ա��Ϣ
    def load_zhuyaorenyuan(self, table_iframe):
        zhuyaorenyuan_template.delete_from_database(self.cur_code)
        table_element = self.driver.find_element_by_xpath("/html/body/table[1]")
        if len(table_element.find_elements_by_xpath("tbody/tr")) > 2:
            last_index_element = self.driver.find_element_by_xpath('/html/body/table[2]/tbody/tr/th/a[last()-1]')
            index_element_list_length = int(last_index_element.text.strip())
            for i in range(index_element_list_length):
                if i > 0:
                    index_element = self.driver.find_element_by_xpath('/html/body/table[2]/tbody/tr/th/a[%d]' % (i+1))
                    index_element.click()
                    table_element = self.driver.find_element_by_xpath("/html/body/table[1]")
                tr_element_list = table_element.find_elements_by_xpath('tbody/tr')
                for tr_element in tr_element_list[2:]:
                    values = []
                    td_element_list = tr_element.find_elements_by_xpath('td')
                    list_length = len(td_element_list)
                    fixed_length = list_length - list_length % 3
                    for i in range(fixed_length):
                        val = td_element_list[i].text.strip()
                        values.append(val)
                        if len(values) == 3:
                            zhuyaorenyuan_template.insert_into_database(self.cur_code, values)
                            values = []

    # ���ط�֧������Ϣ
    def load_fenzhijigou(self, table_iframe):
        fenzhijigou_template.delete_from_database(self.cur_code)
        table_element = self.driver.find_element_by_xpath("/html/body/table[1]")
        if len(table_element.find_elements_by_xpath("tbody/tr")) > 2:
            last_index_element = self.driver.find_element_by_xpath('/html/body/table[2]/tbody/tr/th/a[last()-1]')
            index_element_list_length = int(last_index_element.text.strip())
            for i in range(index_element_list_length):
                if i > 0:
                    index_element = self.driver.find_element_by_xpath('/html/body/table[2]/tbody/tr/th/a[%d]' % (i+1))
                    index_element.click()
                    table_element = self.driver.find_element_by_xpath("/html/body/table[1]")
                tr_element_list = table_element.find_elements_by_xpath('tbody/tr')
                for tr_element in tr_element_list[2:]:
                    td_element_list = tr_element.find_elements_by_xpath('td')
                    values = []
                    for td in td_element_list:
                        val = td.text.strip()
                        values.append(val)
                    fenzhijigou_template.insert_into_database(self.cur_code, values)

    # ����������Ϣ
    def load_qingsuan(self, table_iframe):
        table_element = self.driver.find_element_by_xpath("/html/body/table[1]")
        val_1 = table_element.find_element_by_xpath('tbody/tr[2]/td').text.strip()
        val_2 = table_element.find_element_by_xpath('tbody/tr[3]/td').text.strip()
        values = [val_1, val_2]
        if len(values[0]) != 0 or len(values[1]) != 0:
            qingsuan_template.delete_from_database(self.cur_code)
            qingsuan_template.insert_into_database(self.cur_code, values)

    # ���ض�����Ѻ��Ϣ
    def load_dongchandiyadengji(self):
        dongchandiyadengji_template.delete_from_database(self.cur_code)
        table_iframe = self.driver.find_element_by_xpath(".//div[@id='dcdy']/iframe")
        self.driver.switch_to.frame(table_iframe)
        table_element_list = self.driver.find_elements_by_xpath("/html/body/table")
        table_element = table_element_list[0]
        row_cnt = len(table_element.find_elements_by_xpath("tbody/tr"))
        if row_cnt > 2:
            last_index_element = self.driver.find_element_by_xpath('/html/body/table[2]/tbody/tr/th/a[last()-1]')
            index_element_list_length = int(last_index_element.text.strip())
            for i in range(index_element_list_length):
                if i > 0:
                    index_element = self.driver.find_element_by_xpath('/html/body/table[2]/tbody/tr/th/a[%d]' % (i+1))
                    index_element.click()
                    table_element = self.driver.find_element_by_xpath("/html/body/table[1]")
                tr_element_list = table_element.find_elements_by_xpath('tbody/tr')
                for tr_element in tr_element_list[2:]:
                    td_element_list = tr_element.find_elements_by_xpath('td')
                    values = []
                    for td in td_element_list:
                        val = td.text.strip()
                        if val == u'����':
                            values.append(td.find_element_by_xpath('a').get_attribute('href'))
                        else:
                            values.append(val)
                    dongchandiyadengji_template.insert_into_database(self.cur_code, values)
        self.driver.switch_to.default_content()

    # ���ع�Ȩ���ʵǼ���Ϣ
    def load_guquanchuzhidengji(self):
        guquanchuzhidengji_template.delete_from_database(self.cur_code)
        table_iframe = self.driver.find_element_by_xpath(".//div[@id='guquanchuzhi']/iframe")
        self.driver.switch_to.frame(table_iframe)
        table_element_list = self.driver.find_elements_by_xpath("/html/body/table")
        table_element = table_element_list[0]
        row_cnt = len(table_element.find_elements_by_xpath("tbody/tr"))
        if row_cnt > 2:
            last_index_element = self.driver.find_element_by_xpath('/html/body/table[2]/tbody/tr/th/a[last()-1]')
            index_element_list_length = int(last_index_element.text.strip())
            for i in range(index_element_list_length):
                if i > 0:
                    index_element = self.driver.find_element_by_xpath('/html/body/table[2]/tbody/tr/th/a[%d]' % (i+1))
                    index_element.click()
                    table_element = self.driver.find_element_by_xpath("/html/body/table[1]")
                tr_element_list = table_element.find_elements_by_xpath('tbody/tr')
                for tr_element in tr_element_list[2:]:
                    td_element_list = tr_element.find_elements_by_xpath('td')
                    values = []
                    for td in td_element_list:
                        val = td.text.strip()
                        values.append(val)
                    guquanchuzhidengji_template.insert_into_database(self.cur_code, values)
        self.driver.switch_to.default_content()

    # ��������������Ϣ
    def load_xingzhengchufa(self):
        xingzhengchufa_template.delete_from_database(self.cur_code)
        table_iframe = self.driver.find_element_by_xpath(".//div[@id='xingzhengchufa']/iframe")
        self.driver.switch_to.frame(table_iframe)
        table_element_list = self.driver.find_elements_by_xpath("/html/body/table")
        table_element = table_element_list[0]
        row_cnt = len(table_element.find_elements_by_xpath("tbody/tr"))
        if row_cnt > 2:
            last_index_element = self.driver.find_element_by_xpath('/html/body/table[2]/tbody/tr/th/a[last()-1]')
            index_element_list_length = int(last_index_element.text.strip())
            for i in range(index_element_list_length):
                if i > 0:
                    index_element = self.driver.find_element_by_xpath('/html/body/table[2]/tbody/tr/th/a[%d]' % (i+1))
                    index_element.click()
                    table_element = self.driver.find_element_by_xpath("/html/body/table[1]")
                tr_element_list = table_element.find_elements_by_xpath('tbody/tr')
                for tr_element in tr_element_list[2:]:
                    td_element_list = tr_element.find_elements_by_xpath('td')
                    values = []
                    for td in td_element_list:
                        val = td.text.strip()
                        values.append(val)
                    xingzhengchufa_template.insert_into_database(self.cur_code, values)
        self.driver.switch_to.default_content()

    # ���ؾ�Ӫ�쳣��Ϣ
    def load_jingyingyichang(self):
        jingyingyichang_template.delete_from_database(self.cur_code)
        table_iframe = self.driver.find_element_by_xpath(".//div[@id='jyyc']/iframe")
        self.driver.switch_to.frame(table_iframe)
        table_element_list = self.driver.find_elements_by_xpath("/html/body/table")
        table_element = table_element_list[0]
        row_cnt = len(table_element.find_elements_by_xpath("tbody/tr"))
        if row_cnt > 2:
            last_index_element = self.driver.find_element_by_xpath('/html/body/table[2]/tbody/tr/th/a[last()-1]')
            index_element_list_length = int(last_index_element.text.strip())
            for i in range(index_element_list_length):
                if i > 0:
                    index_element = self.driver.find_element_by_xpath('/html/body/table[2]/tbody/tr/th/a[%d]' % (i+1))
                    index_element.click()
                    table_element = self.driver.find_element_by_xpath("/html/body/table[1]")
                tr_element_list = table_element.find_elements_by_xpath('tbody/tr')
                for tr_element in tr_element_list[2:]:
                    td_element_list = tr_element.find_elements_by_xpath('td')
                    values = []
                    for td in td_element_list:
                        val = td.text.strip()
                        values.append(val)
                    jingyingyichang_template.insert_into_database(self.cur_code, values)
        self.driver.switch_to.default_content()

    # ����ԭ��Υ����Ϣ
    def load_yanzhongweifa(self):
        yanzhongweifa_template.delete_from_database(self.cur_code)
        table_iframe = self.driver.find_element_by_xpath(".//div[@id='yzwf']/iframe")
        self.driver.switch_to.frame(table_iframe)
        table_element_list = self.driver.find_elements_by_xpath("/html/body/table")
        table_element = table_element_list[0]
        row_cnt = len(table_element.find_elements_by_xpath("tbody/tr"))
        if row_cnt > 2:
            last_index_element = self.driver.find_element_by_xpath('/html/body/table[2]/tbody/tr/th/a[last()-1]')
            index_element_list_length = int(last_index_element.text.strip())
            for i in range(index_element_list_length):
                if i > 0:
                    index_element = self.driver.find_element_by_xpath('/html/body/table[2]/tbody/tr/th/a[%d]' % (i+1))
                    index_element.click()
                    table_element = self.driver.find_element_by_xpath("/html/body/table[1]")
                tr_element_list = table_element.find_elements_by_xpath('tbody/tr')
                for tr_element in tr_element_list[2:]:
                    td_element_list = tr_element.find_elements_by_xpath('td')
                    values = []
                    for td in td_element_list:
                        val = td.text.strip()
                        values.append(val)
                    yanzhongweifa_template.insert_into_database(self.cur_code, values)
        self.driver.switch_to.default_content()

    # ���س������Ϣ
    def load_chouchajiancha(self):
        chouchajiancha_template.delete_from_database(self.cur_code)
        table_iframe = self.driver.find_element_by_xpath(".//div[@id='ccjc']/iframe")
        self.driver.switch_to.frame(table_iframe)
        table_element_list = self.driver.find_elements_by_xpath("/html/body/table")
        table_element = table_element_list[0]
        row_cnt = len(table_element.find_elements_by_xpath("tbody/tr"))
        if row_cnt > 2:
            last_index_element = self.driver.find_element_by_xpath('/html/body/table[2]/tbody/tr/th/a[last()-1]')
            index_element_list_length = int(last_index_element.text.strip())
            for i in range(index_element_list_length):
                if i > 0:
                    index_element = self.driver.find_element_by_xpath('/html/body/table[2]/tbody/tr/th/a[%d]' % (i+1))
                    index_element.click()
                    table_element = self.driver.find_element_by_xpath("/html/body/table[1]")
                tr_element_list = table_element.find_elements_by_xpath('tbody/tr')
                for tr_element in tr_element_list[2:]:
                    td_element_list = tr_element.find_elements_by_xpath('td')
                    values = []
                    for td in td_element_list:
                        val = td.text.strip()
                        values.append(val)
                    chouchajiancha_template.insert_into_database(self.cur_code, values)
        self.driver.switch_to.default_content()

if __name__ == '__main__':

    code_list = ['640103200001999', '640100200099662', '640000100002816', '91640000715044058N',  '640221200010727',  '640103200001999', '640181200008860']
    searcher = NingXiaFirefoxSearcher()
    searcher.set_config()
    if searcher.build_driver() == 0:
        searcher.search(u"�������������۹�����޹�˾")
