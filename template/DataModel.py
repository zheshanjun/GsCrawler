# coding=gbk
from DBClient import *


class DataModel:
    # self.code：工商注册码
    # self.update_status：查询状态 {-1:未更新, 0:代码不存在, 1:代码存在, 8:网页模板异常}
    def __init__(self, code):
        self.code = code
        self.update_status = -1

    def set_update_status(self, status):
        self.update_status = status

    def __str__(self):
        return 'code:%s, update_status:%d' % (self.code, self.update_status)

    def update_to_db(self):
        update_sql = "update GsSrc set updateStatus = %d, lastUpdateTime = getDate() where registeredCode = '%s'"\
                     % (self.update_status, self.code)
        print update_sql
        database_client_cursor.execute(update_sql)

if __name__ == '__main__':
    model = DataModel("123")
    print model
