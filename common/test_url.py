# author=xiangling
# coding=utf-8
from common.config import Config

config = Config()


class test_url(object):

    def __init__(self):
        URL = "URL"
        self.in_url = config.getConfigData(URL, 'in_url')
        self.cashier_url = config.getConfigData(URL, 'cashier_url')
        self.callback_url = config.getConfigData(URL, 'callback_url')
        self.mch_url = config.getConfigData(URL, 'mch_url')
        self.m_url = config.getConfigData(URL, 'm_url')
        self.notify_url = config.getConfigData(URL, 'notify_url')
        self.wallet_url = config.getConfigData(URL, 'wallet_url')
        self.www_url = config.getConfigData(URL, 'www_url')
        self.elasticjob_url = config.getConfigData(URL, 'elasticjob_url')
