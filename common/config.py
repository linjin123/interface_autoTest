# -*- coding: utf-8 -*- 
# @File : config.py
# @Author: julia 
# @Date : 2018/9/13 
# @Desc : 读取config.ini 配置文件

from configparser import ConfigParser
import os

BASE_DIR = os.path.dirname(os.path.realpath(__file__))
root_path = os.path.abspath(os.path.join(BASE_DIR, "../"))


class Config():
    CATEGORY = "SIT"
    PARTNER = "partner"
    LOGIN_NAME = "login_name"

    def __init__(self):
        self.config = ConfigParser()
        self.conf_path = os.path.join(root_path, 'config.ini')
        if not os.path.exists(self.conf_path):
            raise FileNotFoundError("请确保配置文件存在！")
        self.config.read(self.conf_path, encoding="utf-8")

    def getConfigData(self, title, value):
        return self.config.get(title, value)


'''
if __name__=='__main__':
    a=Config()
    c=a.getConfigData(a.CATEGORY,a.PARTNER)
    print(c)
'''
