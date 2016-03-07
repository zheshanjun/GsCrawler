# coding=gbk
import time
from DBClient import *
import SysConfig
from logger import *
import sys
import os


class UpdateJob(object):

    process_name = None
    pid = None
    process_identity = None
    host = None
    searcher = None
    province = None
    batch_size = 10
    host_type = 'PC'

    def __init__(self):
        pass

    def set_config(self):
        pass

    def build_searcher(self):
        self.searcher.set_config()
        if self.searcher.build_driver() != 0:
            logging.info(u"��ѯ������ʧ��!")
            logging.shutdown()
            sys.exit()

    def register_process(self):
        for arg in sys.argv:
            if arg.startswith('host='):
                self.host = arg.split('=')[1].strip()
        if not self.host:
            self.host = os.getenv('computername')
        SysConfig.province = self.province
        self.pid = os.getpid()
        cur_time = time.strftime('%Y-%m-%d %X', time.localtime())

        sql1 = "insert into ProcessStatus (processID,processName,processStatus,startTime,lastUpdateTime,totalUpdateCnt,host) " \
               "values('%s','%s',0,'%s',getDate(),0,'%s')" % (self.pid, self.process_name, cur_time, self.host);
        database_client_cursor.execute(sql1)
        sql2 = 'select SCOPE_IDENTITY()'
        database_client_cursor.execute(sql2)
        self.process_identity = int(database_client_cursor.fetchone()[0])
        database_client_connection.commit()
        file_name = SysConfig.get_log_path(self.process_identity)
        set_logger_name(file_name)
        logging.info(u"��������:%s" % self.process_name)
        logging.info(u"pid:%s" % self.pid)
        logging.info(u"process_identity:%s" % self.process_identity)
        logging.info(u"������/IP:%s" % self.host)

    def update_code(self, code):
        logging.info(u"���´���:%s" % code)
        update_result = 1
        for i in range(SysConfig.max_try_times):
            data_model = self.searcher.search(code)
            if data_model.update_status in (0, 1, 4, 8):
                break
        if data_model.update_status in (0, 1, 8):
            data_model.update_to_db()
            update_result = 0
        elif data_model.update_status == 4:
            update_result = 4
        logging.info(u"����״̬:%d" % data_model.update_status)
        return update_result

    def update_proc(self):
        process_status = 0
        while True:
            failed_process_identity = -1
            row_count = 0

            sql_0 = "select top 1 processIdentity from ProcessStatus(tablockx) " \
                    "where processStatus!=0 " \
                    "and processStatus!=9 " \
                    "and processName='%s'" % self.process_name
            database_client_cursor.execute(sql_0)
            res_0 = database_client_cursor.fetchone()
            if res_0:
                failed_process_identity = int(res_0[0])
                sql_1 = "update ProcessStatus set processStatus=9 where processIdentity=%d" % failed_process_identity
                database_client_cursor.execute(sql_1)
            database_client_connection.commit()

            if failed_process_identity != -1:
                logging.info(u'�ӹܽ���;%d' % failed_process_identity)
                sql_2 = "update GsSrc set lastUpdateTime=GETDATE(), processIdentity=%d " \
                        "where processIdentity=%d " \
                        "and updateStatus=-2" % (self.process_identity, failed_process_identity)
                database_client_cursor.execute(sql_2)
                sql_3 = "select @@rowcount"
                database_client_cursor.execute(sql_3)
                res_3 = database_client_cursor.fetchone()
                row_count = int(res_3[0])
            if row_count == 0:
                sql_4 = "update top(%d) GsSrc " \
                        "set updateStatus=-2, processIdentity=%d, lastUpdateTime=GETDATE() " \
                        "where province='%s' " \
                        "and updateStatus=-1" % (self.batch_size, self.process_identity, self.province)
                database_client_cursor.execute(sql_4)
                sql_5 = "select @@rowcount"
                database_client_cursor.execute(sql_5)
                res_5 = database_client_cursor.fetchone()
                row_count = int(res_5[0])
            database_client_connection.commit()
            logging.info(u'��������Ŀ;%d' % row_count)
            if row_count > 0:
                sql_6 = "select registeredCode from GsSrc where processIdentity=%d and updateStatus=-2 order by reverse(registeredCode)" % self.process_identity
                database_client_cursor.execute(sql_6)
                res_6 = database_client_cursor.fetchall()
                batch_list = [row[0] for row in res_6]
                for code in batch_list:
                    process_status = self.update_code(code)
                    sql_7 = "update ProcessStatus set processStatus=%d, lastUpdateTime=GETDATE() where processIdentity=%d" % (process_status, self.process_identity)
                    database_client_cursor.execute(sql_7)
                    database_client_connection.commit()
                    if process_status != 0:
                        break
                if process_status != 0:
                    break
            else:
                break
        if process_status == 0:
            logging.info(u'����������!')
        else:
            logging.info(u'�������ʧ��!')

    def run(self):
        self.set_config()
        self.register_process()
        self.build_searcher()
        self.update_proc()

if __name__ == '__main__':
    job = UpdateJob()
    print time.strftime('%Y-%m-%d %X', time.localtime())
    job.register_process()
