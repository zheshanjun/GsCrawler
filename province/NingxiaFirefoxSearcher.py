# coding=gbk
from template.FirefoxSearcher import FirefoxSearcher
from selenium import common
import template.SysConfig as SysConfig
import sys
import os
from template.UnknownTableException import UnknownTableException
from template.UnknownColumnException import UnknownColumnException
from template.Tables import *
from template.DataModel import DataModel
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from template.logger import *
import traceback


class NingXiaFirefoxSearcher(FirefoxSearcher):

    def __init__(self):
        super(NingXiaFirefoxSearcher, self).__init__()
        # 宁夏抽查检查信息缺少备注列
        chouchajiancha_template.column_list.pop()
        self.start_page_handle_bak = None
        self.detail_page_handle = None

    # 配置页面元素xpath与浏览器插件
    def set_config(self):
        self.start_url = 'http://gsxt.ngsh.gov.cn/ECPS/index.jsp'
        self.code_input_box_xpath = ".//input[@id='selectValue']"
        self.code_submit_button_xpath = '/html/body/form/div[3]/div/div[2]/div/div[2]/div[2]/a'
        self.validate_image_xpath = ".//img[@id='verificationCode1']"
        self.validate_input_box_xpath = '/html/body/div[2]/div/div/ul/li[3]/div[2]/input'
        self.validate_submit_button_xpath = '/html/body/div[2]/div/div/ul/li[4]/a'
        self.tab_list_xpath = '/html/body/div[2]/div[2]/div/div[1]/ul/li'
        self.plugin_path = os.path.join(sys.path[0], r'..\ocr\ningxia.bat')

    # 查询代码
    def search(self, code):
        data_model = DataModel(code)
        self.cur_code = code
        try:
            if not self.get_ip_status():
                # IP被禁，update_status：4
                data_model.set_update_status(4)
            else:
                self.submit_search_request()
                enter_detail_page_result = self.enter_detail_page()
                if enter_detail_page_result == 0:
                    # 查询无结果，update_status：0
                    data_model.set_update_status(0)
                elif enter_detail_page_result == 1:
                    # 查询成功，update_status：1
                    data_model.set_update_status(1)
                    self.parse_detail_page()
                else:
                    # 查询失败，update_status：3
                    data_model.set_update_status(3)
        except (UnknownTableException, UnknownColumnException):
            # 未知表名或列名，update_status：8
            data_model.set_update_status(8)
        except Exception:
            # 未知异常，update_status：3
            traceback.print_exc()
            data_model.set_update_status(3)

        for handle in self.driver.window_handles:
            if handle != self.start_page_handle_bak:
                self.driver.switch_to.window(handle)
                self.driver.close()
        if self.start_page_handle_bak:
            self.driver.switch_to.window(self.start_page_handle_bak)
        else:
            self.build_driver()
        return data_model

    # 提交查询请求
    def submit_search_request(self):
        self.start_page_handle_bak = None
        self.code_input_box = self.driver.find_element_by_xpath(self.code_input_box_xpath)
        self.code_submit_button = self.driver.find_element_by_xpath(self.code_submit_button_xpath)
        self.code_input_box.clear()  # 清空输入框
        self.code_input_box.send_keys(self.cur_code)  # 输入查询代码
        ActionChains(self.driver).key_down(Keys.SHIFT).perform()
        self.code_submit_button.click()
        ActionChains(self.driver).key_up(Keys.SHIFT).perform()
        self.start_page_handle_bak = self.driver.window_handles[-1]
        self.validate_image = self.driver.find_element_by_xpath(self.validate_image_xpath)  # 定位验证码图片
        self.validate_input_box = self.driver.find_element_by_xpath(self.validate_input_box_xpath)  # 定位验证码输入框
        self.validate_submit_button = self.driver.find_element_by_xpath(self.validate_submit_button_xpath)  # 定位验证码提交按钮
        validate_image_save_path = SysConfig.get_validate_image_save_path(self.cur_code)  # 获取验证码保存路径
        for i in range(SysConfig.max_try_times):
            try:
                self.validate_image = self.driver.find_element_by_xpath(self.validate_image_xpath)  # 定位验证码图片
                self.download_validate_image(self.validate_image, validate_image_save_path)  # 截图获取验证码
                validate_code = self.recognize_validate_code(validate_image_save_path)  # 识别验证码
                self.validate_input_box.clear()  # 清空验证码输入框
                self.validate_input_box.send_keys(validate_code)  # 输入验证码
                self.validate_submit_button.click()  # 点击搜索（验证码弹窗）
                self.driver.switch_to_alert().accept()
                time.sleep(1)
            except common.exceptions.NoAlertPresentException:
                break
        logging.info(u"提交查询请求成功")

    # 判断IP是否被禁
    def get_ip_status(self):
        body_text = self.driver.find_element_by_xpath("/html/body").text
        if body_text.startswith(u'您的访问过于频繁'):
            return False
        else:
            return True

    # 判断搜索起始页是否加载成功 {0:成功, 1:失败}
    def wait_for_load_start_url(self):
        load_result = True
        try:
            self.driver.get(self.start_url)
            self.start_page_handle = self.driver.current_window_handle
        except common.exceptions.TimeoutException:
            pass
        return load_result

    # 进入详情页 返回int型 {0：查询无结果，1：查询有结果且进入成功，4：IP被禁，9：进入失败}
    def enter_detail_page(self):
        res = 9
        if not self.get_ip_status():
            return 4
        search_result = self.driver.find_element_by_xpath('/html/body/form/div/div/dl')
        result_text = search_result.text.strip()
        if result_text == '':
            logging.info(u'查询结果0条')
            res = 0
        else:
            info_list = result_text.split('\n')
            company_name = info_list[0]
            company_abstract = info_list[1]
            self.cur_code = search_result.find_element_by_xpath('div/dd/span[1]').text.strip()
            print 'cur_code:' + self.cur_code
            print 'company_name:'+company_name
            print 'company_abstract:'+company_abstract
            detail_link = self.driver.find_element_by_xpath('/html/body/form/div/div/dl/div/dt/a')
            detail_link.click()
            self.detail_page_handle = self.driver.window_handles[-1]
            self.driver.close()
            res = 1
            self.driver.switch_to.window(self.detail_page_handle)
            logging.info(u"进入详情页成功")
        return res

    # def parse_detail_page(self):
    #     self.tab_list = self.driver.find_elements_by_xpath(self.tab_list_xpath)
    #     i = 0
    #     for tab in self.tab_list:
    #         i += 1
    #         if i <= 2:
    #             time.sleep(2)
    #         else:
    #             time.sleep(1)
    #         tab_text = tab.text
    #         logging.info(u"解析%s ..." % tab_text)
    #         if tab.get_attribute('class') != 'current':
    #             tab.click()
    #         self.load_func_dict[tab_text]()
    #         logging.info(u"解析%s成功" % tab_text)

    # 加载登记信息
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
            logging.info(u"解析%s ..." % table_desc)
            self.load_func_dict[table_desc](table_iframe)
            self.driver.switch_to.default_content()
            logging.info(u"解析%s成功" % table_desc)

    # 加载基本信息
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
        jiben_template.insert_into_database(self.cur_code, values)

    # 加载股东信息
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
                        if val == u'详情':
                            values.append(td.find_element_by_xpath('a').get_attribute('href'))
                            td.find_element_by_xpath('a').click()
                            values.extend(self.load_gudong_detail())
                            self.driver.switch_to.frame(table_iframe)
                        else:
                            values.append(val)
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

    # 加载变更信息
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
                        if val.endswith(u'更多'):
                            td.find_element_by_xpath('div/a').click()
                        val = td.text.strip()
                        values.append(val[:-4].strip())
                    biangeng_template.insert_into_database(self.cur_code, values)

    # 加载变更信息
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
            logging.info(u"解析%s ..." % table_desc)
            self.load_func_dict[table_desc](table_iframe)
            self.driver.switch_to.default_content()
            logging.info(u"解析%s成功" % table_desc)

    # 加载主要人员信息
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

    # 加载分支机构信息
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

    # 加载清算信息
    def load_qingsuan(self, table_iframe):
        qingsuan_template.delete_from_database(self.cur_code)
        table_element = self.driver.find_element_by_xpath("/html/body/table[1]")
        val_1 = table_element.find_element_by_xpath('tbody/tr[2]/td').text.strip()
        val_2 = table_element.find_element_by_xpath('tbody/tr[3]/td').text.strip()
        values = [val_1, val_2]
        qingsuan_template.insert_into_database(self.cur_code, values)

    # 加载动产抵押信息
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
                        if val == u'详情':
                            values.append(td.find_element_by_xpath('a').get_attribute('href'))
                        else:
                            values.append(val)
                    dongchandiyadengji_template.insert_into_database(self.cur_code, values)
        self.driver.switch_to.default_content()

    # 加载股权出质登记信息
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

    # 加载行政处罚信息
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

    # 加载经营异常信息
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

    # 加载原种违法信息
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

    # 加载抽查检查信息
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
        for code1 in code_list:
            searcher.search(code1)
