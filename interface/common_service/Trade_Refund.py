#!/usr/bin/env python 
# -*- coding: utf-8 -*- 
# @File : B2C_trade_01.py
# @Author: xiangling
# @Date : 2018-10-11 
# @Desc :

import sys
from common.common_util import data_init
import requests
from time import sleep
from common.common_db import OperationMysql
from operationMysql.operation_db_order import OperationDbOrder
from simple_settings import settings
from common.elasticjob import elasticjob

class Trade_Refund(object):
    def __init__(self,url_dict=None):

        # self.url = url_dict
        # print("111111111", self.url["Pay_H5_url"])
        #获取商户接入url
        # self.partnerin_url = test_url().in_url
        # 生成请求序列号
        self.req_seq_number = data_init().req_seq_number()
        self.time=data_init().token_time()
        #获取token、token_time(PC收银台)
        # self.token, self.token_time = GetToken().get_token()
        #获取token、token_time（H5收银台）
        # self.token_H5, self.token_time_H5 = GetToken_H5().get_token_H5()
        #生成out_trade_no
        self.out_trade_no = data_init().serial_no()
        self.in_headers = {'referer': 'in.mideaepayuat.com'}
        #生成外部退款号
        self.out_refund_no = data_init().serial_no()

    #**************************************交易退款**************************************
    # def B2C_refund(self,send_data,out_trade_no,partner):
    def B2C_refund(self, send_data, trade):
        out_trade_no = trade["out_trade_no"]
        partner = trade["partner"]
        send_data["refund_total_amount"] = trade["trade_amount"]
        send_data["refund_market_amount"] = trade["market_amount"]
        send_data["refund_amount"] = trade["pay_amount"]

        # 将请求序列号放入send_data
        send_data.update({'req_seq_no': self.req_seq_number})
        # 将外部退款号放入send_data
        send_data.update({'out_refund_no': self.out_refund_no})
        # 将退款原单号放入send_data
        send_data.update({'out_trade_no': out_trade_no})
        send_data.update({'out_refund_time':self.time})
        send_data.update({'partner': partner})
        #签名
        sign = data_init().get_sign_no_sort(send_data)
        send_data.update({'sign': sign})
        # r = requests.post(self.url["B2C_refund_url"], send_data, verify=False)
        r = requests.post(settings.B2C_refund_url, send_data, verify=False)
        result = r.json()

        return result

    # OperationDbOrder().refund_trade_query(out_trade_no)

    def update_bank_pay_status_success(self,url_dict):
        elasticjob(url_dict, "paycore-repair-job").jobTrigger("refundRepairProducerJob")



    def three_Received(self,pay_total_no):
        # pay_total_no=self.query_paytotal_from_order_trade(out_trade_no)["pay_total_no"]


        res = OperationMysql("db_bank").query('''SELECT CONCAT('13', CEILING(RAND() * 9000000000000000000000000000 + 100000000000000000000000000000)) as tran_no,`real_bank_type` , CONCAT('21', CEILING(RAND() * 90000000000 + 10000000000000000000)) as `send_tran_no` , `bank_type` ,
                       CONCAT('13', CEILING(RAND() * 900000000000000000 + 10000000000000000000)) as pay_total_no ,
                       `pay_item_no` ,
                       `bank_tran_no` ,
                       `pay_amount` ,
                       `amount_encrypt` ,
                       `pay_status` ,
                       `tran_type` ,
                       `pos_type` ,
                       `account_type` ,
                       `partner` ,
                       `partner_name` ,                
                       NOW() as tran_time ,
                       NOW() as create_time,
                       NOW() as modify_time,
                       NOW() as rsp_time,
                       `remark` ,
                       `bank_name` ,
                       `interface_name` ,
                       `replace_name_flag` ,
                       `virtual_channel` 
                FROM db_bank.t_bank_tran
                WHERE pay_total_no = "%s" ''' % pay_total_no)
        value = res[0]
        print("111111111", value)
        OperationMysql("db_bank").update('''INSERT INTO db_bank.t_bank_tran(
                   `tran_no`,
                   `real_bank_type`,
                   `send_tran_no`,
                   `bank_type`,
                   `pay_total_no` ,
                   `pay_item_no` ,
                   `bank_tran_no` ,
                   `pay_amount` ,
                   `amount_encrypt` ,
                   `pay_status` ,
                   `tran_type` ,
                   `pos_type` ,
                   `account_type` ,
                   `partner` ,
                   `partner_name` ,                
                   tran_time ,
                   create_time,
                   modify_time,
                   rsp_time,
                   `remark` ,
                   `bank_name` ,
                   `interface_name` ,
                   `replace_name_flag` ,
                   `virtual_channel` 
) value ("%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s")
                                                             ''' % (
            value["tran_no"], value["real_bank_type"], value["send_tran_no"], value["bank_type"],
            value["pay_total_no"],value["pay_item_no"],
            # value["pay_item_no"].replace('\t',''),
            value["bank_tran_no"], value["pay_amount"], value["amount_encrypt"], value["pay_status"],
            value["tran_type"], value["pos_type"],
            value["account_type"], value["partner"], value["partner_name"],
            value["tran_time"],value["create_time"],value["modify_time"],value["rsp_time"],
            # "2021-11-14 18:47:26","2021-11-14 18:47:26","2021-11-14 18:47:26","2021-11-14 18:47:26",
            value["remark"],
            value["bank_name"],value["interface_name"],value["replace_name_flag"],value["virtual_channel"]))



    #**************************************B2C交易退款查询**************************************
    def B2C_trade_refund_query(self,send_data):
        # 将请求序列号放入send_data
        send_data.update({'req_seq_number': self.req_seq_number})
        #签名
        plain_text = data_init().get_plain_text(send_data)
        sign = data_init().get_sign_no_sort(plain_text)
        send_data.update({'sign': sign})
        #发起请求
        r = requests.post(settings.B2C_refund_url, send_data, verify=False)
        result = r.json()
        return result

    def refund_trade_query(self, out_trade_no):
        res = OperationMysql("db_order").query(
            'SELECT * FROM db_order.t_refund WHERE origi_out_trade_no="%s"' % out_trade_no)
        return res


    def query_paytotal_from_order_trade(self,out_trade_no):

        res = OperationMysql("db_order").query(
            'SELECT pay_total_no FROM db_order.t_trade WHERE out_trade_no="%s" '%(out_trade_no))

        return res[0]







