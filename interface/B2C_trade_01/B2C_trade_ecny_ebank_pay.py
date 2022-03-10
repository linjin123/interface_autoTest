#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File : B2C_trade_ecny_ebank_pay.py
# @Author: xiongyc9
# @Date : 2021-12-23
# @Desc : 邮储数字人民币网银支付

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
import time
from common.common_db import OperationMysql
from common.elasticjob import elasticjob
from operationMysql.operation_db_order import OperationDbOrder
from operationMysql.operation_db_pay import OperationDbPay
from operationMysql.operation_db_bank import OperationDbBank
from operationMysql.operation_db_escrow_channel import OperationDbEscrowChannel
from operationMysql.operation_db_escrow_trade import OperationDbEscrowTrade


class B2CTradeEcnyEbankPay:
    def __init__(self, url_dict):
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

    def b2c_trade_PC_ecny_ebank_pay(self, order_info, repeat_flag):

        session = requests.Session()
        r = session.get(order_info, headers=self.in_headers, verify=False)
        result = r.text
        contextToken_array = re.findall(r'window.contextToken="(.+?)"', result)
        tradeNo_array = re.findall(r'window.tradeNo="(.+?)"', result)

        send_data = OrderedDict()
        try:
            send_data["contextToken"] = contextToken_array[0]
            # 获取交易订单号
            trade_no = tradeNo_array[0]
            logger.info(trade_no)
        except IndexError as e:
            print('IndexError:', e)
            print('接入收银台失败，退出用例执行')
            sys.exit()

        ecny_ebank_url = self.url["ecny_ebank_url"]
        send_data["eWalletId"] = "0082000000012113"
        send_data["eWalletName"] = '桃江财政局零余额账户'
        send_data["bankType"] = '6900'

        # 0为单笔支付，1为重复支付
        if repeat_flag == 0:
            r = session.post(ecny_ebank_url, send_data, headers=self.in_headers, verify=False)
            result = r.json()
        # 重复支付
        else:
            r = session.post(ecny_ebank_url, send_data, headers=self.in_headers, verify=False)
            time.sleep(5)
            r = session.post(ecny_ebank_url, send_data, headers=self.in_headers, verify=False)
            result = r.json()
        session.post(self.url["Logout_url"], verify=False)

        # 根据订单号查询数字人民币网银支付渠道流水，将支付状态pay_status=1
        res = OperationDbEscrowChannel().update_ecny_ebank_tran(trade_no)

        # 触发escrow-trade-job的付款补单任务payRepairProducerJob
        elasticjob(self.url, "escrow-trade-job").jobTrigger("payRepairProducerJob")

        pay_total_no = OperationDbEscrowTrade().query_trade_no_by_rele_order_no(trade_no)[0]["trade_no"]
        ecny_ebank_pay_status = OperationDbEscrowTrade().query_pay_total_order(pay_total_no)["pay_status"]
        run_count = 1
        # 循环判断是否获取到数据，只有获取到数据之后才会进行后续操作
        while ecny_ebank_pay_status != 3:
            time.sleep(3)
            ecny_ebank_pay_status = OperationDbEscrowTrade().query_pay_total_order(pay_total_no)["pay_status"]
            run_count += 1
            if run_count > 20:
                raise RuntimeError('邮储数字人民币支付未成功')

        # 对账详单入库：db_checkrecord.t_escrow_channel_trade_detail

        #
        return result, trade_no
