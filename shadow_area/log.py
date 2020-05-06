# -*- coding:utf-8 -*-

"""
Auther: Fan Tenglong
Time: 2019-11-28
"""

import logging
import time
import os

class Log(object):
    def __init__(self, logger=None, log_cate='log', file_level=logging.INFO, console_level=logging.INFO):
        '''
            指定保存日志的文件路径，日志级别，以及调用文件
            将日志存入到指定的文件中
        '''
        # 创建一个logger
        self.logger = logging.getLogger(logger)
        self.logger.setLevel(logging.DEBUG)
        # 创建一个handler，用于写入日志文件
        self.log_time = time.strftime("%Y_%m_%d")
        file_dir = os.getcwd() + '/' + log_cate
        #file_dir = os.path.abspath(os.path.dirname(__file__)) + '/' + log_cate
        if not os.path.exists(file_dir):
            os.mkdir(file_dir)
        self.log_path = file_dir
        self.log_name = self.log_path + "/" + self.log_time + '.log'

        fh = logging.FileHandler(self.log_name, 'a', encoding='utf-8')  # 这个是python3的
        fh.setLevel(file_level)
        # fh.setLevel(logging.INFO)

        # 再创建一个handler，用于输出到控制台
        ch = logging.StreamHandler()
        ch.setLevel(console_level)
        # ch.setLevel(logging.INFO)

        # 定义handler的输出格式
        formatter = logging.Formatter(
            '[%(asctime)s] [%(levelname)s] %(filename)s->%(funcName)s:%(lineno)d %(message)s')
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)

        # 给logger添加handler
        self.logger.addHandler(fh)
        self.logger.addHandler(ch)

        #  添加下面一句，在记录日志之后移除句柄
        # self.logger.removeHandler(ch)
        # self.logger.removeHandler(fh)
        # 关闭打开的文件
        fh.close()
        ch.close()

    def getlog(self):
        return self.logger


if __name__ == "__main__":
    log = Log(__name__).getlog()
    log.info('I am log main')