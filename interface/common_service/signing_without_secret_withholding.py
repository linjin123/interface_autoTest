#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: ex_zhangjf11
# @Date : 2022-03-10
# @Desc : 免密代扣签约公共方法


from common.common_util import data_init
import requests


class ContractingPublicMethod:
    def __init__(self, url_dict):
        self.url = url_dict
        # 生成请求序列号
        self.req_seq_no = data_init().req_seq_number()
        # 生成签约协议号
        self.out_sign_no = data_init().token_time()


    # 微信签约
    def wechat_signing(self,send_data):
        send_data.update({'req_seq_no': self.req_seq_no})
        send_data.update({'out_sign_no': self.out_sign_no})
        sign = data_init().get_sign_no_sort(send_data)
        send_data["sign"] = sign

        r = requests.post(self.url["B2C_trade_url"], send_data, verify=False)
        print("r", r.json())
        return r.json()

    # 微信签约查询
    def wechat_signing_query(self,send_data):
        pass


    #支付宝签约
    def alipay_signed(self,send_data):
        send_data.update({'req_seq_no': self.req_seq_no})
        send_data.update({'out_sign_no': self.out_sign_no})
        sign = data_init().get_sign_no_sort(send_data)
        send_data["sign"] = sign

        r = requests.post(self.url["B2C_trade_url"], send_data, verify=False)
        print("r", r.json())
        return r.json()


    # 支付宝签约查询
    def alipay_signed_inquiry(self,send_data):
        pass




