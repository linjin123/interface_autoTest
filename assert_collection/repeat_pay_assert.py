#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File : B2C_trade_01.py
# @Author: xiongyc9
# @Date : 2021-12-17
# @Desc : 重复支付的支付流水断言、财务流水断言

import time
import ast
import json
from common.common_db import OperationMysql
from operationMysql.operation_db_pay import OperationDbPay
from operationMysql.operation_db_order import OperationDbOrder
from operationMysql.operation_db_bank import OperationDbBank
import json
from common.logger import logger
from operationMysql.operation_db_act import OperationDbAct
from operationMysql.operation_db_user import OperationDbUser
from operationMysql.operation_db_order import OperationDbOrder
from operationMysql.operation_db_bank_act import OperationDbBankAct
from operationMysql.operation_db_partner_notify import OperationDbPartnerNotify


class pay_assert:
    """
    Desc:支付断言，包括支付总单，支付流水校验、订单校验、三方账务流水校验、通知校验
    """
    def assert_pay_flow(self, send_data, pay_data, except_value, trade_no):
        order_result = OperationDbOrder().query_trade_detail_by_trade_no(trade_no)
        pay_total_no = order_result["pay_total_no"]
        pay_flow = OperationDbPay().query_pay_flow_by_trade_no(pay_total_no)
        # 校验支付流水数量
        assert len(pay_flow) == 2
        pay_flow_no = pay_flow[0]["pay_flow_no"][-2:]
        if pay_flow_no == "01":
            pay_flow1 = pay_flow[0]
            pay_flow2 = pay_flow[1]
        elif pay_flow_no == "02":
            pay_flow2 = pay_flow[0]
            pay_flow1 = pay_flow[1]
        else:
            logger.info("支付流水号有误！")

        # 校验流水1
        assert pay_flow1["pay_flow_no"][0:22] == pay_total_no
        assert pay_flow1["pay_inner_id"] == 100
        # 获取渠道流水号
        tran_no = OperationDbBank().query_tran_no_by_pay_flow_no(pay_flow1["pay_flow_no"])
        assert pay_flow1["pos_no"] == tran_no["tran_no"]
        assert pay_flow1["payee_login_act"] == send_data["payer_login_name"]
        assert pay_flow1["payee_act_type"] == 10  # 现金账户
        assert pay_flow1["pay_source"] == except_value["pay_source"]
        # assert pay_type校验
        business_types = str(except_value["business_type1"]) + str(except_value["business_type2"]) \
                         + str(except_value["business_type3"])
        assert pay_flow1["business_types"] == business_types
        assert pay_flow1["amount"] == send_data["pay_amount"]
        assert pay_flow1["pay_status"] == 3  # 支付成功
        assert pay_flow1["pay_inner_status"] == 1
        assert pay_flow1["need_risk"] == 1  # 是否需要风控 1  需要  2  不需要
        assert pay_flow1["have_refund_amount"] == 0
        assert pay_flow1["pay_time"] != ""
        assert pay_flow1["create_time"] != ""
        assert pay_flow1["modify_time"] != ""
        # 校验流水2
        assert pay_flow2["pay_flow_no"][0:22] == pay_total_no
        assert pay_flow2["pay_inner_id"] == 100
        assert pay_flow2["payer_login_act"] == send_data["payer_login_name"]
        assert pay_flow2["payee_login_act"] == send_data["partner"]
        assert pay_flow2["payee_inner_id"] == int(send_data["partner"])
        assert pay_flow2["payer_act_type"] == 10  # 现金账户
        assert pay_flow2["payee_act_type"] == 11  # 交易账户
        assert pay_flow2["pay_source"] == except_value["pay_source"]
        assert pay_flow2["business_types"] == business_types
        assert pay_flow2["amount"] == send_data["pay_amount"]
        assert pay_flow2["pay_status"] == 3  # 支付成功
        assert pay_flow2["pay_inner_status"] == 1
        assert pay_flow2["need_risk"] == 1  # 是否需要风控 1  需要  2  不需要
        assert pay_flow2["have_refund_amount"] == 0
        assert pay_flow2["pay_time"] != ""
        assert pay_flow2["create_time"] != ""
        assert pay_flow2["modify_time"] != ""

    def assert_act_history(self, send_data, pay_data, except_value, trade_no):
        pass


