#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File : confirm_receive.py
# @Author: xiongyc9
# @Date : 2021-12-2
# @Desc : 担保交易-确认收货下单

import sys
from common.common_util import data_init
import requests
from collections import OrderedDict
from common.logger import logger
import json
from common.read_data import OperationYaml
from operationMysql.operation_db_order import OperationDbOrder
import time


class ConfirmReceive(object):

    def __init__(self, url_dict):
        self.url = url_dict
        self.req_seq_no = data_init().req_seq_no()

    # 确认收货下单接口
    def confirm_receive(self, partner, out_trade_no):
        """
        Functions:
            1.担保交易确认收货下单接口，涵盖单笔和合单交易，合单交易也是一笔一笔的确认收货
            2.单笔交易确认收货传入partner,out_trade_no
            3.合单交易确认收货，则需要对每笔子单进行确认收货，传入子单的partner,out_trade_no
        Parameters:
            partner: 商户号，如果是合单，则传入子单交易的的商户号
            out_trade_no: 交易外部订单号，如果是合单，则传入子单交易的外部订单号
        Return:
            result: 如果确认收货成功，返回确认收货下单成功的json结果，否则返回None，打印不能确认收货的提示信息
        """

        # 获取配置文件中确认收货下单接口的send_data数据
        confirm_receive_data, _ = OperationYaml.getData \
            ("/test_data/01_B2C_trade_data/confirm-receive.yml")
        confirm_receive_send_data = confirm_receive_data[0][0]

        # 将req_seq_no放入confirm_receive_send_data
        confirm_receive_send_data.update({'req_seq_no': self.req_seq_no})
        # 将partner放入confirm_receive_send_data
        confirm_receive_send_data.update({'partner': partner})
        # 将out_trade_no放入confirm_receive_send_data
        confirm_receive_send_data.update({'out_trade_no': out_trade_no})
        # 获取签名，并放入confirm_receive_send_data
        confirm_receive_send_data["sign"] = data_init().get_sign_no_sort(confirm_receive_send_data)
        # time.sleep(30)

        order_result = OperationDbOrder().query_trade_detail(out_trade_no, partner)
        trade_status = order_result["trade_status"]

        # 确保订单已经支付成功后才进行确认收货下单
        loop_count = 1
        while trade_status != 3:  # 3:支付成功
            time.sleep(5)
            order_result = OperationDbOrder().query_trade_detail(out_trade_no, partner)
            trade_status = order_result["trade_status"]
            loop_count += 1
            if loop_count > 30:
                raise RuntimeError("订单未支付成功")

        # 发起确认收货下单请求
        r = requests.post(self.url["B2C_trade_url"], confirm_receive_send_data, verify=False)
        result = r.json()
        # 如果确认收货成功，返回接口数据，否则返回确认收货失败的提示信息
        if result["result_code"] == '1001':
            return result
        else:
            logger.error(result["result_info"])
            return None


if __name__ == '__main__':
    pass
