#!/usr/bin/env python 
# -*- coding: utf-8 -*- 
# @File : B2C_trade_01.py
# @Author: xiangling
# @Date : 2018-10-11 
# @Desc :
import logging
import time
import datetime
from common.common_util import data_init
import requests
from common.elasticjob import elasticjob
from operationMysql.operation_db_order import OperationDbOrder
from operationMysql.operation_db_escrow_channel import OperationDbEscrowChannel
from operationMysql.operation_db_escrow_trade import OperationDbEscrowTrade
from operationMysql.operation_db_checkrecord import OperationDbCheckrecord
from operationMysql.operation_db_bank import OperationDbBank
from common.escorw_trade_check import EscrowTradeCheck
from common.dubbo import dubbo




class EscrowTradeSingleAlipay(object):
    def __init__(self, url_dict):
        self.url = url_dict
        # 生成请求序列号
        self.req_seq_no = data_init().req_seq_number()
        # 生成out_trade_no
        self.out_trade_no = data_init().serial_no()
        self.in_headers = {'referer': 'in.mideaepayuat.com'}
        # 生成外部退款号
        self.out_refund_no = data_init().serial_no()
        self.out_trade_time = data_init().token_time()
        self.elasticjob_url = {"elasticjob_url": "http://10.16.157.96:20814"}

    def V3_alipay_scan_code(self, send_data):

        send_data.update({'req_seq_no': self.req_seq_no})
        send_data.update({'out_trade_no': self.out_trade_no})
        send_data.update({'out_trade_time': self.out_trade_time})
        send_data.update({'is_guarantee': str(send_data["is_guarantee"]).upper()})
        send_data.update({'is_virtual_product': str(send_data["is_virtual_product"]).upper()})
        send_data.update({'profit_sharing': str(send_data["profit_sharing"]).upper()})
        sign = data_init().get_sign_no_sort(send_data)
        send_data["sign"] = sign

        out_trade_no = send_data["out_trade_no"]

        print("out_trade_no", out_trade_no)
        r = requests.post(self.url["B2C_trade_url"], send_data, verify=False)
        print("r",r.json())


        #查询支付总单
        data_res = OperationDbOrder().query_trade_info_by_out_trade_no(out_trade_no)
        print("data_res",data_res)
        # # # 更新银行接口流水为支付成功
        OperationDbBank().update_db_bank_by_pos_no(data_res["trade_no"])

        # # 触发定时任务，更新支付流水为成功，交易订单状态为已到账
        # elasticjob(self.url, "paycore-repair-job").jobTrigger("payRepairProducerJob")
        time.sleep(200)
        pay_total_no = data_res["pay_total_no"]
        return r.json(), data_res, pay_total_no

    # 托管交易下单
    def escrow_trade_single_pay(self, send_data):
        send_data.update({'req_seq_no': self.req_seq_no})
        send_data.update({'out_trade_no': self.out_trade_no})
        send_data.update({'out_trade_time': self.out_trade_time})
        send_data.update({'is_guarantee': str(send_data["is_guarantee"]).upper()})
        send_data.update({'is_virtual_product': str(send_data["is_virtual_product"]).upper()})
        send_data.update({'profit_sharing': str(send_data["profit_sharing"]).upper()})
        trade_amount = send_data['pay_amount']
        market_amount = 0
        if 'market_amount' in send_data.keys():
            if send_data["market_amount"] is not None:
                market_amount = send_data['market_amount']
        total_amount = int(trade_amount) + int(market_amount)
        send_data.update({'order_amount': total_amount})
        # 获取外部订单号
        out_trade_no = send_data["out_trade_no"]
        partner = send_data["partner"]
        # 获取下单签名
        sign = data_init().get_sign_no_sort(send_data)
        send_data["sign"] = sign
        # 进行下单
        pay_result = requests.post(self.url["B2C_trade_url"], data=send_data, verify=False)
        result_code = pay_result.json()['result_code']
        # 断言下单结果是否为成功，成功才往下执行
        if result_code == '1001':
            return pay_result.json(), out_trade_no, partner
        else:
            raise RuntimeError('支付下单失败，交易订单号：%s' % out_trade_no)

    # @Author: linxy57
    # @Date : 2021-12-15
    # @Desc : 托管支付宝-单笔即时到账-支付成功不做到账
    def escrow_trade_single_pay_success(self, send_data):
        # 进行支付下单
        pay_result, out_trade_no, partner = EscrowTradeSingleAlipay(self.url).escrow_trade_single_pay(send_data)
        # 查询交易订单
        trade_detail = OperationDbOrder().query_trade_detail(out_trade_no, partner)
        trade_no = trade_detail["trade_no"]
        # 支付总单号
        pay_total_no = trade_detail["pay_total_no"]
        # 查询托管交易支付总单
        pay_total_detail = OperationDbEscrowTrade().query_pay_total_order(pay_total_no)
        trade_inner_id = pay_total_detail["trade_inner_id"]
        # 第一笔托管交易流水号
        receive_pay_flow_no = pay_total_no + '-' + str(trade_inner_id) + '-01'
        # 检查托管交易收款流水内部状态
        check_result = EscrowTradeCheck().check_receive_pay_flow(trade_no, receive_pay_flow_no)
        if check_result == True:
            time.sleep(2)
            pay_total_detail = OperationDbEscrowTrade().query_pay_total_order(pay_total_no)
            pay_total_pay_status = pay_total_detail["pay_status"]
            pay_total_pay_inner_status = pay_total_detail["pay_inner_status"]
            loop_count = 0
            while (pay_total_pay_status != 3 or pay_total_pay_inner_status != 1) and loop_count < 10:
                time.sleep(2)
                pay_total_detail = OperationDbEscrowTrade().query_pay_total_order(pay_total_no)
                pay_total_pay_status = pay_total_detail["pay_status"]
                pay_total_pay_inner_status = pay_total_detail["pay_inner_status"]
                loop_count += 1
            if loop_count >= 10:
                raise RuntimeError('更新托管交易支付总单状态异常，交易订单号：%s' % trade_no)
            time.sleep(2)
            trade_detail = OperationDbOrder().query_trade_detail_by_trade_no(trade_no)
            trade_status = trade_detail["trade_status"]
            arrival_status = trade_detail["arrival_status"]
            loop_count = 0
            while (trade_status != 3 or arrival_status != 1) and loop_count < 10:
                time.sleep(2)
                trade_detail = OperationDbOrder().query_trade_detail_by_trade_no(trade_no)
                trade_status = trade_detail["trade_status"]
                arrival_status = trade_detail["arrival_status"]
                loop_count += 1
            if loop_count == 10:
                raise RuntimeError('更新托管交易订单状态异常，交易订单号：%s' % trade_no)
            return trade_detail

    # @Author: linxy57
    # @Date : 2021-11-07
    # @Desc : 托管支付宝-单笔即时到账-资金已到账
    def escrow_trade_single_pay_arrival(self, send_data):
        # 进行支付下单
        pay_result, out_trade_no, partner = EscrowTradeSingleAlipay(self.url).escrow_trade_single_pay(send_data)
        # 查询交易订单
        trade_detail = OperationDbOrder().query_trade_detail(out_trade_no, partner)
        trade_no = trade_detail["trade_no"]
        # 支付总单号
        pay_total_no = trade_detail["pay_total_no"]
        # 第一笔托管交易流水号
        receive_pay_flow_no = pay_total_no + '-100-01'
        # 第二笔分账流水号
        profit_pay_flow_no = pay_total_no + '-100-02'
        # 检查托管交易收款流水内部状态
        check_result = EscrowTradeCheck().check_receive_pay_flow(trade_no, receive_pay_flow_no)
        assert check_result == True
        pay_time = (datetime.datetime.now() + datetime.timedelta(days=-1)).strftime("%Y-%m-%d %H:%M:%S")
        OperationDbOrder().update_pay_time_by_trade_no(trade_no, pay_time)
        # 插入对账数据，模拟对账单入库
        OperationDbCheckrecord().insert_escrow_channel_trade_detail(trade_no)
        # 触发escrow-trade-job:网银对账单补单任务，第一笔收款流水更新为资金已到账
        elasticjob(self.elasticjob_url, "escrow-trade-job").jobTrigger("arriveRepairProducerJob")
        # dubbo().RepairTradeFacade_arriveRepairForOnlinePay_dubbo(receive_pay_flow_no)
        time.sleep(5)
        # 检查托管交易分账流水内部状态
        check_result = EscrowTradeCheck().check_profit_pay_flow(trade_no, profit_pay_flow_no)
        assert check_result == True
        # 等待第二笔托管交易流水内部状态为渠道受理成功，插入模拟安心户加款sql
        OperationDbEscrowChannel().insert_reverse_tran(profit_pay_flow_no)
        # 触发escrow-channel-task-schedule-job:线下收款任务
        # elasticjob_url = self.url["elasticjob_url"]
        elasticjob(self.elasticjob_url, "escrow-channe-task-schedule-job").jobTrigger("ReverseAccountingJob")
        # dubbo().ReverseAccountingJob()
        time.sleep(5)
        profit_pay_flow_list = OperationDbEscrowTrade().query_trade_flow(profit_pay_flow_no)
        profit_pay_inner_status = profit_pay_flow_list['pay_inner_status']
        loop_count = 0
        while profit_pay_inner_status != 8 and loop_count < 10:
            time.sleep(5)
            elasticjob(self.elasticjob_url, "escrow-channe-task-schedule-job").jobTrigger("ReverseAccountingJob")
            profit_pay_flow_list = OperationDbEscrowTrade().query_trade_flow(profit_pay_flow_no)
            profit_pay_inner_status = profit_pay_flow_list['pay_inner_status']
            loop_count += 1
        if loop_count == 10:
            raise RuntimeError('到账状态异常')
        # 查询托管交易总单是否资金已到账
        pay_total_detail = OperationDbEscrowTrade().query_pay_total_order(pay_total_no)
        pay_total_pay_status = pay_total_detail['pay_status']
        pay_total_inner_status = pay_total_detail['pay_inner_status']
        if pay_total_pay_status != 3 or pay_total_inner_status != 5:
            raise RuntimeError('总单到账状态异常')
        # 订单是否资金已到账
        trade_detail = OperationDbOrder().query_trade_detail(out_trade_no, partner)
        trade_status = trade_detail['trade_status']
        arrival_status = trade_detail['arrival_status']
        if trade_status != 3 or arrival_status != 3:
            raise RuntimeError('订单到账状态异常')
        return trade_detail, pay_total_detail

    # @Author: ex_yuanxiao3
    # @Date : 2022-02-06
    # @Desc : 托管支付宝-单笔即时到账-关单退款
    def escrow_trade_single_pay_close_refund(self, send_data,url_dict):
        # 进行支付下单
        pay_result, out_trade_no, partner = EscrowTradeSingleAlipay(self.url).escrow_trade_single_pay(send_data)
        OperationDbOrder().close_Order_trade_by_trade_no(out_trade_no)
        # 查询交易订单
        trade_detail = OperationDbOrder().query_trade_detail(out_trade_no, partner)
        trade_no = trade_detail["trade_no"]
        # 支付总单号
        pay_total_no = trade_detail["pay_total_no"]
        # 查询托管交易支付总单
        pay_total_detail = OperationDbEscrowTrade().query_pay_total_order(pay_total_no)
        trade_inner_id = pay_total_detail["trade_inner_id"]
        # 第一笔托管交易流水号
        receive_pay_flow_no = pay_total_no + '-' + str(trade_inner_id) + '-01'
        # 检查托管交易收款流水内部状态
        check_result = EscrowTradeCheck().check_receive_pay_flow(trade_no, receive_pay_flow_no)
        if check_result == True:
            time.sleep(2)
            pay_total_detail = OperationDbEscrowTrade().query_pay_total_order(pay_total_no)
            pay_total_pay_status = pay_total_detail["pay_status"]
            pay_total_pay_inner_status = pay_total_detail["pay_inner_status"]
            loop_count = 0
            while (pay_total_pay_status != 3 or pay_total_pay_inner_status != 1) and loop_count < 10:
                time.sleep(2)
                pay_total_detail = OperationDbEscrowTrade().query_pay_total_order(pay_total_no)
                pay_total_pay_status = pay_total_detail["pay_status"]
                pay_total_pay_inner_status = pay_total_detail["pay_inner_status"]
                loop_count += 1
            if loop_count >= 10:
                raise RuntimeError('更新托管交易支付总单状态异常，交易订单号：%s' % trade_no)
            time.sleep(2)
            trade_detail = OperationDbOrder().query_trade_detail_by_trade_no(trade_no)
            elasticjob(url_dict, "mch-job").jobTrigger("mchjobs-tradeOrderCloseRefundElasticJob")
            time.sleep(2)
            OperationDbCheckrecord().insert_escrow_channel_trade_detail(trade_no)
            elasticjob(url_dict, "escrow-trade-job").jobTrigger("arriveRepairProducerJob")

            return trade_detail

