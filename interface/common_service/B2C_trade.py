#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File : B2C_trade_01.py
# @Author: xiangling
# @Date : 2021-11-9
# @Desc :B2C交易接入收银台

import sys
from common.common_util import data_init
import requests
from collections import OrderedDict
from common.logger import logger
import json


class B2C_trade_pay(object):
    def __init__(self, url_dict):
        self.url = url_dict
        # 生成out_trade_no
        self.out_trade_no = data_init().serial_no()
        self.req_seq_no = data_init().req_seq_no()
        self.sub_out_trade_no_1 = data_init().serial_Sub_no()
        self.sub_out_trade_no_2 = data_init().serial_Sub_no()

    def get_token(self, url, send_data):
        token_time = data_init().token_time()
        risk_params = json.loads(send_data["risk_params"])
        ip = risk_params["ip"]
        '''获取token'''
        token_data = OrderedDict()
        token_data["service"] = "auth_token"
        token_data["version"] = "3.0.0"
        token_data["req_seq_no"] = data_init().req_seq_no()
        token_data["partner"] = send_data["partner"]
        token_data["input_charset"] = send_data["input_charset"]
        token_data["language"] = send_data["language"]
        token_data["sign_type"] = send_data["sign_type"]
        token_data["terminal_type"] = send_data["terminal_type"]
        token_data["login_name"] = send_data["payer_login_name"]
        token_data["token_time"] = token_time
        token_data["ip"] = ip
        token_data["session_id"] = send_data["session_id"]
        # 获取签名
        token_data["sign"] = data_init().get_sign_no_sort(token_data)
        r = requests.post(url["B2C_trade_url"], token_data, verify=False)
        result = r.json()
        token = result['token']
        logger.info(token)
        return (token, token_time)

    def B2C_trade_single(self, send_data):
        send_data.update({'is_guarantee': str(
            send_data["is_guarantee"]).upper()})
        send_data.update({'is_virtual_product': str(
            send_data["is_virtual_product"]).upper()})
        send_data.update({'req_seq_no': self.req_seq_no})
        # 获取token、token_time并放入send_data
        self.token, self.token_time = self.get_token(self.url, send_data)
        send_data.update({'token': self.token})
        send_data.update({'token_time': self.token_time})
        # 将out_trade_no、out_trade_time放入send_data
        send_data.update({'out_trade_no': self.out_trade_no})
        send_data.update({'out_trade_time': self.token_time})
        # 签名
        send_data["sign"] = data_init().get_sign_no_sort(send_data)
        # 进入收银台
        r = requests.post(self.url["B2C_trade_url"], send_data, verify=False)

        if send_data["terminal_type"] == "MOBILE":
            order_info = r.text[87:-10]
        elif send_data["terminal_type"] == "PC":
            order_info = r.text[46:-10]
        else:
            sys.exit()
        logger.info(order_info)
        return order_info, self.out_trade_no

    def B2C_trade_batch(self, send_data):
        send_data.update({'is_guarantee': str(
            send_data["is_guarantee"]).upper()})
        send_data.update({'is_virtual_product': str(
            send_data["is_virtual_product"]).upper()})
        send_data.update({'req_seq_no': self.req_seq_no})

        self.token, self.token_time = self.get_token(self.url, send_data)
        # 将token、token_time放入send_data
        send_data.update({'token': self.token})
        send_data.update({'token_time': self.token_time})
        # 将out_trade_no、out_trade_time放入send_data
        send_data.update({'out_trade_time': self.token_time})
        send_data.update({'out_trade_no': self.out_trade_no})

        send_data["sub_orders"][0]["sub_out_trade_no"] = self.sub_out_trade_no_1
        send_data["sub_orders"][1]["sub_out_trade_no"] = self.sub_out_trade_no_2
        logger.info(self.sub_out_trade_no_1)
        send_data["sub_orders"] = self.sub_orders(send_data)
        # # 签名
        send_data["sign"] = data_init().get_sign_no_sort(send_data)
        print("sign", send_data)
        # 进入收银台
        r = requests.post(self.url["B2C_trade_url"], send_data, verify=False)

        if send_data["terminal_type"] == "MOBILE":
            order_info = r.text[87:-10]
        elif send_data["terminal_type"] == "PC":
            order_info = r.text[46:-10]
        else:
            sys.exit()
        logger.info(order_info)
        return order_info, self.out_trade_no, self.sub_out_trade_no_1, self.sub_out_trade_no_2

    def sub_orders(self, send_data):
        lst = list()
        for v in send_data["sub_orders"]:
            data = json.dumps(v)
            lst.append(data)
        send_data["sub_orders"] = lst
        print("send_data", send_data)
        str1 = str(send_data["sub_orders"])
        send_data["sub_orders"] = str1.replace("\'", "")
        return send_data["sub_orders"]
