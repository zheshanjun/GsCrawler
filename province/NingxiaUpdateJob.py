# coding=gbk
from NingxiaFirefoxSearcher import NingXiaFirefoxSearcher
from template.UpdateJob import UpdateJob


class NingxiaUpdateJob(UpdateJob):

    def set_config(self):
        self.process_name = 'NingxiaGs'
        self.province = u'宁夏回族自治区'
        self.searcher = NingXiaFirefoxSearcher()

if __name__ == "__main__":
    
    job = NingxiaUpdateJob()
    job.run()


