# coding=gbk
from template.FirefoxSearcher import FirefoxSearcher
from selenium import common
import template.SysConfig as SysConfig
import sys
import os
from template.UnknownColumnException import UnknownColumnException as unknown_column
from template.UnknownTableException import UnknownTableException as unknown_table
from selenium.common.exceptions import NoSuchElementException
from template.Tables import *
import time
from selenium import webdriver
from template.DataModel import DataModel
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from template.logger import *
from template.DBClient import *
from template.logger import *
import traceback


class SichuanFirefoxSearcher(FirefoxSearcher):

    def __init__(self):
        super(SichuanFirefoxSearcher, self).__init__()
        # �Ĵ��������Ϣû�б�ע��
        chouchajiancha_template.column_list.pop()
        gudong_template.column_list.remove('Shareholder_Details')
        self.detail_page_handle=None
        
    def search(self, code): 
        
        data_model = DataModel(code)
        self.cur_code = code
        try:
            if not self.get_ip_status():
                # IP������update_status��4
                data_model.set_update_status(4)
            else:
                self.submit_search_request()
                enter_detail_page_result = self.enter_detail_page()
                print enter_detail_page_result
                
                if enter_detail_page_result == 0:
                    # ��ѯ�޽����update_status��0
                    data_model.set_update_status(0)
                    print data_model.set_update_status
                    
                elif enter_detail_page_result == 1:
                    # ��ѯ�ɹ���update_status��1
                    data_model.set_update_status(1)
                    delete_from_db(self.cur_code)
                    self.parse_detail_page()
                else:
                    # ��ѯʧ�ܣ�update_status��3
                    data_model.set_update_status(3)
                self.driver.close()
                self.driver.switch_to.window(self.start_page_handle)
        except:
            # δ֪�쳣��update_status��3
            traceback.print_exc()
            data_model.set_update_status(3)
            self.driver.close()
            self.driver.switch_to.window(self.start_page_handle)
        return data_model

            
    def submit_search_request(self):
        self.code_input_box = self.driver.find_element_by_xpath(self.code_input_box_xpath)
        self.code_submit_button = self.driver.find_element_by_xpath(self.code_submit_button_xpath)
        self.code_input_box.clear()  # ��������
        self.code_input_box.send_keys(self.cur_code)  # �����ѯ����
        self.code_submit_button.click()
        validate_image_save_path = SysConfig.get_validate_image_save_path(self.cur_code)  # ��ȡ��֤�뱣��·��
        for i in range(SysConfig.max_try_times):
            self.validate_image = self.driver.find_element_by_xpath(self.validate_image_xpath)  # ��λ��֤��ͼƬ
            self.validate_input_box = self.driver.find_element_by_xpath(self.validate_input_box_xpath)  # ��λ��֤�������
            self.validate_submit_button = self.driver.find_element_by_xpath(self.validate_submit_button_xpath)  # ��λ��֤���ύ��ť
            self.download_validate_image(self.validate_image, validate_image_save_path)  # ��ͼ��ȡ��֤��
            validate_code = self.recognize_validate_code(validate_image_save_path)  # ʶ����֤��
