#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: ex_zhangjf11
# @Date : 2022-03-10
# @Desc :  签约（支付宝）

import logging

import allure
import pytest
from common.logger import logger
from common.read_data import OperationYaml
from interface.common_service.signing_without_secret_withholding import ContractingPublicMethod



#免密代扣-支付宝签约接口

Alipay_signing_parameters, Alipay_contract_expectations = OperationYaml.getData(
    "/test_data/wechatAndAlipaySecretFreeWhithhold/trade_alipay_withhold_sign.yml")


# ****************************免密代扣-微信签约-正常流程***********************************
@pytest.mark.pay
@pytest.mark.parametrize("send_data","except_value",Alipay_signing_parameters)
def test_alipay_signed_success(send_data, except_value, url_dict):
    try:
        data = ContractingPublicMethod(url_dict).alipay_signed(send_data)

    except RuntimeError as e:
        logger.error(e)
        raise RuntimeError