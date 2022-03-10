#!/usr/bin/env python 
# -*- coding: utf-8 -*- 
# @File : B2C_trade_01.py
# @Author: xiangling
# @Date : 2018-10-11 
# @Desc :

import sys

# from pymysql.constants.FIELD_TYPE import JSON

from common.common_util import data_init
import requests
import re,urllib
from common.gettoken_H5 import GetToken_H5
from json import JSONDecodeError
from collections import OrderedDict
from common.get_data import get_data
from common.logger import logger
import json
import re

class B2C_trade_batch_pay(object):
    def __init__(self,url_dict):
        self.url = url_dict
        # 生成请求序列号
        self.req_seq_number = data_init().req_seq_number()
        #生成out_trade_no
        self.out_trade_no = data_init().serial_Bath_no()  #总商户订单号
        self.sub_out_trade_no_1=data_init().serial_Sub_no() #子商户订单号1
        self.sub_out_trade_no_2 = data_init().serial_Sub_no() #子商户订单号2
        self.in_headers = {'referer': 'in.mideaepayuat.com'}
        #生成外部退款号
        # self.out_refund_no = data_init().serial_no()


    def B2C_trade_H5(self, send_data):
        self.token_H5, self.token_time_H5 = GetToken_H5.get_token_H5(self.url,send_data)
        print("token_H5",self.token_H5)
        send_data.update({'is_guarantee': str(send_data["is_guarantee"]).upper()})
        send_data.update({'is_virtual_product': str(send_data["is_virtual_product"]).upper()})

        send_data.update({'req_seq_no': self.req_seq_number})
        #将token、token_time放入send_data
        send_data.update({'token': self.token_H5})
        send_data.update({'token_time': self.token_time_H5})
        #将out_trade_no、out_trade_time放入send_data
        send_data.update({'out_trade_no': self.out_trade_no})
        send_data.update({'out_trade_time': self.token_time_H5})

        sub1=send_data["sub_orders"][0]

        send_data.update({'sub_orders':[]})
        # 签名
        send_data["sign"] = data_init().get_sign_no_sort(send_data)
        send_data["sub_orders"].append(sub1)
        send_data["sub_orders"][0]["sub_out_trade_no"] = self.sub_out_trade_no_1
        # send_data["sub_orders"][1]["sub_out_trade_no"] = self.sub_out_trade_no_2
        #
        sub1=json.dumps(send_data["sub_orders"][0])
        send_data["sub_orders"][0]=json.loads(sub1)


        # send_data={'service': 'batch_trade_pay_cashier', 'version': '3.4.0', 'partner': 1000011005, 'input_charset': 'UTF-8', 'language': 'ZH-CN', 'sign_type': 'MD5_RSA_TW', 'notify_url': 'https://bg.mideaepayuat.com/testAcceptCheckSign.htm', 'return_url': 'https://bg.mideaepayuat.com/notifySuccessCheckSign.htm', 'cashier_product_type': 'DIRECT', 'is_guarantee': 'FALSE', 'out_trade_time': '20211027141527', 'payer_type': 'C', 'payer_login_name': 'test01', 'currency_type': 'CNY', 'total_order_amount': 6, 'total_amount': 4, 'total_count': 2, 'pay_expire_time': 30, 'is_virtual_product': 'TRUE', 'product_name': '空调', 'product_info': '收银台买买买', 'attach': 'C0012175;91441403314971889E;ck00065511', 'session_id': 355065053311001, 'return_script': 'http://www.midea.com', 'reference_url': 'https://mall.midea.com', 'risk_params': '{"ip":"127.0.0.1"}', 'terminal_type': 'PC', 'sub_orders': [{"pay_amount": 4, "market_acc_partner": 1010076133, "partner": 1000011005, "market_amount": 2, "sub_product_name": "冰箱", "sub_product_info": "收银台买买买,商品代码:X112323", "sub_attach": "子单attach", "profit_sharing": "FALSE", "sub_out_trade_no": "TestSubBatch2021102714152781"}], 'req_seq_no': '8961b7b7b4d34946bd3b52e6d5bbb007', 'token': 'f50e9c6ac78a1d1bf4ba0ac82b2c106ee5de46cb3c4455d6766f1d8c93e601aa8da03a6e9bb4e3931ffa441a3dfb9b975ff617019df020fea69f239ab57cda5352318ff3314e419f6c766ba655026fd7', 'token_time': '20211027141527', 'out_trade_no': 'TestBatch2021102714152791'}

        #进入收银台
        r = requests.post(self.url["B2C_trade_url"], send_data, verify=False)
        print("000000000000000000",r.text)
        result_orderinfo = r.text[87:-10]
        return result_orderinfo,self.out_trade_no
        # #重定向
        # session = requests.Session()
        # m_url = 'https://m.mideaepayuat.com/mallCashierNew.htm?'
        # send_url = m_url + result_orderinfo
        # r = session.get(send_url, verify=False)
        # # 获取公共信息
        # common_url = 'https://m.mideaepayuat.com/common/getCommonInfo.htm'
        # r = session.post(common_url, verify=False)
        # result = json.loads(r.text)
        # contextToken = result['data']['contextToken']
        # checkToken = result['data']['checkToken']
        #
        #
        # #第三方支付
        # thirCreditPayUrl = "https://m.mideaepayuat.com/escrow/thirdCreditPay.htm"
        # send_data = OrderedDict()
        # send_data["contextToken"] = contextToken
        # send_data["checkToken"]=checkToken
        # send_data["productId"]='1001'
        # send_data["returnScript"]="https://m.mideaepayuat.com/mallCashierNew.htm?order=7f0ad4e85a8c2252361f163dc9db40515b07cefb39249b809e90319806fcdeef321c5be3874da2af2cbc139aefb59993dff6aada5c24bd79d9628b41c3012780dcab62598744930450fa871c36bac62769ce351271cfce3f5e09829efd999265854e62d9f4c15bbfea71ec38865c3262345758d0db33f7bf3744dc80f0c3709fd6c900d8226343ccf231b077a3e2e5921d74cf95729a06b10368980042e70dc13535e2e48bbc678d7eeb14e64dc0a6a432f8fb990a1c1a391ffd9a0875b80cea71e961977151382948e526e34b3c79d960bb38dcc8290a496c4363b457114aafb21b61139d331d4b3521546a4e652e8507b29b5224b243fa816a458f059cd7449af47f50cdec25b851645a7fcfb6ba7bd0de6c0bdd2fd0e1201554ac4997ee80b320f956d3b1a41f153381650a71d628192c830aadc4da83082d3ae2b0e9b3315fdda6a67c4d8f28973c7e3678e14d67c24755bd9572d72345ac773131efb4f52dbb6c7e8a331fe79ac5e817be06bab9696d7cdeb102319300e07988dd4b510f0af78b80a1d8b6107bb41f25ebcecb3d2fa53b95e35bf7d520a85dfe7c13c9670f95357208a1b067048645a95bc13b0866332fc05f687b71bc18b78fac84d21b838642ece8c6649f32775254a953c42f7ce4bb7b258ad33084d5d8879fb10a8236c195a8b8a39ae17127956ec0e7e0e7f14ef5f76da20e5e57b7008026802add4538331fc939e95419b4c445b2648e9c861d2c16d4f5f38e80032dd54d57ea812a5a7261c665abee9bf58c58834958cf5921b5367cc5be89f4ff34f702fa421aee48bb00aa414f7a0fcb793c227785a6fea1144da87d35e596a2ebbd2218fd1c8bb232cb4aeb4e93cff8807b23a32fa4e47d8cecc8476f4dded08e1273b1c09661afc68d928c28f38ed5b1019b9763e7311daa71408932d3ce6f6e8bf41a879cbcebd996d64856e993d4f674423d0c50e2aef90d49b08fb451b1e5e6ea830cc2767d2605e432c5a850cba9e4061821063ef5869982322895f42dacc673ef4d4b753894090ca0dc062373a467c34355f52d50bc1c578dbfca56ffc638d01c2c9b6131b37ee3af1e5e5e249155868c60a8745c4b599ec4cd7f576dc9f5d6618b9e6a513dd99d1e5d5206b22e637c64a4fb60df27f707cf33e468fb4223a8e2e1ace76ebcc8ac3d797cc1ab23b5ee964ab0&amp;backToken=E2E0C35DE547F2567217C60953915370"
        # r = session.post(thirCreditPayUrl, send_data, verify=False)
        # result = r.json()
        # return result,self.out_trade_no\

    def B2C_BacthTrade_H5(self, send_data):

        send_data.update({'is_guarantee': str(send_data["is_guarantee"]).upper()})
        send_data.update({'is_virtual_product': str(send_data["is_virtual_product"]).upper()})

        send_data.update({'req_seq_no': self.req_seq_number})
        # 将token、token_time放入send_data

        # 将out_trade_no、out_trade_time放入send_data
        send_data.update({'out_trade_no': self.out_trade_no})
        self.token_H5, self.token_time_H5 = GetToken_H5.get_token_H5(self.url, send_data)

        send_data.update({'token': self.token_H5})
        send_data.update({'token_time': self.token_time_H5})
        send_data.update({'out_trade_time': self.token_time_H5})

        send_data["sub_orders"][0]["sub_out_trade_no"] = self.sub_out_trade_no_1
        send_data["sub_orders"][1]["sub_out_trade_no"] = self.sub_out_trade_no_2
        send_data["sub_orders"]=self.sub_orders(send_data)

        # # 签名
        send_data["sign"] = data_init().get_sign_no_sort(send_data)
        print("sign",send_data)


        # 进入收银台
        r = requests.post(self.url["B2C_trade_url"], send_data, verify=False)
        # print("000000000000000000", r.text)
        result_orderinfo = r.text[87:-10]
        return result_orderinfo,self.sub_out_trade_no_1,self.sub_out_trade_no_2


    def B2C_BacthTrade_PC(self, send_data):

        send_data.update({'is_guarantee': str(send_data["is_guarantee"]).upper()})
        send_data.update({'is_virtual_product': str(send_data["is_virtual_product"]).upper()})

        send_data.update({'req_seq_no': self.req_seq_number})
        # 将token、token_time放入send_data

        # 将out_trade_no、out_trade_time放入send_data
        send_data.update({'out_trade_no': self.out_trade_no})
        self.token_H5, self.token_time_H5 = GetToken_H5.get_token_H5(self.url, send_data)

        send_data.update({'token': self.token_H5})
        send_data.update({'token_time': self.token_time_H5})
        send_data.update({'out_trade_time': self.token_time_H5})

        send_data["sub_orders"][0]["sub_out_trade_no"] = self.sub_out_trade_no_1
        send_data["sub_orders"][1]["sub_out_trade_no"] = self.sub_out_trade_no_2
        logger.info(self.sub_out_trade_no_1)
        send_data["sub_orders"]=self.sub_orders(send_data)

        # # 签名
        send_data["sign"] = data_init().get_sign_no_sort(send_data)
        print("sign",send_data)


        # 进入收银台
        r = requests.post(self.url["B2C_trade_url"], send_data, verify=False)
        # print("000000000000000000", r.text)
        result_orderinfo = r.text[46:-10]
        return result_orderinfo

    def sub_orders(self,send_data):
        lst = list()
        for v in send_data["sub_orders"]:
            data = json.dumps(v)
            lst.append(data)
        send_data["sub_orders"] = lst
        print("send_data", send_data)
        str1 = str(send_data["sub_orders"])
        send_data["sub_orders"] = str1.replace("\'", "")
        return send_data["sub_orders"]




