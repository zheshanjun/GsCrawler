# coding=gbk
import PackageTool
import sys
print sys.path
from template.UpdateJob import UpdateJob
from NingxiaFirefoxSearcher import NingXiaFirefoxSearcher
from template.logger import logging


class NingxiaUpdateJob(UpdateJob):

    def set_config(self):
        self.process_name = 'NingxiGs'
        self.province = u'���Ļ���������'
        self.searcher = NingXiaFirefoxSearcher()


if __name__ == "__main__":
    
    job = NingxiaUpdateJob()
    job.run()