#             if i < 3:
#                 validate_code = '1233'
            self.validate_input_box.clear()  # �����֤�������
            self.validate_input_box.send_keys(validate_code)  # ������֤��
            self.validate_submit_button.click()  # �����������֤�뵯����
            try:
                self.wait_for_element("/html/body/div[1]/div/table/tbody/tr[2]/td[2]/div/table/tbody/tr[3]/td/div/input", 1).click()
            except common.exceptions.TimeoutException:
                break

    # �ж�IP�Ƿ񱻽�
    def get_ip_status(self):
        body_text = self.driver.find_element_by_xpath("/html/body").text
        if body_text.startswith(u'���ķ��ʹ���Ƶ��'):
            return False
        else:
            return True

    def set_config(self):
        self.start_url = 'http://gsxt.scaic.gov.cn'
        self.code_input_box_xpath = '//*[@id="entname"]'
        self.code_submit_button_xpath = "//*[@onclick='zdm()']/img"
        self.validate_image_xpath = "//*[@id='img']"
        self.validate_input_box_xpath = "//*[@id='yzm']"
        self.validate_submit_button_xpath = "//*[@id='woaicss_con1']/ul/li[4]/a"
        self.tab_list_xpath = '/html/body/div[2]/div[2]/div/div[1]/ul/li'
        self.plugin_path = os.path.join(sys.path[0], r'..\ocr\sichuan\sichuan.bat')

    # �ж�������ʼҳ�Ƿ���سɹ� {0:�ɹ�, 1:ʧ��}
    def wait_for_load_start_url(self):
        load_result = True
        try:
            self.driver.get(self.start_url)
            self.start_page_handle = self.driver.current_window_handle
        except common.exceptions.TimeoutException:
            pass
        try:
            self.code_input_box = self.driver.find_element_by_xpath(self.code_input_box_xpath)
            self.code_submit_button = self.driver.find_element_by_xpath(self.code_submit_button_xpath)
        except common.exceptions.NoSuchElementException:
            load_result = False
        return load_result

    # ��������ҳ ����int�� {0����ѯ�޽����1����ѯ�н��������ɹ���9������ʧ��}
    def enter_detail_page(self):
        res = 9
        if not self.get_ip_status():
            return 4
        search_result = self.driver.find_element_by_xpath('/html/body/form/div[5]/div[position()>1][position()<11]')
        result_text = search_result.text.encode('gbk').strip()
        logging.info(result_text)
        print result_text
        if result_text == '�������������޲�ѯ�����':
            logging.info(u'��ѯ���0��')
            res = 0
        else:
            info_list = result_text.split('\n')
            company_name = info_list[0]
            company_abstract = info_list[1]
            print 'company_name:'+company_name
            print 'company_abstract:'+company_abstract
            detail_link = self.driver.find_element_by_xpath('/html/body/form/div[5]/div[2]/ul/li[1]/a')
            detail_link.click()
            for handle in self.driver.window_handles:
                if handle == self.driver.current_window_handle:
                    continue
                else:
                    self.driver.switch_to.window(handle)
                    self.detail_page_handle=handle
                    res = 1
                    logging.info(u"��������ҳ�ɹ�")
        print res
        return res

    
    def parse_detail_page(self):
        tab_list_length = len(self.driver.find_elements_by_xpath(self.tab_list_xpath))
        for i in range(tab_list_length):
            tab = self.driver.find_element_by_xpath("/html/body/div[2]/div[2]/div/div[1]/ul/li[%d]" % (i+1))
            tab_text = tab.text
            if tab.get_attribute('class') != 'current':
                tab.click()
            self.load_func_dict[tab_text]()

    
    def load_dengji(self):
        table_list = self.driver.find_elements_by_xpath("/html/body/div[2]/div[2]/div/div[2]//table[@class='detailsList']")
        for table_element in table_list:
            row_cnt = len(table_element.find_elements_by_xpath("tbody/tr"))
            table_desc_element = table_element.find_element_by_xpath("tbody/tr/th")
            table_desc = table_desc_element.text.split('\n')[0].strip()
            print row_cnt
            print table_desc
            if table_desc == u'������Ϣ':
                self.load_func_dict[table_desc](table_element)
            elif table_desc in self.load_func_dict:
                if row_cnt > 2:
                        self.load_func_dict[table_desc](table_element)
            else:
                raise unknown_table(table_desc)
            self.driver.switch_to.default_content()

    def load_jiben(self,table_element):
        tr_element_list = self.driver.find_elements_by_xpath("//*[@id='jibenxinxi']/table[1]/tbody/tr")
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
#         for k in values:
#             print k+"->"+values[k]
        jiben_template.insert_into_database(self.cur_code, values)

    def load_gudong(self,table_element):
        tr_element_list = self.driver.find_elements_by_xpath("//*[@id='table_fr']/tbody/tr[position()<last()]")
        style = 'block'
        for tr_element in tr_element_list[2:]:
            if "display: none" in tr_element.get_attribute("style"):
                self.driver.execute_script("arguments[0].style='%s'" % style, tr_element)
            else:
                style = tr_element.get_attribute("style")            
            td_element_list = tr_element.find_elements_by_xpath('td')
            values = []
            for td in td_element_list:
                val = td.text.strip()
                if val == u'����':
                    td.find_element_by_xpath('a').click()
                    for handle in self.driver.window_handles:
                        if handle != self.start_page_handle and handle!=self.detail_page_handle:
                            self.driver.switch_to.window(handle)
                    tr_detail_list = self.driver.find_elements_by_xpath("//*[@id='sifapanding']/table/tbody/tr")
                    for tr_ele in tr_detail_list[3:]:
                        td_ele_list = tr_ele.find_elements_by_xpath('td')                             
                        for td in td_ele_list[1:]:
                            va = td.text.strip()
                            print va
                            values.append(va)                                     
                    self.driver.close()
                    self.driver.switch_to.window(self.detail_page_handle) 
                else:
                    values.append(val)
                    #values.extend(['','','','','','',''])                                                                 
            gudong_template.insert_into_database(self.cur_code, values)
            
 
    def load_biangeng(self, table_element):
        tr_element_list = self.driver.find_elements_by_xpath("//*[@id='table_bg']/tbody/tr[position()<last()]")
        style = 'block'
        for tr_element in tr_element_list[2:]:           
            if "display: none" in tr_element.get_attribute("style"):
                self.driver.execute_script("arguments[0].style='%s'" % style, tr_element)
            else:
                style = tr_element.get_attribute("style")           
            td_element_list = tr_element.find_elements_by_xpath('td')
            values = []
            for td in td_element_list:
                val = td.text.strip()
                if val.endswith(u'����'):
                    td.find_element_by_xpath('span/a').click()
                    val = td.text.strip()
                    values.append(val[:-4].strip())
                else:
                    values.append(val.strip())
            biangeng_template.insert_into_database(self.cur_code, values)

    def load_beian(self):
        table_list = self.driver.find_elements_by_xpath("/html/body/div[2]/div[2]/div/div[3]//table[@class='detailsList']")
        for table_element in table_list:
            row_cnt = len(table_element.find_elements_by_xpath("tbody/tr"))
            table_desc_element = table_element.find_element_by_xpath("tbody/tr/th")
            table_desc = table_desc_element.text.split('\n')[0].strip()
            print row_cnt
            print table_desc
            if table_desc == u'������Ϣ':
                self.load_func_dict[table_desc](table_element)
            elif table_desc in self.load_func_dict:
                if row_cnt > 2:
                        self.load_func_dict[table_desc](table_element)
            else:
                raise unknown_table(table_desc)
            self.driver.switch_to.default_content()

    def load_zhuyaorenyuan(self, table_element):
        table_element = self.driver.find_element_by_xpath("//*[@id='table_ry1']/tbody/tr[position()<last()]")
        tr_element_list = table_element.find_elements_by_xpath("//*[@id='table_ry1']/tbody/tr[position()<last()]")
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
                    
    def load_jiatingchengyuan(self, table_element):
        table_element = self.driver.find_element_by_xpath("//*[@id='table_ry1']/tbody/tr[position()<last()]")
        tr_element_list = table_element.find_elements_by_xpath("//*[@id='table_ry1']/tbody/tr[position()<last()]")
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
 
    def load_fenzhijigou(self, table_element):
        table_element = self.driver.find_element_by_xpath("//*[@id='table_fr2']/tbody/tr[position()<last()]")
        tr_element_list = table_element.find_elements_by_xpath("//*[@id='table_fr2']/tbody/tr[position()<last()]")
        for tr_element in tr_element_list[2:]:
            td_element_list = tr_element.find_elements_by_xpath('td')
            values = []
            for td in td_element_list:
                val = td.text.strip()
                values.append(val)
            fenzhijigou_template.insert_into_database(self.cur_code, values)
 
    def load_qingsuan(self, table_element):
        pass


    def load_dongchandiyadengji(self):       
        table_element_list = self.driver.find_elements_by_xpath("/html/body/div[2]/div[2]/div/div[6]/table[@class='detailsList']")
        table_element = table_element_list[0]
        row_cnt = len(table_element.find_elements_by_xpath("tbody/tr"))
        if row_cnt > 2:
            tr_element_list = self.driver.find_elements_by_xpath("//*[@id='table_dc']/tbody/tr[position()<last()]")
            style = 'block'
            for tr_element in tr_element_list[2:]:
                if "display: none" in tr_element.get_attribute("style"):
                    self.driver.execute_script("arguments[0].style='%s'" % style, tr_element)
                else:
                    style = tr_element.get_attribute("style")           
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


    def load_guquanchuzhidengji(self):
        table_element_list = self.driver.find_elements_by_xpath("/html/body/div[2]/div[2]/div/div[5]/table[@class='detailsList']")
        table_element = table_element_list[0]
        row_cnt = len(table_element.find_elements_by_xpath("tbody/tr"))
        if row_cnt > 2:
            tr_element_list = self.driver.find_elements_by_xpath("//*[@id='table_gq']/tbody/tr[position()<last()]")
            style = 'block'
            for tr_element in tr_element_list[2:]:
                if "display: none" in tr_element.get_attribute("style"):
                    self.driver.execute_script("arguments[0].style='%s'" % style, tr_element)
                else:
                    style = tr_element.get_attribute("style")           
                td_element_list = tr_element.find_elements_by_xpath('td')
                values = []
                for td in td_element_list:
                    val = td.text.strip()
                    values.append(val)
                guquanchuzhidengji_template.insert_into_database(self.cur_code, values)
        self.driver.switch_to.default_content()
        
        
    def load_xingzhengchufa(self):
        table_element_list = self.driver.find_elements_by_xpath("/html/body/div[2]/div[2]/div/div[4]/table[@class='detailsList']")
        table_element = table_element_list[0]
        row_cnt = len(table_element.find_elements_by_xpath("tbody/tr"))
        if row_cnt > 2:
            tr_element_list = self.driver.find_elements_by_xpath("//*[@id='table_gscfxx']/tbody/tr[position()<last()]")
            style = 'block'
            for tr_element in tr_element_list[2:]:
                if "display: none" in tr_element.get_attribute("style"):
                    self.driver.execute_script("arguments[0].style='%s'" % style, tr_element)
                else:
                    style = tr_element.get_attribute("style")           
                td_element_list = tr_element.find_elements_by_xpath('td')
                values = []
                for td in td_element_list:
                    val = td.text.strip()
                    values.append(val)
                xingzhengchufa_template.insert_into_database(self.cur_code, values)
        self.driver.switch_to.default_content()
 
    def load_jingyingyichang(self):
        table_element_list = self.driver.find_elements_by_xpath("/html/body/div[2]/div[2]/div/div[7]/table[@class='detailsList']")
        table_element = table_element_list[0]
        row_cnt = len(table_element.find_elements_by_xpath("tbody/tr"))
        if row_cnt > 2:
            tr_element_list = self.driver.find_elements_by_xpath("//*[@id='table_yc']/tbody/tr[position()<last()]")
            style = 'block'
            for tr_element in tr_element_list[2:]:
                if "display: none" in tr_element.get_attribute("style"):
                    self.driver.execute_script("arguments[0].style='%s'" % style, tr_element)
                else:
                    style = tr_element.get_attribute("style")           
                td_element_list = tr_element.find_elements_by_xpath('td')
                values = []
                for td in td_element_list:
                    val = td.text.strip()
                    values.append(val)
                jingyingyichang_template.insert_into_database(self.cur_code, values)
        self.driver.switch_to.default_content()


    def load_yanzhongweifa(self):
        table_element_list = self.driver.find_elements_by_xpath("/html/body/div[2]/div[2]/div/div[8]/table[@class='detailsList']")
        table_element = table_element_list[0]
        row_cnt = len(table_element.find_elements_by_xpath("tbody/tr"))
        if row_cnt > 2:
            tr_element_list = self.driver.find_elements_by_xpath("//*[@id='table_wfxx']/tbody/tr[position()<last()]")
            style = 'block'
            for tr_element in tr_element_list[2:]:
                if "display: none" in tr_element.get_attribute("style"):
                    self.driver.execute_script("arguments[0].style='%s'" % style, tr_element)
                else:
                    style = tr_element.get_attribute("style")           
                td_element_list = tr_element.find_elements_by_xpath('td')
                values = []
                for td in td_element_list:
                    val = td.text.strip()
                    values.append(val)
                yanzhongweifa_template.insert_into_database(self.cur_code, values)
        self.driver.switch_to.default_content()
 
    def load_chouchajiancha(self):
        table_element_list = self.driver.find_elements_by_xpath("/html/body/div[2]/div[2]/div/div[9]/table[@class='detailsList']")
        table_element = table_element_list[0]
        row_cnt = len(table_element.find_elements_by_xpath("tbody/tr"))
        if row_cnt > 2:
            tr_element_list = self.driver.find_elements_by_xpath("//*[@id='table_ccjc']/tbody/tr[position()<last()]")
            style = 'block'
            for tr_element in tr_element_list[2:]:
                if "display: none" in tr_element.get_attribute("style"):
                    self.driver.execute_script("arguments[0].style='%s'" % style, tr_element)
                else:
                    style = tr_element.get_attribute("style")           
                td_element_list = tr_element.find_elements_by_xpath('td')
                values = []
                for td in td_element_list:
                    val = td.text.strip()
                    values.append(val)
                    print val
                chouchajiancha_template.insert_into_database(self.cur_code, values)
        self.driver.switch_to.default_content()

if __name__ == '__main__':

    code_list = ['510000000276185','510125000075372','510125000075410']
    searcher = SichuanFirefoxSearcher()
    searcher.set_config()
    if searcher.build_driver() == 0:
        for code1 in code_list:
            if searcher.wait_for_load_start_url():
                print time.strftime('%Y-%m-%d %X', time.localtime())
                data_model=searcher.search(code1)
                print data_model.update_status
                time.sleep(30)
                print time.strftime('%Y-%m-%d %X', time.localtime())
                database_client_connection.commit()
            #break
