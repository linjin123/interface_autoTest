#!/usr/bin/env python 
# -*- coding: utf-8 -*- 
# @File : B2C_trade_01.py
# @Author: xiangling
# @Date : 2018-10-11 
# @Desc :

import sys
from common.common_util import data_init
import requests
from common.test_url import test_url
import re,urllib
from common.gettoken_H5 import GetToken_H5
from common.gettoken_PC import GetToken
from json import JSONDecodeError
from collections import OrderedDict
from common.get_data import get_data
from common.logger import logger
import json

class Trade_Query(object):
    def __init__(self,url_dict):
        self.url = url_dict
        # print("111111111", self.url["Pay_H5_url"])
        #获取商户接入url
        # self.partnerin_url = test_url().in_url
        # 生成请求序列号
        self.req_seq_number = data_init().req_seq_number()
        #获取token、token_time(PC收银台)
        self.token, self.token_time = GetToken().get_token()
        #获取token、token_time（H5收银台）
        # self.token_H5, self.token_time_H5 = GetToken_H5().get_token_H5()
        #生成out_trade_no
        self.out_trade_no = data_init().serial_no()
        self.in_headers = {'referer': 'in.mideaepayuat.com'}
        #生成外部退款号
        self.out_refund_no = data_init().serial_no()




    #***********************************B2C交易查单**************************************
    def B2C_trade_query(self,send_data):
        # 将请求序列号放入send_data
        send_data.update({'req_seq_number': self.req_seq_number})
        # 签名
        plain_text = data_init().get_plain_text(send_data)
        sign = data_init().get_sign_no_sort(plain_text)
        send_data.update({'sign': sign})
        #发起请求
        r = requests.post(self.url["B2C_trade_query_url"], send_data, verify=False)
        result = r.json()
        return result





