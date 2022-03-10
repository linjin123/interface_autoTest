#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: linxy57
# @Date : 2021-11-11
# @Desc : 托管支付宝APP交易-即时到账
import logging

import allure
import pytest
import datetime
from common.logger import logger
from common.read_data import OperationYaml
from interface.common_service.escrow_trade_single_alipay import EscrowTradeSingleAlipay
from interface.common_service.escrow_trade_batch_alipay import EscrowTradeBatchAlipay
from assert_collection.trade_pay_assert import TradePayAssert
from operationMysql.operation_db_order import OperationDbOrder

Alipay_escrow_trade_args_item = "send_data,except_value"  # 根据测试数据信息定义参数信息
Alipay_escrow_trade_param, Alipay_escrow_trade_desc = OperationYaml.getData(
    "/test_data/05_V3_Alipay_data/alipay-escrow-trade-app-single-immediately.yml")


# ****************************单笔及时到账-支付成功***********************************
@pytest.mark.pay
@allure.feature('111383_托管支付宝APP')
@pytest.mark.parametrize(Alipay_escrow_trade_args_item, Alipay_escrow_trade_param, ids=Alipay_escrow_trade_desc)
@allure.story('B2C交易_托管支付宝APP支付_单笔即时到账_支付成功')
def test_alipay_app_single_immediately_pay_success(send_data, except_value, url_dict):
    try:
        trade_detail = EscrowTradeSingleAlipay(url_dict).escrow_trade_single_pay_success(send_data)
        logger.info('订单号为：%s' % trade_detail["trade_no"])
    except RuntimeError as e:
        logger.error(e)
        raise RuntimeError


# ****************************单笔及时到账-支付成功-修改交易时间***********************************
@pytest.mark.pay
@allure.feature('111383_托管支付宝APP')
@pytest.mark.parametrize(Alipay_escrow_trade_args_item, Alipay_escrow_trade_param, ids=Alipay_escrow_trade_desc)
@allure.story('B2C交易_托管支付宝APP支付_单笔即时到账_支付成功后修改交易时间')
def test_alipay_app_single_immediately_change_pay_time(send_data, except_value, url_dict):
    try:
        trade_detail = EscrowTradeSingleAlipay(url_dict).escrow_trade_single_pay_success(send_data)
        trade_no = trade_detail["trade_no"]
        pay_time = (datetime.datetime.now() + datetime.timedelta(days=-1)).strftime("%Y-%m-%d %H:%M:%S")
        OperationDbOrder().update_pay_time_by_trade_no(trade_no, pay_time)
        logger.info('订单号为：%s' % trade_detail["trade_no"])
    except RuntimeError as e:
        logger.error(e)
        raise RuntimeError


# ****************************单笔及时到账-资金已到账***********************************
@pytest.mark.pay
@allure.feature('111383_托管支付宝APP')
@pytest.mark.parametrize(Alipay_escrow_trade_args_item, Alipay_escrow_trade_param, ids=Alipay_escrow_trade_desc)
@allure.story('B2C交易_托管支付宝APP支付_单笔即时到账_资金已到账')
def test_alipay_app_single_immediately_arrival(send_data, except_value, url_dict):
    try:
        trade_detail, pay_total_order_detail = EscrowTradeSingleAlipay(url_dict).escrow_trade_single_pay_arrival(
            send_data)
        # 交易订单信息校验
        TradePayAssert().assert_order_detail(send_data, except_value, trade_detail)
        pay_total_no = pay_total_order_detail["trade_no"]
        # 托管交易总单校验
        TradePayAssert().assert_pay_total(send_data, except_value, pay_total_no)
        # 托管交易收款流水校验
        TradePayAssert().assert_receive_pay_flow(send_data, except_value, pay_total_no)
        # 托管交易分账流水校验
        TradePayAssert().assert_profit_pay_flow(send_data, except_value, pay_total_no)
        # 托管交易账务流水校验
        TradePayAssert().assert_act_history(send_data, pay_total_no)
        # 外部通知校验
        TradePayAssert().assert_notify(send_data, except_value, trade_detail)
        logger.info('订单号为：%s' % trade_detail["trade_no"])
    except RuntimeError as e:
        logger.error(e)
        raise RuntimeError


