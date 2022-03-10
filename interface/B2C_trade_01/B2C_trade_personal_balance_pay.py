#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File : B2C_trade_01.py
# @Author: xiongyc9
# @Date : 2021-12-20
# @Desc : PC收银台，余额支付

import requests
import sys
from json import JSONDecodeError
from collections import OrderedDict
from common.logger import logger
import re,urllib.parse

class B2cPersonalBalancePay(object):
    def __init__(self,url_dict):
        self.url = url_dict
        self.in_headers = {'referer': self.url["B2C_trade_url"]}

    def B2C_trade_PC_personal_balance_pay(self, pay_data, order_info):
        session = requests.Session()
        r =  session.get(order_info, headers=self.in_headers, verify=False)
        result = r.text
        contextToken_array = re.findall(r'window.contextToken="(.+?)"', result)
        tradeNo_array = re.findall(r'window.tradeNo="(.+?)"', result)

        cashier_data = OrderedDict()
        try:
            cashier_data["contextToken"] = contextToken_array[0]
            #获取交易订单号
            trade_no = tradeNo_array[0]
            logger.info(trade_no)
        except IndexError as e:
            print('IndexError:', e)
            print('接入收银台失败，退出用例执行')
            sys.exit()

        #获取si、pwdkey、salt
        cashier_headers = {'referer': order_info}
        try:
            t = session.post(self.url["GetPayPwdKey_url"], headers=cashier_headers, verify=False)
            t = t.json()
        except JSONDecodeError as e:
            print('JSONDecodeError:',e)
            print('获取si、pwdkey、salt失败，退出用例执行')
            sys.exit()
        cashier_data["si"] = t['si']
        cashier_data["salt"] = t['salt']
        getgenPwd_data = OrderedDict()
        getgenPwd_data["si"] = "%s" % cashier_data["si"]
        getgenPwd_data["password"] = pay_data["password"]
        getgenPwd_data["salt"] = "%s" % cashier_data["salt"]

        r = requests.post(self.url["Get_genPwd_url"], getgenPwd_data, verify=False)
        r = r.json()
        data = r['data']
        payPwd = urllib.parse.unquote(data)

        #支付数据
        paydata = {'bindNo': pay_data["bindNo"], #余额支付
                    'payType':pay_data["payType"], #余额支付
                    'contextToken': cashier_data["contextToken"],
                    'tradeNo': '%s' % trade_no,
                    'password': '%s' % payPwd,
                    'si': cashier_data["si"]}
        #==================================================================================
        r = session.post(self.url["Pay_url"], paydata, headers=self.in_headers,verify=False)
        result = r.json()
        #退出登录
        session.post(self.url["Logout_url"], verify=False)
        return result, trade_no

