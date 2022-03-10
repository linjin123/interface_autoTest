#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File : test_pay_system_trade_refund.py
# @Author: xiongyc9
# @Date : 2021-12-15
# @Desc : 支付系统交易退款入口

import datetime
import os, sys
BASE_DIR = os.path.dirname(os.path.realpath(__file__))
root_path = os.path.abspath(os.path.join(BASE_DIR, "../.."))
sys.path.append(root_path)
import pytest
import allure
from common.logger import logger
from common.read_data import OperationYaml
from interface.common_service.Trade_Refund import Trade_Refund
from interface.common_service.Wechat_trade_single_pay import Wechat_trade_single_pay
from interface.common_service.Wechat_trade_batch_pay import Wechat_trade_batch_pay
from operationMysql.operation_db_order import OperationDbOrder
from operationMysql.operation_db_bank import OperationDbBank
from assert_collection.refund_assert import refund_assert
from operationMysql.operation_db_pay import OperationDbPay
from operationMysql.operation_db_act import OperationDbAct
from operationMysql.operation_db_bank import OperationDbBank
from operationMysql.operation_db_settle import OperationDbSettle
from time import sleep





trade_query_args_item = "send_data,except_value"  # 根据测试数据信息定义参数信息
B2C_trade_query_param, B2C_trade_query_desc = OperationYaml.getData("/test_data/pay_system_trade_refund_1.yml")


@pytest.mark.refund
@allure.feature('支付系统交易退款')
@pytest.mark.parametrize(trade_query_args_item, B2C_trade_query_param, ids=B2C_trade_query_desc)
@allure.story('支付已到账交易退款')
def test_trade_refund(send_data, except_value,url_dict):
    """
    Functions:
        退款入口
    scence 枚举如下
    on_trade_date  当天退款（D0及时到账，非D0及时到账，D0担保交易已确认已结算，非D0担保交易未确认收货，非D0担保交易已确认收货）
    un_D0_secured_next_date_no_settle 非D0担保交易隔天未结算
    un_D0_secured_next_date_settle 非D0担保交易隔天已结算
    un_D0_arrival_next_date_settle 非D0 及时到账隔天已结算
    D0_arrival_unconfirmed D0担保交易未确认收货

    """
    try:
        scence = except_value["scence"]
        guarantee_type = except_value["guarantee_type"]
        origi_arrival_status = except_value["origi_arrival_status"]

        # 根据配置中的三级业务类型查找到对应的交易订单
        if scence == 'on_trade_date':  #当天退款

            sysdate = datetime.date.today().strftime("%Y-%m-%d") + '%'
            order_trade = OperationDbOrder().query_trade_by_confirm_receive_status_no_market(except_value, sysdate)

        elif scence=="un_D0_secured_next_date_no_settle": #非D0担保交易隔天未结算
            sysdate = (datetime.date.today() + datetime.timedelta(days=-1)).strftime("%Y-%m-%d") + '%'
            order_trade = OperationDbOrder().query_trade_by_business_types_and_last_date_no_market(except_value,
                                                                                                   sysdate)
            settle_data=OperationDbSettle().query_user_id_by_login_name(order_trade["trade_no"])
            assert len(settle_data) <= 0
            logger.info("settle_data",settle_data)

        elif scence=="un_D0_secured_next_date_settle": #非D0担保交易隔天已结算
            sysdate = (datetime.date.today() + datetime.timedelta(days=-1)).strftime("%Y-%m-%d") + '%'
            order_trade = OperationDbOrder().query_trade_by_business_types_and_last_date_no_market(except_value,
                                                                                                   sysdate)

            settle_data = OperationDbSettle().query_user_id_by_login_name(order_trade["trade_no"])
            assert len(settle_data) > 0
            logger.info("settle_data", settle_data)

        elif scence=="un_D0_arrival_next_date_settle":  #非D0 及时到账隔天已结算

            sysdate = (datetime.date.today() + datetime.timedelta(days=-1)).strftime("%Y-%m-%d") + '%'
            order_trade = OperationDbOrder().query_trade_by_confirm_receive_status_no_market(except_value,sysdate)
            settle_data = OperationDbSettle().query_user_id_by_login_name(order_trade["trade_no"])
            assert len(settle_data) > 0
            logger.info("settle_data", settle_data)

        elif scence == 'D0_arrival_unconfirmed': #D0担保交易未确认收货
            # confirm_receive_status = 0
            sysdate = datetime.date.today().strftime("%Y-%m-%d") + '%'
            order_trade = OperationDbOrder().query_trade_by_confirm_receive_status_no_market(except_value, sysdate)

        logger.info("order_trade:%s" % order_trade)
        assert len(order_trade) >0
        #退款金额需小于剩余退款金额
        assert send_data["refund_amount"] <= order_trade["trade_amount"]-order_trade["have_refund_amount"]

        re = Trade_Refund()
        result = re.B2C_refund(send_data, order_trade)

        if scence == 'on_trade_date' or scence=="un_D0_secured_next_date_settle" or scence=="un_D0_arrival_next_date_settle":

            # 如果退款接口返回成功，才继续进行后续的校验操作，否则返回退款失败原因
            assert result["result_code"] == '1001'
            # 获取到退款的订单号refund_no
            sleep(1)
            #查询退款单
            refund_order=OperationDbOrder().query_refund_trade_by_refund_no(result["refund_no"])
            logger.info("refund_order:%s"%refund_order)
            #修改退款单渠道流水为成功
            OperationDbBank().update_bank_tran_by_pay_total_no(refund_order["refund_pay_no"])
            #触发退款补单job
            re.update_bank_pay_status_success(url_dict)
            #再次查询渠道流水支付状态，未支付成功时修改为支付成功，再次出发退款补单job
            res=OperationDbBank().query_bank_tran_by_pay_total_no(refund_order["refund_pay_no"])
            if res["pay_status"] !=1:
                # 修改退款单渠道流水为成功
                OperationDbBank().update_bank_tran_by_pay_total_no(refund_order["refund_pay_no"])
                # 触发退款补单job
                re.update_bank_pay_status_success(url_dict)
            sleep(300)
            #查询补单后的退款单
            refund_order = OperationDbOrder().query_refund_trade_by_refund_no(result["refund_no"])
            logger.info("退款下单成功后的操作")
            logger.info("支付系统退款校验")

            refund_assert().assert_pay(result)  # 接口校验
            refund_assert().assert_order(refund_order, send_data, order_trade)  # 退款订单校验
            refund_assert().assert_act_history(refund_order["refund_pay_no"], send_data)  # 退款财务流水校验
            refund_assert().assert_pay_total(except_value, send_data, result["refund_no"],
                                             order_trade)  # 退款总单校验
            refund_assert().assert_notify(send_data, result["refund_no"])  # 退款通知校验

        # D0 担保交易未确认收货退款
        elif scence == 'D0_arrival_unconfirmed':
            assert result["result_code"] == '110350142'
            assert result["result_info"] == 'D0结算担保交易未确认收货不允许退款'

        # 非D0担保确认收货隔日未结算退款
        elif scence == 'un_D0_secured_next_date_no_settle':
            assert result["result_code"] == '110350133'
            assert result["result_info"] == '无结算订单记录，无法退款'


    except RuntimeError as err:
        logger.error(err)
        raise











