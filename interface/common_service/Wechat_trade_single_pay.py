#!/usr/bin/env python 
# -*- coding: utf-8 -*- 
# @File : B2C_trade_01.py
# @Author: xiangling
# @Date : 2018-10-11 
# @Desc :


from common.common_util import data_init
import requests
from common.common_db import OperationMysql
from common.elasticjob import elasticjob
from time import sleep
from operationMysql.operation_db_order import OperationDbOrder
from operationMysql.operation_db_pay import OperationDbPay
from operationMysql.operation_db_bank import OperationDbBank
import time
from common.logger import logger


class Wechat_trade_single_pay(object):
    def __init__(self, url_dict):
        self.url = url_dict
        # 生成请求序列号
        self.req_seq_number = data_init().req_seq_number()
        # 生成out_trade_no
        self.out_trade_no = data_init().serial_no()
        self.in_headers = {'referer': 'in.mideaepayuat.com'}
        # 生成外部退款号
        self.out_refund_no = data_init().serial_no()
        self.out_trade_time = data_init().token_time()

    def V3_wechat_trade_app(self, send_data):

        send_data.update({'req_seq_no': self.req_seq_number})
        send_data.update({'out_trade_no': self.out_trade_no})
        send_data.update({'out_trade_time': self.out_trade_time})
        send_data.update({'is_guarantee': 'FALSE'})
        send_data.update({'is_virtual_product': 'TRUE'})
        sign = data_init().get_sign_no_sort(send_data)
        send_data["sign"] = sign

        out_trade_no = send_data["out_trade_no"]

        print("out_trade_no", out_trade_no)
        r = requests.post(self.url["B2C_trade_url"], send_data, verify=False)
        print(r.json())

        # 查询支付总单
        res = OperationMysql("db_order").query(
            'SELECT pay_total_no FROM db_order.t_trade WHERE out_trade_no="%s"' % out_trade_no)
        # print("1111",res)
        pay_total_no = res[0]["pay_total_no"]
        # 查询pos流水
        res = OperationMysql("db_pay").query(
            'SELECT pos_no FROM db_pay.t_pay_flow WHERE pay_total_no="%s"' % pay_total_no)
        print("11111", res)
        pos_no = res[0]["pos_no"]

        # 更新银行接口流水为支付成功
        OperationMysql("db_bank").update(
            'UPDATE db_bank.t_bank_tran SET pay_status=1 WHERE tran_no="%s"' % pos_no)

        # 更新银行接口流水为支付成功
        OperationMysql("db_bank").update(
            'UPDATE db_bank.t_ebank_tran SET pay_status=1 WHERE tran_no="%s"' % pos_no)

        # 触发定时任务，更新支付流水为成功，交易订单状态为已到账
        elasticjob(self.url, "paycore-repair-job").jobTrigger("payRepairProducerJob")
        # sleep(120)
        data_res = self.query_order_trade(out_trade_no)
        pay_total_no = self.get_pay_total_no(out_trade_no)
        return r.json(), data_res, pay_total_no

    def V3_escrow_wechat_h5(self, send_data):

        send_data.update({'req_seq_no': self.req_seq_number})
        send_data.update({'out_trade_no': self.out_trade_no})
        send_data.update({'out_trade_time': self.out_trade_time})
        send_data.update({'is_guarantee': 'FALSE'})
        send_data.update({'is_virtual_product': 'TRUE'})
        send_data.update({'profit_sharing': 'FALSE'})
        sign = data_init().get_sign_no_sort(send_data)
        send_data["sign"] = sign

        out_trade_no = send_data["out_trade_no"]

        print("out_trade_no", out_trade_no)
        r = requests.post(self.url["B2C_trade_url"], send_data, verify=False)

        # 查询支付总单
        res = OperationMysql("db_order").query(
            'SELECT trade_no FROM db_order.t_trade WHERE out_trade_no="%s"' % out_trade_no)
        # print("1111",res)
        trade_no = res[0]["trade_no"]
        # #查询pos流水
        # res = OperationMysql("db_pay").query(
        #     'SELECT pos_no FROM db_pay.t_pay_flow WHERE pay_total_no="%s"' % pay_total_no)
        # print("11111", res)
        # pos_no = res[0]["pos_no"]
        #
        # #更新银行接口流水为支付成功
        OperationMysql("db_bank").update(
            'UPDATE  db_escrow_channel.t_channel_tran SET trade_status=1 WHERE trade_no="%s"' % trade_no)
        # 触发定时任务，更新支付流水为成功，交易订单状态为已到账
        # elasticjob(self.url, "escrow-trade-job").jobTrigger("arriveRepairProducerJob")

        # 托管渠道补单地址：https://bg.mideaepayuat.com/escrow/channel/repairPayOrder.htm
        # tranNo: 10446801121001202110310000000969
        print(r.json())

        return r.json()

    def V3_wechat_mini_program(self, send_data):
        """
        @Author: xiongyc9
        Functions:
            微信小程序支付-单笔
        Parameters:
            send_data: 支付发起时发送的参数数据
        Returns:
            result: 接口返回的json数据
            out_trade_no: 订单外部商户号
            trade_no: 订单号
        Raises:
            暂无
        """

        send_data.update({'req_seq_no': self.req_seq_number})
        send_data.update({'out_trade_no': self.out_trade_no})
        send_data.update({'out_trade_time': self.out_trade_time})
        send_data.update({'is_guarantee': str(
            send_data["is_guarantee"]).upper()})
        send_data.update({'is_virtual_product': str(
            send_data["is_virtual_product"]).upper()})
        sign = data_init().get_sign_no_sort(send_data)
        send_data["sign"] = sign
        # 发起支付请求
        r = requests.post(self.url["B2C_trade_url"], send_data, verify=False)
        result = r.json()
        time.sleep(5)

        out_trade_no = send_data["out_trade_no"]
        trade_no =  OperationDbOrder().query_trade_no_by_out_trade_no(out_trade_no)
        # 查询支付总单
        pay_total_no = OperationDbOrder().query_pay_total_no_by_trade_no(trade_no)
        # 查询pos流水
        pos_no = OperationDbPay().query_pos_no_by_pay_total_no(pay_total_no)
        # 更新银行接口流水为支付成功
        OperationDbBank().update_db_bank_by_pos_no(pos_no)
        if send_data["is_guarantee"] == "TRUE":
            OperationDbOrder().update_confirm_receive_status_by_trade_no(trade_no)
        return result, out_trade_no, trade_no

    def V3_wechat_scan_code(self, send_data):

        send_data.update({'req_seq_no': self.req_seq_number})
        send_data.update({'out_trade_no': self.out_trade_no})
        send_data.update({'out_trade_time': self.out_trade_time})
        send_data.update({'is_guarantee': 'FALSE'})
        send_data.update({'is_virtual_product': 'TRUE'})
        send_data.update({'profit_sharing': 'FALSE'})
        sign = data_init().get_sign_no_sort(send_data)
        send_data["sign"] = sign

        out_trade_no = send_data["out_trade_no"]

        print("out_trade_no", out_trade_no)
        r = requests.post(self.url["B2C_trade_url"], send_data, verify=False)
        # print("1111111111111111111111",r.json())
        #
        # # 查询支付总单
        # res = OperationMysql("db_order").query(
        #     'SELECT pay_total_no FROM db_order.t_trade WHERE out_trade_no="%s"' % out_trade_no)
        # # print("1111",res)
        # pay_total_no = res[0]["pay_total_no"]
        # # 查询pos流水
        # res = OperationMysql("db_pay").query(
        #     'SELECT pos_no FROM db_pay.t_pay_flow WHERE pay_total_no="%s"' % pay_total_no)
        # print("11111", res)
        # pos_no = res[0]["pos_no"]
        #
        # # 更新银行接口流水为支付成功
        # OperationMysql("db_bank").update(
        #     'UPDATE db_bank.t_bank_tran SET pay_status=1 WHERE tran_no="%s"' % pos_no)
        # # 触发定时任务，更新支付流水为成功，交易订单状态为已到账
        # elasticjob(self.url, "paycore-repair-job").jobTrigger("payRepairProducerJob")
        # sleep(120)
        # data_res = self.query_order_trade(out_trade_no)
        # pay_total_no = self.get_pay_total_no(out_trade_no)
        # return r.json(), data_res, pay_total_no
        return r.json()

    def query_order_trade(self, out_trade_no):
        # 查询订单
        res = OperationMysql("db_order").query(
            'SELECT * FROM db_order.t_trade WHERE out_trade_no="%s"' % out_trade_no)
        if res:
            return res[0]
        else:
            return None

    def get_pay_total_no(self, out_trade_no):
        res = OperationMysql("db_order").query(
            'SELECT pay_total_no FROM db_order.t_trade WHERE out_trade_no="%s"' % out_trade_no)
        if res:
            return res[0]["pay_total_no"]
        else:
            return None

    def get_pay_flow(self, pay_total_no):
        # pay_total_no=self.get_pay_total_no(out_trade_no)["pay_total_no"]
        res = OperationMysql("db_pay").query(
            'SELECT pay_flow_no FROM db_pay.t_pay_flow  WHERE pay_total_no="%s"' % pay_total_no)
        if res:
            return res
        else:
            return None

    def get_act_history(self, pay_flow_no):
        res = OperationMysql("db_act").query(
            'SELECT dc_type,tran_amount,inner_remark,trade_msg FROM db_act.t_act_history WHERE `pay_flow_no` ="%s"' % pay_flow_no)
        if res:
            return res
        else:
            return None

    def get_bank_act_hisotry(self, pay_flow_no):
        res = OperationMysql("db_bank_act").query(
            'SELECT dc_type,tran_amount,inner_remark,trade_msg from db_bank_act.t_bank_history  WHERE `pay_flow_no` ="%s"' % pay_flow_no)
        if res:
            return res
        else:
            return None
