# coding=gbk
from DBClient import *


class DataModel(object):
    # self.code������ע����
    # self.name����˾����
    # self.update_status����ѯ״̬ {-1:δ����, 0:���벻����, 1:�������, 8:��ҳģ���쳣}

    def __init__(self, name, province):
        self.name = name
        self.province = province
        self.update_status = -1
        self.code = None
        self.cols = 'orgName,registeredCode,lastUpdateTime,province,updateStatus'

    def set_code(self, code):
        self.code = code

    def set_update_status(self, status):
        self.update_status = status

    def __str__(self):
        return "orgName='%s',registeredCode='%s',lastUpdateTime=getDate(),province='%s',updateStatus=%d" % \
               (self.name, self.code, self.province, self.update_status)

    def get_cols(self):
        return self.cols

    def get_vals(self):
        return "'%s','%s',getDate(),'%s',%d" % (self.name, self.code, self.province, self.update_status)

    def update_to_db(self):
        update_sql = "update GsSrc set %s where orgName = '%s'"\
                     % (self.__str__(), self.name)
        print update_sql
        database_client_cursor.execute(update_sql)

if __name__ == '__main__':
    model = DataModel("123")
    print model
