#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File : test_escrow_system_trade_refund.py
# @Author: xiongyc9
# @Date : 2021-12-15
# @Desc : 托管系统交易退款入口

import os, sys
import datetime
import pytest
import allure
from common.logger import logger
from common.read_data import OperationYaml
from operationMysql.operation_db_order import OperationDbOrder
from assert_collection.trade_pay_refund_assert import TradePayRefundAssert
from interface.common_service.escrow_trade_refund import EscrowTradeRefund

BASE_DIR = os.path.dirname(os.path.realpath(__file__))
root_path = os.path.abspath(os.path.join(BASE_DIR, "../.."))
sys.path.append(root_path)
trade_query_args_item = "send_data,except_value"  # 根据测试数据信息定义参数信息
B2C_trade_query_param, B2C_trade_query_desc = OperationYaml.getData("/test_data/escrow_system_trade_refund1.yml")
@pytest.mark.refund
@allure.feature('托管系统交易退款')
@pytest.mark.parametrize(trade_query_args_item, B2C_trade_query_param, ids=B2C_trade_query_desc)
@allure.story('托管交易退款')
@pytest.mark.run(order=-1)
def test_trade_refund(send_data, except_value):
    """
    Functions:
        托管退款入口
    """
    try:
        scence = except_value["scence"]
        guarantee_type = except_value["guarantee_type"]
        origi_arrival_status = except_value["origi_arrival_status"]
        confirm_receive_status = 0
        # 交易当天退款
        if scence == 'on_trade_date':
            sysdate = datetime.date.today().strftime("%Y-%m-%d") + '%'
            trade_detail = OperationDbOrder().query_trade_by_business_types_no_market(except_value, sysdate,
                                                                                      confirm_receive_status)

            if trade_detail:
                refund_detail, refund_pay_total_detail = EscrowTradeRefund().escrow_trade_refund_on_trade_date(
                    send_data,
                    trade_detail)
                # 退款订单信息断言
                TradePayRefundAssert().assert_refund_order(send_data, except_value, refund_detail)
                # 退款支付总单断言
                TradePayRefundAssert().assert_refund_total(send_data, except_value, refund_pay_total_detail)
                # 退款付款流水断言
                TradePayRefundAssert().assert_channel_refund_flow(send_data, except_value, refund_pay_total_detail)
                logger.info(refund_detail["refund_no"])
            else:
                raise RuntimeError('不存在符合条件的交易订单。')
        # 未确认收货退款
        elif scence == 'arrival_unconfirmed':
            sysdate = (datetime.date.today() + datetime.timedelta(days=-1)).strftime("%Y-%m-%d") + '%'
            trade_detail = OperationDbOrder().query_trade_by_business_types_no_market(except_value, sysdate,
                                                                                      confirm_receive_status)
            if trade_detail:
                refund_detail, refund_pay_total_detail = EscrowTradeRefund().escrow_trade_refund_arrival_guarantee(
                    send_data, trade_detail)
                # 退款订单信息断言
                TradePayRefundAssert().assert_refund_order(send_data, except_value, refund_detail)
                # 退款支付总单断言
                TradePayRefundAssert().assert_refund_total(send_data, except_value, refund_pay_total_detail)
                # 退款付款流水断言
                TradePayRefundAssert().assert_escrow_pay_flow(send_data, except_value, refund_pay_total_detail)
                # 退款渠道退款流水断言
                TradePayRefundAssert().assert_channel_refund_flow(send_data, except_value, refund_pay_total_detail)
                # 退款账务流水断言
                TradePayRefundAssert().assert_act_history(send_data, refund_pay_total_detail)
                # 退款外部通知断言
                TradePayRefundAssert().assert_notify(send_data, refund_detail)
                logger.info(refund_detail["refund_no"])
            else:
                raise RuntimeError('不存在符合条件的交易订单。')
        # 未到账跨天退款/到账退款-即时到账
        elif scence == 'common':
            sysdate = (datetime.date.today() + datetime.timedelta(days=-1)).strftime("%Y-%m-%d") + '%'
            # 已确认收货退款-担保交易
            if guarantee_type == 1 and origi_arrival_status == 3:
                confirm_receive_status = 1
            trade_detail = OperationDbOrder().query_trade_by_business_types_no_market(except_value, sysdate,
                                                                                      confirm_receive_status)
            if trade_detail:
                refund_detail, result_info = EscrowTradeRefund().escrow_trade_refund_common(send_data, trade_detail)
                if refund_detail:
                    logger.info(refund_detail["refund_no"])
                else:
                    logger.info(result_info)
            else:
                raise RuntimeError('不存在符合条件的交易订单。')
        else:
            raise RuntimeError('except_value参数有误。')
    except RuntimeError as e:
        logger.error(e)
        raise RuntimeError