# ****************************合单即时到账-支付成功***********************************
Alipay_escrow_trade_param, Alipay_escrow_trade_desc = OperationYaml.getData(
    "/test_data/05_V3_Alipay_data/alipay-escrow-trade-app-batch-immediately.yml")
@pytest.mark.pay
@allure.feature('111383_托管支付宝APP')
@pytest.mark.parametrize(Alipay_escrow_trade_args_item, Alipay_escrow_trade_param, ids=Alipay_escrow_trade_desc)
@allure.story('B2C交易_托管支付宝APP支付_合单即时到账_支付成功')
def test_alipay_app_batch_immediately_pay_success(send_data, except_value, url_dict):
    try:
        trade_detail, pay_total_detail = EscrowTradeBatchAlipay(url_dict).escrow_trade_batch_pay_success(send_data)
        logger.info('订单号为：%s' % trade_detail["trade_no"])
    except RuntimeError as e:
        logger.error(e)
        raise RuntimeError



# ****************************合单即时到账-支付成功，修改交易时间************************
Alipay_escrow_trade_param, Alipay_escrow_trade_desc = OperationYaml.getData(
    "/test_data/05_V3_Alipay_data/alipay-escrow-trade-app-batch-immediately.yml")
@pytest.mark.pay
@allure.feature('111383_托管支付宝APP')
@pytest.mark.parametrize(Alipay_escrow_trade_args_item, Alipay_escrow_trade_param, ids=Alipay_escrow_trade_desc)
@allure.story('B2C交易_托管支付宝APP支付_合单即时到账_支付成功修改交易时间')
def test_alipay_app_batch_immediately_change_pay_time(send_data, except_value, url_dict):
    try:
        trade_detail, pay_total_detail = EscrowTradeBatchAlipay(url_dict).escrow_trade_batch_pay_success(send_data)
        main_trade_no = trade_detail["main_trade_no"]
        pay_time = (datetime.datetime.now() + datetime.timedelta(days=-1)).strftime("%Y-%m-%d %H:%M:%S")
        OperationDbOrder().update_pay_time_by_main_trade_no(main_trade_no, pay_time)
        logger.info('订单号为：%s' % trade_detail["trade_no"])
    except RuntimeError as e:
        logger.error(e)
        raise RuntimeError



# ****************************合单即时到账-资金已到账*********************************
Alipay_escrow_trade_param, Alipay_escrow_trade_desc = OperationYaml.getData(
    "/test_data/05_V3_Alipay_data/alipay-escrow-trade-app-batch-immediately.yml")
@pytest.mark.pay
@allure.feature('111383_托管支付宝APP')
@pytest.mark.parametrize(Alipay_escrow_trade_args_item, Alipay_escrow_trade_param, ids=Alipay_escrow_trade_desc)
@allure.story('B2C交易_托管支付宝APP支付_合单即时到账_资金已到账')
def test_alipay_app_batch_immediately_arrival(send_data, except_value, url_dict):
    try:
        trade_detail, pay_total_detail = EscrowTradeBatchAlipay(url_dict).escrow_trade_batch_pay_arrival(
            send_data)
        # 交易订单信息校验
        TradePayAssert().assert_order_detail(send_data, except_value, trade_detail)
        pay_total_no = pay_total_detail["trade_no"]
        # 托管交易总单校验
        TradePayAssert().assert_pay_total(send_data, except_value, pay_total_no)
        # 托管交易收款流水校验
        TradePayAssert().assert_receive_pay_flow(send_data, except_value, pay_total_no)
        # 托管交易分账流水校验
        TradePayAssert().assert_profit_pay_flow(send_data, except_value, pay_total_no)
        # 托管交易账务流水校验
        TradePayAssert().assert_act_history(send_data, pay_total_no)
        # 外部通知校验
        TradePayAssert().assert_notify(send_data, except_value, trade_detail)
        logger.info('订单号为：%s' % trade_detail["trade_no"])
    except RuntimeError as e:
        logger.error(e)
        raise RuntimeError
