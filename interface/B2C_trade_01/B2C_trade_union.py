#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File : B2C_trade_01.py
# @Author: xiongyc9
# @Date : 2021-11-30
# @Desc : 银联云闪付支付下单

import sys
from common.common_util import data_init
import requests
import re, urllib
from common.gettoken_H5 import GetToken_H5
from common.gettoken_PC import GetToken
from json import JSONDecodeError
from collections import OrderedDict
from common.get_data import get_data
from common.logger import logger
import json
from common.common_db import OperationMysql
from common.elasticjob import elasticjob
from operationMysql.operation_db_order import OperationDbOrder
from operationMysql.operation_db_pay import OperationDbPay
from operationMysql.operation_db_bank import OperationDbBank


class B2CTradeUnionPay:
    def __init__(self,url_dict):
        self.url = url_dict
        self.in_headers = {'referer': self.url["B2C_trade_url"]}

    def b2c_trade_H5_union_pay(self, order_info, url_dict, out_trade_no):
        # 重定向
        session = requests.Session()
        send_url = url_dict["mallCashier_url"] + order_info
        r = session.get(send_url, verify=False)

        # 获取公共信息
        r = session.post(url_dict["common_url"], verify=False)
        result = json.loads(r.text)
        contextToken = result['data']['contextToken']
        checkToken = result['data']['checkToken']

        # 第三方支付
        send_data = OrderedDict()
        send_data["contextToken"] = contextToken
        send_data["checkToken"] = checkToken
        send_data["isMall"] = 'true'
        send_data["bankType"] = '6116'

        r = session.post(url_dict["thirdCreditPayUrl"], send_data, verify=False)
        result = r.json()

        # 查询支付总单
        trade_no = OperationDbOrder().query_trade_no_by_out_trade_no(out_trade_no)
        # 查询支付总单
        pay_total_no = OperationDbOrder().query_pay_total_no_by_trade_no(trade_no)
        # 查询pos流水
        pos_no = OperationDbPay().query_pos_no_by_pay_total_no(pay_total_no)
        # 更新银行接口流水为支付成功
        # OperationDbBank().update_db_bank_by_pos_no(pos_no)
        return result, trade_no

    def b2c_trade_H5_union_pay_repeat(self, order_info, url_dict, out_trade_no):
        # 重定向
        session = requests.Session()
        send_url = url_dict["mallCashier_url"] + order_info
        r = session.get(send_url, verify=False)

        # 获取公共信息
        r = session.post(url_dict["common_url"], verify=False)
        result = json.loads(r.text)
        contextToken = result['data']['contextToken']
        checkToken = result['data']['checkToken']

        # 第三方支付
        send_data = OrderedDict()
        send_data["contextToken"] = contextToken
        send_data["checkToken"] = checkToken
        send_data["isMall"] = 'true'
        send_data["bankType"] = '6116'

        r = session.post(url_dict["thirdCreditPayUrl"], send_data, verify=False)
        r = session.post(url_dict["thirdCreditPayUrl"], send_data, verify=False)
        result = r.json()

        # 查询支付总单
        trade_no = OperationDbOrder().query_trade_no_by_out_trade_no(out_trade_no)
        # 查询支付总单
        pay_total_no = OperationDbOrder().query_pay_total_no_by_trade_no(trade_no)
        # 查询pos流水
        pos_no = OperationDbPay().query_pos_no_by_pay_total_no(pay_total_no)
        # 更新银行接口流水为支付成功
        # OperationDbBank().update_db_bank_by_pos_no(pos_no)
        return result, trade_no
