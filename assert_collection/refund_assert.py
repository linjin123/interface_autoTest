#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File : B2C_trade_01.py
# @Author: xiangling
# @Date : 2021-11-9
# @Desc :B2C交易接入收银台

import pytest
from common.common_db import OperationMysql
from common.get_data import get_data
from operationMysql.operation_db_act import OperationDbAct
from operationMysql.operation_db_pay import OperationDbPay
from operationMysql.operation_db_order import OperationDbOrder
from operationMysql.operation_db_partner_notify import OperationDbPartnerNotify
import json


class refund_assert(object):

    # 支付总单、支付流水校验

    def assert_pay(self, result):
        assert result["refund_status"] == "PAYING"
        assert result["result_info"] == "成功"

    # 支付
    def assert_pay_total(self, except_value, send_data, refund_trade_no, trade):

        pay_total_result = OperationDbPay().query_pay_total_by_trade_no(refund_trade_no)  # 退款支付总单
        rele_pay_total_result = OperationDbPay().query_origi_pay_total_by_trade_no(trade["trade_no"])  # 原支付总单
        # 检查关联单号类型1 B2C  2充值 3 提现 4  转账 5退款 6结算
        assert pay_total_result["rele_order_type"] == 5
        # 获取三级业务类型
        business_types = str(except_value["business_type1"]) + str(except_value["business_type2"]) + str(
            except_value["business_type3"])
        assert pay_total_result["business_types"] == business_types
        # 检查付款方
        assert pay_total_result["payer_login_act"] == send_data["partner"]
        # 检查收款方
        print("pay_total_result", pay_total_result["payee_login_act"])
        print("rele_pay_total_result", rele_pay_total_result["payee_login_act"])
        assert pay_total_result["payee_login_act"] == rele_pay_total_result["payee_login_act"]
        # 检查支付来源1  纯余额    2  纯快捷  3  纯网银 4  快捷余额混合支付  5  网银余额混合支付
        # assert pay_total_result["pay_source"] == except_value["pay_source"]
        # 检查支付金额
        assert pay_total_result["amount"] == send_data["refund_amount"]
        # 检查支付状态   TODO：2：支付中，待解决
        # assert pay_total_result["pay_status"] == 3
        # 检查支付内部状态：1  有效  2  正常 3审批通过 4审批拒绝
        assert pay_total_result["pay_inner_status"] == 3
        # # 检查绑卡序列号
        # assert pay_total_result["bind_no"] == pay_data["bindNo"]

    # 订单校验
    # def assert_order(self, send_data, refund_data, trade):

    def assert_order(self, refund_data,send_data,  trade):
        origi_trade_indo = OperationDbOrder().query_trade_detail_by_trade_no(trade["trade_no"])

        assert refund_data["refund_amount"] == send_data["refund_total_amount"]
        # assert refund_data["market_amount"] == send_data["refund_market_amount"]
        assert refund_data["pay_amount"] == send_data["refund_amount"]
        assert refund_data["arrival_status"] == 3  #todo 已到账更新状态
        assert refund_data["refund_status"] == 3
        assert refund_data["inner_status"] == 1
        assert refund_data["refund_amount"] == origi_trade_indo["have_refund_amount"]

    # 账务流水校验
    def assert_act_history(self, pay_no, send_data):


        act_historys = OperationDbAct().get_act_history(str(pay_no))

        for act_history in act_historys:
            if act_history["pay_flow_type"]:
                if act_history["pay_flow_type"] == "64":
                    if act_history["dc_type"] == 2:
                        assert act_history["tran_amount"] == send_data["refund_amount"]
                        assert act_history["inner_remark"] == "减少余额"
                        assert act_history["trade_msg"] == "交易【退款】"
                    elif act_history["dc_type"] == 1:
                        assert act_history["tran_amount"] == send_data["refund_amount"]
                        assert act_history["inner_remark"] == "增加余额"
                        assert act_history["trade_msg"] == "退款至余额"

                elif act_history["pay_flow_type"] == "7":
                    if act_history["dc_type"] == 2:
                        assert act_history["tran_amount"] == send_data["refund_amount"]
                        assert act_history["inner_remark"] == "增加余额"
                        assert act_history["trade_msg"] == "退款【提现】"
                    elif act_history["dc_type"] == 1:
                        assert act_history["tran_amount"] == send_data["refund_amount"]
                        assert act_history["inner_remark"] == "减少余额"
                        assert act_history["trade_msg"] == "交易【退款】"

                elif act_history["pay_flow_type"] == "8":
                    if act_history["dc_type"] == 2:
                        assert act_history["tran_amount"] == send_data["refund_amount"]
                        assert act_history["inner_remark"] == "减少余额"
                        assert act_history["trade_msg"] == "交易【退款】"

                elif act_history["pay_flow_type"] == "10":
                    if act_history["dc_type"] == 2:
                        assert act_history["tran_amount"] == send_data["refund_amount"]
                        assert act_history["inner_remark"] == "增加余额"
                        assert act_history["trade_msg"] == "退款【提现】"
                    elif act_history["dc_type"] == 1:
                        assert act_history["tran_amount"] == send_data["refund_amount"]
                        assert act_history["inner_remark"] == "减少余额"
                        assert act_history["trade_msg"] == "交易【退款】"

                elif act_history["pay_flow_type"] == "69":
                    if act_history["dc_type"] == 2:
                        assert act_history["tran_amount"] == send_data["refund_amount"]
                        assert act_history["inner_remark"] == "减少余额"
                        assert act_history["trade_msg"] == "交易【退款】"
                    elif act_history["dc_type"] == 1:
                        assert act_history["tran_amount"] == send_data["refund_amount"]
                        assert act_history["inner_remark"] == "增加余额"
                        assert act_history["trade_msg"] == "退款至余额"

                elif act_history["pay_flow_type"] == "22":
                    if act_history["dc_type"] == 2:
                        assert act_history["tran_amount"] == send_data["refund_amount"]
                        assert act_history["inner_remark"] == "增加余额"
                        assert act_history["trade_msg"] == "退款【提现】"
                    elif act_history["dc_type"] == 1:
                        assert act_history["tran_amount"] == send_data["refund_amount"]
                        assert act_history["inner_remark"] == "减少余额"
                        assert act_history["trade_msg"] == "交易【退款】"

                elif act_history["pay_flow_type"] == "20":
                    if act_history["dc_type"] == 1:
                        assert act_history["tran_amount"] == send_data["refund_amount"]
                        assert act_history["inner_remark"] == "减少余额"
                        assert act_history["trade_msg"] == "交易【退款】"
            else:
                continue

    # 通知校验
    def assert_notify(self, send_data, refund_no):

        # 获取商户外部通知数据
        notify_datas = OperationDbPartnerNotify().query_out_notify_list_by_trade_no(refund_no)
        for notify_data in notify_datas:
            if notify_data["order_type"] == 6:

                # 获取商户外部通知数据中的content内容
                notify_content = json.loads(notify_data["content"])
                # 判断通知接收者是否为支付时的收款商户
                assert notify_data["remark"] == "内转成功通知"
                assert notify_data["receiver"] == send_data["partner"]
                # 判断通知地址是否为支付时的notify_url
                assert notify_data["notify_url"] == send_data["notify_url"]
                # 判断通知的订单号是否为传入的交易单号
                assert notify_data["order_no"] == refund_no
                # 判断通知内容中的商户是否为支付时传入的商户
                assert notify_content["partner"] == send_data["partner"]
                # 判断通知内容中的退款金额是否为一致
                assert notify_content["refund_amount"] == str(send_data["refund_amount"])
                # assert notify_content["refund_market_amount"] == str(send_data["refund_market_amount"])
                assert notify_content["refund_total_amount"] == str(send_data["refund_total_amount"])
                assert notify_content["refund_no"] == str(refund_no)
                assert notify_content["refund_status_info"] == "退款成功"
            elif notify_data["order_type"] == 14:
                # 获取商户外部通知数据中的content内容
                notify_content = json.loads(notify_data["content"])
                # 判断通知接收者是否为支付时的收款商户
                assert notify_data["remark"] == "退款到账通知"
                assert notify_data["receiver"] == send_data["partner"]
                # 判断通知地址是否为支付时的notify_url
                assert notify_data["notify_url"] == send_data["notify_url"]
                # 判断通知的订单号是否为传入的交易单号
                assert notify_data["order_no"] == refund_no
                # 判断通知内容中的商户是否为支付时传入的商户
                assert notify_content["partner"] == send_data["partner"]
                # 判断通知内容中的退款金额是否为一致
                assert notify_content["refund_amount"] == str(send_data["refund_amount"])
                # assert notify_content["refund_market_amount"] == str(send_data["refund_market_amount"])
                assert notify_content["refund_total_amount"] == str(send_data["refund_total_amount"])
                assert notify_content["refund_no"] == str(refund_no)
                assert notify_content["refund_status_info"] == "退款成功"
