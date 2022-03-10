#!/usr/bin/env python 
# -*- coding: utf-8 -*- 
# @File : B2C_trade_01.py
# @Author: xiangling
# @Date : 2018-10-11 
# @Desc :



import requests
import time
import json
import datetime
from common.logger import logger
from common.common_db import OperationMysql
from common.elasticjob import elasticjob
from common.common_util import data_init
from operationMysql.operation_db_order import OperationDbOrder
from operationMysql.operation_db_escrow_channel import OperationDbEscrowChannel
from operationMysql.operation_db_escrow_trade import OperationDbEscrowTrade
from operationMysql.operation_db_checkrecord import OperationDbCheckrecord
from common.escorw_trade_check import EscrowTradeCheck
from common.dubbo import dubbo


class EscrowTradeBatchAlipay(object):
    def __init__(self, url_dict):
        self.url = url_dict
        # 生成请求序列号
        self.req_seq_no = data_init().req_seq_no()

        self.in_headers = {'referer': 'in.mideaepayuat.com'}
        # 生成外部退款号
        self.out_refund_no = data_init().serial_no()
        self.out_trade_time = data_init().token_time()
        # 生成out_trade_no
        self.out_trade_no = data_init().serial_Bath_no()  # 总商户订单号
        self.sub_out_trade_no_1 = data_init().serial_Sub_no()  # 子商户订单号1
        self.sub_out_trade_no_2 = data_init().serial_Sub_no()  # 子商户订单号2
        self.elasticjob_url = {"elasticjob_url": "http://10.16.157.96:20814"}

    def V3_alipay_scan_code(self, send_data):

        send_data.update({'req_seq_no': self.req_seq_no})
        send_data.update({'out_trade_no': self.out_trade_no})
        send_data.update({'out_trade_time': self.out_trade_time})
        send_data.update({'is_guarantee': str(send_data["is_guarantee"]).upper()})
        send_data.update({'is_virtual_product': str(send_data["is_virtual_product"]).upper()})
        # send_data.update({'profit_sharing': str(send_data["profit_sharing"]).upper()})
        send_data["sub_orders"][0]["sub_out_trade_no"] = self.sub_out_trade_no_1
        send_data["sub_orders"][1]["sub_out_trade_no"] = self.sub_out_trade_no_2
        send_data["sub_orders"] = self.sub_orders(send_data)
        sign = data_init().get_sign_no_sort(send_data)
        send_data["sign"] = sign

        print("send_data", send_data)

        r = requests.post(self.url["B2C_trade_url"], send_data, verify=False)

        print("返回", r.json())
        print("子单1", self.sub_out_trade_no_1)
        print("子单2", self.sub_out_trade_no_2)

        # #
        # # 查询支付总单
        res = OperationMysql("db_order").query(
            'SELECT pay_total_no FROM db_order.t_trade WHERE out_trade_no="%s"' % self.sub_out_trade_no_1)
        pay_total_no = res[0]["pay_total_no"]
        #
        # # # 更新银行接口流水为支付成功
        OperationMysql("db_bank").update(
            'UPDATE db_bank.t_ebank_tran SET pay_status=1 WHERE pay_total_no="%s"' % pay_total_no)
        # # # 触发定时任务，更新支付流水为成功，交易订单状态为已到账
        # # elasticjob(self.url, "paycore-repair-job").jobTrigger("payRepairProducerJob")
        time.sleep(200)
        self.sub_out_trade_no_1 = "TestSubBatch2021110715544778"

        pay_total_no = self.get_pay_total_no(self.sub_out_trade_no_1)
        return r.json(), self.sub_out_trade_no_1, self.sub_out_trade_no_2, pay_total_no

    # @Author: linxy57
    # @Date : 2021-12-20
    # @Desc : 托管交易-合单-下单
    def escrow_trade_batch_pay(self, send_data):
        send_data.update({'req_seq_no': self.req_seq_no})
        send_data.update({'out_trade_no': self.out_trade_no})
        send_data.update({'out_trade_time': self.out_trade_time})
        send_data.update({'is_guarantee': str(send_data["is_guarantee"]).upper()})
        send_data.update({'is_virtual_product': str(send_data["is_virtual_product"]).upper()})

        total_amount = int(send_data["sub_orders"][0]["pay_amount"]) + int(send_data["sub_orders"][1]["pay_amount"])
        send_data.update({'total_order_amount': total_amount})
        send_data.update({'total_amount': total_amount})

        sub_order = send_data["sub_orders"][0]
        sub_order.update({'sub_out_trade_no': self.sub_out_trade_no_1})
        sub_order2 = send_data["sub_orders"][1]
        sub_order2.update({'sub_out_trade_no': self.sub_out_trade_no_2})
        # 获取外部订单号
        out_trade_no_01 = sub_order["sub_out_trade_no"]
        partner = sub_order["partner"]
        sub_order_list = []
        sub_order_list.append(sub_order)
        sub_order_list.append(sub_order2)
        json_sub_orders = json.dumps(sub_order_list, ensure_ascii=False)
        send_data["sub_orders"] = json_sub_orders
        # 获取下单签名
        sign = data_init().get_sign_no_sort(send_data)
        send_data["sign"] = sign
        # 进行下单
        pay_result = requests.post(self.url["B2C_trade_url"], data=send_data, verify=False)
        result_code = pay_result.json()['result_code']
        # 断言下单结果是否为成功，成功才往下执行
        if result_code == '1001':
            return pay_result.json(), out_trade_no_01, partner
        else:
            raise RuntimeError('支付下单失败，交易订单号：%s' % out_trade_no_01)

    # @Author: linxy57
    # @Date : 2021-11-15
    # @Desc : 托管交易-合单-支付成功
    def escrow_trade_batch_pay_success(self, send_data):
        pay_result, out_trade_no, partner = EscrowTradeBatchAlipay(self.url).escrow_trade_batch_pay(send_data)
        # 查询交易订单
        trade_detail = OperationDbOrder().query_trade_detail(out_trade_no, partner)
        trade_no = trade_detail["trade_no"]
        # 支付总单号
        pay_total_no = trade_detail["pay_total_no"]
        pay_total_detail = OperationDbEscrowTrade().query_pay_total_order(pay_total_no)
        trade_inner_id = pay_total_detail["trade_inner_id"]
        # 托管交易收款流水号
        receive_pay_flow_no = pay_total_no + '-' + str(trade_inner_id) + '-' + '01'
        # 检查托管交易收款流水内部状态
        check_result = EscrowTradeCheck().check_receive_pay_flow(trade_no, receive_pay_flow_no)
        if check_result == True:
            time.sleep(2)
            # 查询托管交易总单是否资金已到账
            pay_total_detail = OperationDbEscrowTrade().query_pay_total_order(pay_total_no)
            pay_total_pay_status = pay_total_detail['pay_status']
            pay_total_inner_status = pay_total_detail['pay_inner_status']
            loop_count = 0
            while (pay_total_pay_status != 3 or pay_total_inner_status != 1) and loop_count < 10:
                time.sleep(2)
                pay_total_detail = OperationDbEscrowTrade().query_pay_total_order(pay_total_no)
                pay_total_pay_status = pay_total_detail['pay_status']
                pay_total_inner_status = pay_total_detail['pay_inner_status']
                loop_count += 1
            if loop_count == 10:
                raise RuntimeError('总单到账状态异常，总单号为：%s' % pay_total_no)
            # 订单是否资金已到账
            trade_detail = OperationDbOrder().query_trade_detail(out_trade_no, partner)
            trade_status = trade_detail['trade_status']
            arrival_status = trade_detail['arrival_status']
            loop_count = 0
            while (trade_status != 3 or arrival_status != 1) and loop_count < 10:
                time.sleep(2)
                trade_detail = OperationDbOrder().query_trade_detail(out_trade_no, partner)
                trade_status = trade_detail['trade_status']
                arrival_status = trade_detail['arrival_status']
                loop_count += 1
            if loop_count == 10:
                raise RuntimeError('订单到账状态异常，订单号为：%s' % trade_no)
            return trade_detail, pay_total_detail

    # @Author: linxy57
    # @Date : 2021-11-15
    # @Desc : 托管交易-合单-资金已到账
    def escrow_trade_batch_pay_arrival(self, send_data):
        total_count = send_data["total_count"]
        pay_result, out_trade_no, partner = EscrowTradeBatchAlipay(self.url).escrow_trade_batch_pay(send_data)
        # 查询交易订单
        trade_detail = OperationDbOrder().query_trade_detail(out_trade_no, partner)
        trade_no = trade_detail["trade_no"]
        main_trade_no = trade_detail["main_trade_no"]
        # 支付总单号
        pay_total_no = trade_detail["pay_total_no"]
        pay_total_detail = OperationDbEscrowTrade().query_pay_total_order(pay_total_no)
        trade_inner_id = pay_total_detail["trade_inner_id"]
        # 托管交易收款流水号
        receive_pay_flow_no = pay_total_no + '-' + str(trade_inner_id) + '-' + '01'
        # 检查托管交易收款流水内部状态
        check_result = EscrowTradeCheck().check_receive_pay_flow(trade_no, receive_pay_flow_no)
        assert check_result == True
        pay_time = (datetime.datetime.now() + datetime.timedelta(days=-1)).strftime("%Y-%m-%d %H:%M:%S")
        OperationDbOrder().update_pay_time_by_main_trade_no(main_trade_no, pay_time)
        # 插入对账数据，模拟对账单入库
        OperationDbCheckrecord().insert_escrow_channel_trade_detail(main_trade_no)
        # 触发escrow-trade-job:网银对账单补单任务，第一笔收款流水更新为资金已到账
        elasticjob(self.elasticjob_url, "escrow-trade-job").jobTrigger("arriveRepairProducerJob")
        # dubbo().RepairTradeFacade_arriveRepairForOnlinePay_dubbo(receive_pay_flow_no)
        time.sleep(5)
        for i in range(1, total_count+1):
            # 分账流水号
            profit_pay_flow_no = pay_total_no + '-' + str(trade_inner_id) + '-' + str(i+1).zfill(2)
            # 检查托管交易分账流水内部状态
            check_result = EscrowTradeCheck().check_profit_pay_flow(trade_no, profit_pay_flow_no)
            assert check_result == True
            # 等待第二笔托管交易流水内部状态为渠道受理成功，插入模拟安心户加款sql
            OperationDbEscrowChannel().insert_reverse_tran(profit_pay_flow_no)
            # 触发escrow-channel-task-schedule-job:线下收款任务
            elasticjob(self.elasticjob_url, "escrow-channe-task-schedule-job").jobTrigger("ReverseAccountingJob")
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
                print(loop_count)
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
        # @Date : 2021-12-19
        # @Desc : 托管支付宝APP-即时到账-合单

    def V3_alipay_trade_app(self, send_data):
        send_data.update({'req_seq_no': self.req_seq_number})
        send_data.update({'out_trade_no': self.out_trade_no})
        send_data.update({'out_trade_time': self.out_trade_time})
        send_data.update({'is_guarantee': str(send_data["is_guarantee"]).upper()})
        send_data.update({'is_virtual_product': str(send_data["is_virtual_product"]).upper()})
        send_data["sub_orders"][0]["sub_out_trade_no"] = self.sub_out_trade_no_1
        send_data["sub_orders"][1]["sub_out_trade_no"] = self.sub_out_trade_no_2
        total_count = send_data["total_count"]

        # market_amount = int(send_data["sub_orders"][0]["market_amount"]) + int(
        #     send_data["sub_orders"][1]["market_amount"])
        total_amount = int(send_data["sub_orders"][0]["pay_amount"]) + int(send_data["sub_orders"][1]["pay_amount"])
        # # total_order_amount = market_amount + total_amount
        send_data.update({'total_order_amount': total_amount})
        send_data.update({'total_amount': total_amount})
        # 获取外部订单号
        out_trade_no_01 = send_data["sub_orders"][0]["sub_out_trade_no"]
        partner = send_data["sub_orders"][0]["partner"]

        sub_order_list = []
        sub_order = send_data["sub_orders"][0]
        sub_order2 = send_data["sub_orders"][1]
        sub_order_list.append(sub_order)
        sub_order_list.append(sub_order2)
        json_sub_orders = json.dumps(sub_order_list, ensure_ascii=False)
        send_data["sub_orders"] = json_sub_orders
        # 获取下单签名
        sign = data_init().get_sign_no_sort(send_data)
        send_data["sign"] = sign
        # 进行下单
        pay_result = requests.post(self.url["B2C_trade_url"], data=send_data, verify=False)
        result_code = pay_result.json()['result_code']
        assert result_code == '1001'
        # 查询交易订单
        trade_detail = OperationDbOrder().query_trade_detail(out_trade_no_01, partner)
        trade_no = trade_detail["trade_no"]
        main_trade_no = trade_detail["main_trade_no"]
        # 支付总单号
        pay_total_no = trade_detail["pay_total_no"]
        pay_total_detail = OperationDbEscrowTrade().query_pay_total_order(pay_total_no)
        trade_inner_id = pay_total_detail["trade_inner_id"]
        # 托管交易收款流水号
        receive_pay_flow_no = pay_total_no + '-' + str(trade_inner_id) + '-' + '01'
        # 检查托管交易收款流水内部状态
        check_result = EscrowTradeCheck().check_receive_pay_flow(trade_no, receive_pay_flow_no)
        assert check_result == True
        # 插入对账数据，模拟对账单入库
        OperationDbCheckrecord().insert_escrow_channel_trade_detail(main_trade_no)
        # 触发escrow-trade-job:网银对账单补单任务，第一笔收款流水更新为资金已到账
        # elasticjob(self.elasticjob_url, "escrow-trade-job").jobTrigger("arriveRepairProducerJob")
        dubbo().RepairTradeFacade_arriveRepairForOnlinePay_dubbo(receive_pay_flow_no)
        time.sleep(5)
        for i in range(1, total_count + 1):
            # 分账流水号
            profit_pay_flow_no = pay_total_no + '-' + str(trade_inner_id) + '-' + str(i + 1).zfill(2)
            # 检查托管交易分账流水内部状态
            check_result = EscrowTradeCheck().check_profit_pay_flow(trade_no, profit_pay_flow_no)
            assert check_result == True
            # 等待第二笔托管交易流水内部状态为渠道受理成功，插入模拟安心户加款sql
            OperationDbEscrowChannel().insert_reverse_tran(profit_pay_flow_no)
            # 触发escrow-channel-task-schedule-job:线下收款任务
            elasticjob(self.elasticjob_url, "escrow-channe-task-schedule-job").jobTrigger("ReverseAccountingJob")
            time.sleep(5)
            profit_pay_flow_list = OperationDbEscrowTrade().query_trade_flow(profit_pay_flow_no)
            profit_pay_inner_status = profit_pay_flow_list['pay_inner_status']
            loop_count = 0
            while profit_pay_inner_status != 8 and loop_count < 10:
                time.sleep(10)
                profit_pay_flow_list = OperationDbEscrowTrade().query_trade_flow(profit_pay_flow_no)
                profit_pay_inner_status = profit_pay_flow_list['pay_inner_status']
                loop_count += 1
            if loop_count == 10:
                raise RuntimeError('到账状态异常')
        # 查询托管交易总单是否资金已到账
        pay_total_order_detail = OperationDbEscrowTrade().query_pay_total_order(pay_total_no)
        pay_total_pay_status = pay_total_order_detail['pay_status']
        pay_total_inner_status = pay_total_order_detail['pay_inner_status']
        if pay_total_pay_status != 3 or pay_total_inner_status != 5:
            raise RuntimeError('总单到账状态异常')
        # 订单是否资金已到账
        trade_detail = OperationDbOrder().query_trade_detail(out_trade_no_01, partner)
        trade_status = trade_detail['trade_status']
        arrival_status = trade_detail['arrival_status']
        if trade_status != 3 or arrival_status != 3:
            raise RuntimeError('订单到账状态异常')
        return pay_result.json(), trade_detail, pay_total_order_detail

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



