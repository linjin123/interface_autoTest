#!/usr/bin/env python 
# -*- coding: utf-8 -*- 
# @File : conftest.py 
# @Author: xiangling
# @Date : 2018-10-11 
# @Desc :
import os, sys
import pytest

BASE_DIR = os.path.dirname(os.path.realpath(__file__))
root_path = os.path.abspath(os.path.join(BASE_DIR, "../../.."))
sys.path.append(root_path)

from common.test_url import test_url


# from simple_settings import settings
# from funpinpin_api.util.para import action


# 让pytest认识--settings参数
def pytest_addoption(parser):
    parser.addoption('--settings', action='store')


@pytest.fixture(scope='session')
def settings(request):
    return request.config.getoption("--settings")


# ==================url==========================================
url = test_url()
# 商户接入url
partnerin_url = url.in_url
# PC收银台url
cashier_url = url.cashier_url
# 个人端url
personal_url = url.www_url
# H5钱包url
mobile_url = url.m_url
elasticjob_url = url.elasticjob_url

# ===============B2C交易查询接口=================================
B2C_trade_query_url = partnerin_url + '/trade/b2cTradeQuery.htm'

# ===============B2C交易==========================================
# B2C交易接入收银台接口(H5、PC收银台)
B2C_trade_url = partnerin_url + '/gateway.htm'
# 获取si、pwdkey、salt地址（PC收银台）
GetPayPwdKey_url = cashier_url + '/getSaltOfPayPwd.json'
# 获取密码地址，需要替换personal-web下personal-control-3.2.3.jar（PC收银台）
Get_genPwd_url = personal_url + '/security/common/genPwd.htm'
# 支付地址（PC收银台）
Pay_url = cashier_url + '/directPay.json'
Pay_ebank_url = cashier_url + '/eBank.json'
# 注销（PC收银台）
Logout_url = cashier_url + '/logout.htm'
# 获取paykey地址(H5收银台)
Get_PayPwdKey_H5_url = mobile_url + '/common/getPayPwdKey.htm'
# 支付地址（H5收银台）
Pay_H5_url = mobile_url + '/mallPay/payAll.htm'

# ===================B2C交易退款=====================================
# B2C_refund_url= partnerin_url + '/trade/b2cRefund.htm'
B2C_refund_url = partnerin_url + '/gateway.htm'
# ===================B2C交易退款查单=====================================
B2C_refund_query_url = partnerin_url + '/trade/b2cRefundQuery.htm'

# 测试个人用户(登录名、密码、user_id)
test_user_1 = {'login_name': '18780030001', 'password': '112233', 'user_id': '900260007'}
# 测试商户(商户号、平台号)
test_partner_1 = {'partner': '1000011005', 'plat_id': '1'}

# 助贷支付地址
zhudai = 'http://m.mideaepayuat.com/getThirdCreditQuota.htm'

# 云闪付支付地址
mallCashier_url = 'https://m.mideaepayuat.com/mallCashierNew.htm?'
common_url = 'https://m.mideaepayuat.com/common/getCommonInfo.htm'
thirdCreditPayUrl = "https://m.mideaepayuat.com/cashier/thirdPlatPay.htm"

# 邮储数字人民币
ecny_ebank_url = 'https://cashier.mideaepayuat.com/escrow/eCnyPay/pay.json'

# conftest.py
@pytest.fixture(scope='session')
def zhudai():
    zhudai = 'http://m.mideaepayuat.com/getThirdCreditQuota.htm'
    print('获取到token:%s' % zhudai)
    return zhudai


# 获取URL
@pytest.fixture(scope='session')
def url_dict():
    url = {
        "B2C_trade_query_url": B2C_trade_query_url,
        "B2C_trade_url": B2C_trade_url,
        "GetPayPwdKey_url": GetPayPwdKey_url,
        "Get_genPwd_url": Get_genPwd_url,
        "Pay_url": Pay_url,
        "Logout_url": Logout_url,
        "B2C_refund_url": B2C_refund_url,
        "test_user_1": test_user_1,
        "test_partner_1": test_partner_1,
        "Pay_H5_url": Pay_H5_url,
        "Get_PayPwdKey_H5_url": Get_PayPwdKey_H5_url,
        "B2C_refund_query_url": B2C_refund_query_url,
        "elasticjob_url": elasticjob_url,
        "Pay_ebank_url": Pay_ebank_url,
        "thirdCreditPayUrl": thirdCreditPayUrl,
        "common_url": common_url,
        "mallCashier_url": mallCashier_url,
        "ecny_ebank_url": ecny_ebank_url

    }
    return url
