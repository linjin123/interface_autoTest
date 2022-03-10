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
from common.logger import logger

class close_refund_assert(object):



    def assert_inner_refund(self, inner_refund_result,send_data,except_value,trade_detail):
        logger.info("inner_refund_result:%s  ,type is :%s " % (inner_refund_result,type(inner_refund_result)))
        logger.info("trade_detail:%s,type is :%s "% (trade_detail,type(trade_detail)))

        assert inner_refund_result["partner"] == str(send_data['partner'])
        assert inner_refund_result["refund_channel"] == 2
        assert inner_refund_result["refund_type"] == 1
        assert inner_refund_result["business_types"] == str(except_value["business_type1"])+str(except_value["business_type2"])+str(except_value["business_type3"])
        assert inner_refund_result["origi_pay_channel"] == 2
        assert inner_refund_result["origi_pay_total_no"] ==trade_detail["pay_total_no"]
        assert inner_refund_result["refund_amount"] ==send_data["pay_amount"]
        assert inner_refund_result["cur_type"] == "156"
        assert inner_refund_result["plat_id"] ==int(trade_detail["plat_id"])
        assert int(inner_refund_result["plat_partner"]) ==int(trade_detail["plat_partner"])
        assert inner_refund_result["pay_status"] == 3
        # assert inner_refund_result["arrival_status"] == 3


