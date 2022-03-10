#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File : B2C_trade_01.py
# @Author: xiangling
# @Date : 2021-11-9
# @Desc :支付断言，包括支付总单，支付流水校验、订单校验、三方账务流水校验、通知校验

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

    # 支付总单校验
    def assert_pay_total(self, send_data, pay_data, except_value, trade_no):
        """
        Functions:
            1.支付系统的支付总单校验，涵盖单笔合单交易，以及担保和及时到账交易
        Parameters:
            send_data: 支付发起时发送的参数数据
            pay_data: 支付数据，配置文件中pay_data内容
            except_value: 期望值，配置文件中except_value内容
            trade_no:如果是单笔交易，传入该交易的订单号；如果是合单交易，传入任意一笔子单的订单号
        Returns:
            None: 无返回值
        Raises:
            暂无
        """

        # 合单交易会有必填的sub_orders字段，以此判断是否是合单交易，合单和单笔交易走不同逻辑
        if "sub_orders" in send_data.keys():
            is_batch = 'TRUE'
        else:
            is_batch = 'FALSE'

        # 根据交易订单号获取数据库中的支付总单数据
        pay_total_result = OperationDbPay().query_pay_total_by_trade_no(trade_no)
        # 检查关联单号类型：1 B2C ， 2充值， 3提现， 4转账， 5退款， 6结算
        assert pay_total_result["rele_order_type"] == except_value["rele_order_type"]
        # 获取三级业务类型
        business_types = str(except_value["business_type1"]) + str(except_value["business_type2"]) + str(
            except_value["business_type3"])
        assert pay_total_result["business_types"] == business_types

        '''
        检查付款方，付款方根据不同的交易类型不同，所以需要做判断
        这里先判断是快速交易还是普通交易，ordinaryOrQuickTrade=1为普通交易，ordinaryOrQuickTrade=2为快速交易
        如果是普通交易，付款方为具体支付时登录的账号或者登录账号对应的商户号，如果是快速交易，付款方为中间商户
        '''
        if pay_total_result["ordinaryOrQuickTrade"] == 2:
            assert len(pay_total_result["payer_login_act"]) == 10
        # 检查收款方
        assert pay_total_result["payee_login_act"] == send_data["partner"]
        # 检查支付来源：1纯余额 ，   2纯快捷 ， 3纯网银， 4快捷余额混合支付，  5 网银余额混合支付
        assert pay_total_result["pay_source"] == except_value["pay_source"]
        # 检查支付金额，如果是合单交易，金额为子单金额总和
        if is_batch == 'TRUE':
            total_amount = 0
            for i in json.loads(send_data["sub_orders"]):
                total_amount += int(i["pay_amount"])
            assert pay_total_result["amount"] == total_amount
        else:
            assert pay_total_result["amount"] == send_data["pay_amount"]
        # 检查支付状态
        assert pay_total_result["pay_status"] == 3
        # 检查支付内部状态：1有效， 2正常， 3审批通过， 4审批拒绝
        assert pay_total_result["pay_inner_status"] == 9
        # 检查绑卡序列号
        if pay_total_result["bind_no"] is not None:
            assert pay_total_result["bind_no"] == pay_data["bindNo"]

    # 支付流水单校验
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
        if tran_no is not None:
            assert pay_flow1["pos_no"] == tran_no["tran_no"]
        # assert pay_flow1["payee_login_act"] == send_data["payer_login_name"]
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
        # assert pay_flow2["payer_login_act"] == send_data["payer_login_name"]
        assert pay_flow2["payee_login_act"] == send_data["partner"]
        assert pay_flow2["payee_inner_id"] == int(send_data["partner"])
        assert pay_flow2["payer_act_type"] == 10  # 现金账户
        if send_data["is_guarantee"] == 'FALSE':
            assert pay_flow2["payee_act_type"] == 11  # 交易账户
        else:
            assert pay_flow2["payee_act_type"] == 18  # 交易账户
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

    # 订单校验
    def assert_order(self, send_data, pay_data, except_value, trade_no, out_trade_no):
        order_result = OperationDbOrder().query_trade_detail_by_trade_no(trade_no)
        pay_total_result = OperationDbPay().query_pay_total_by_trade_no(trade_no)
        # 检查商户订单号
        assert order_result["out_trade_no"] == out_trade_no
        # 检查商户号
        assert order_result["partner"] == send_data["partner"]
        # 检查商户号
        assert order_result["partner_id"] == int(send_data["partner"])
        # 检查付款方账号
        assert order_result["buyer_loginno"] == send_data["payer_login_name"]
        # 检查商品名称
        assert order_result["good_name"] == send_data["product_name"]
        # 检查商品描述
        assert order_result["body"] == send_data["product_info"]
        # 检查总订单金额
        assert order_result["trade_amount"] == send_data["pay_amount"] + send_data["market_amount"]
        # 检查订单状态
        assert order_result["trade_status"] == 3
        # 检查内部订单状态
        assert order_result["order_inner_status"] == 5
        # 检查订单金额
        assert order_result["pay_amount"] == send_data["pay_amount"]
        # 支付总单号
        assert order_result["pay_total_no"] == pay_total_result["pay_total_no"]
        # 检查
        risk_params = json.loads(send_data["risk_params"])
        assert order_result["source_ip"] == risk_params["ip"]
        # 检查goods_type
        # 检查即时到账 0  担保交易 1
        if send_data["is_guarantee"] == 'FALSE':
            assert order_result["guarantee_type"] == 0
        elif send_data["is_guarantee"] == 'TRUE':
            assert order_result["guarantee_type"] == 1
        # 检查产品标识product_type
        # 检查是否是营销订单
        # 检查营销金额
        assert order_result["market_amount"] == send_data["market_amount"]
        # 检查营销商户
        assert order_result["market_partner"] == send_data["market_acc_partner"]
        # 检查三级业务类型
        assert order_result["business_type1"] == except_value["business_type1"]
        assert order_result["business_type2"] == except_value["business_type2"]
        assert order_result["business_type3"] == except_value["business_type3"]
        # 检查支付渠道:1 支付系统 2 托管系统
        assert order_result["pay_channel"] == except_value["pay_channel"]
        # 检查到账状态：
        assert order_result["arrival_status"] == 3

    # 三方账务流水校验
    def assert_act_history(self, send_data, pay_data, except_value, trade_no):
        """
        Functions:
            1.支付方式的支付渠道为支付系统的财务流水断言，涵盖单笔合单交易，以及担保和及时到账交易
            2.个人余额/商户余额三笔流水：中间账户充值、收款账户收款、中间账户付款
            3.其他三方支付四笔流水：支付账户付款、中间商户收款、中间账户付款、收款账户收款
            4.配置文件中except_value中要添加对应的key/value：
                act_history_add_balance:"增加余额"
                act_history_subtract_balance:"减少余额"
                act_history_charge_type:"交易【充值】"
                act_history_payer_type:"交易【付款】"
                act_history_payee_type:"交易【收款】"
        Parameters:
            send_data: 支付发起时发送的参数数据
            pay_data: 支付数据，配置文件中pay_data内容
            except_value: 期望值，配置文件中except_value内容
            trade_no:如果是单笔交易，传入该交易的订单号；如果是合单交易，传入任意一笔子单的订单号
        Returns:
            None: 无返回值
        Raises:
            暂无
        """

        # 合单交易会有必填的sub_orders字段，以此判断是否是合单交易，合单和单笔交易走不同逻辑
        if "sub_orders" in send_data.keys():
            is_batch = 'TRUE'
        else:
            is_batch = 'FALSE'

        # 用于判断是个人余额/商户余额，还是其他的三方支付方式
        pay_way = pay_data["payType"]
        if is_batch == 'FALSE':
            # 单笔交易，且非个人余额/商户余额，则调用非个人余额/商户余额财务流水断言方法
            if pay_way != 1:
                self.assert_act_history_single_other(send_data, except_value, trade_no, pay_data)
            # 单笔交易，且是个人余额/商户余额，则调用个人余额/商户余额财务流水断言方法
            else:
                self.assert_act_history_single_balance(send_data, except_value, trade_no, pay_data)

        else:
            # 合单交易，且非个人余额/商户余额，则调用非个人余额/商户余额财务流水断言方法
            if pay_way != 1:
                self.assert_act_history_batch_other(send_data, except_value, trade_no, pay_data)
            # 合单交易，且是个人余额/商户余额，则调用个人余额/商户余额财务流水断言方法
            else:
                self.assert_act_history_batch_balance(send_data, except_value, trade_no, pay_data)



    # 三方财务流水校验-单笔-个人余额/商户余额
    def assert_act_history_single_balance(self, send_data, except_value, trade_no, pay_data=None):
        """
        Functions:
            1.三方财务流水校验-单笔-个人余额/商户余额
            2.个人余额/商户余额四笔流水：支付账户付款、中间商户收款、中间账户付款、收款账户收款
        Parameters:
            send_data: 支付发起时发送的参数数据
            pay_data: 支付数据，配置文件中pay_data内容
            except_value: 期望值，配置文件中except_value内容
            trade_no: 单笔交易的订单号
        Returns:
            None: 无返回值
        Raises:
            RuntimeError：获取财务流水数据异常！
        """

        # 用于判断是否是担保交易，担保交易is_guarantee=TRUE,即时到账交易is_guarantee=FALSE
        is_guarantee = send_data["is_guarantee"]
        payee_user_id = send_data["partner"]
        # 根据订单号查询支付总单号
        pay_total_no = OperationDbOrder().query_pay_total_no_by_trade_no(trade_no)

        # 根据支付总单号查询财务流水数据，并按pay_flow_no升序
        act_history = OperationDbAct().query_act_history_by_pay_total_no(pay_total_no)
        run_count = 1
        # 循环判断是否获取到外部通知数据，只有获取到数据之后才会进行后续操作
        while act_history is None:
            time.sleep(5)
            act_history = OperationDbAct().query_act_history_by_pay_total_no(pay_total_no)
            run_count += 1
            if run_count > 20:
                raise RuntimeError('获取财务流水数据异常！')

        act_history_length = len(act_history)

        # 个人余额/商户余额支付：依次校验每笔财务流水
        for i in range(act_history_length):
            # 按pay_flow_no排序第一二笔为支付账户到中间账户的收付款流水
            if i <= 1:
                # 借贷类型dc_type=1为借，dc_type=2为贷
                if act_history[i]["dc_type"] == 1:
                    # 断言支付账户付款到中间账户流水的用户id、账户类型、交易金额、借贷类型、用户展示备注、交易信息
                    assert act_history[i]["act_type"] == 10
                    assert act_history[i]["tran_amount"] == int(send_data["pay_amount"])
                    assert act_history[i]["dc_type"] == 1
                    assert act_history[i]["user_remark"] == except_value["act_history_subtract_balance"]
                    assert act_history[i]["trade_msg"] == except_value["act_history_payer_type"]

                elif act_history[i]["dc_type"] == 2:
                    # 断言中间账户收款支付账户流水的用户id、账户类型、交易金额、借贷类型、用户展示备注、交易信息
                    assert act_history[i]["act_type"] == 10
                    assert act_history[i]["tran_amount"] == int(send_data["pay_amount"])
                    assert act_history[i]["dc_type"] == 2
                    assert act_history[i]["user_remark"] == except_value["act_history_add_balance"]
                    assert act_history[i]["trade_msg"] == except_value["act_history_payee_type"]
            # 按pay_flow_no排序第三、四笔为支中间账户付款给收款账户的收付款流水
            if i > 1:
                if act_history[i]["dc_type"] == 1:
                    # 断言中间账户付款到收款账户的付款流水的用户id、账户类型、交易金额、借贷类型、用户展示备注、交易信息
                    assert act_history[i]["act_type"] == 10
                    assert act_history[i]["tran_amount"] == int(send_data["pay_amount"])
                    assert act_history[i]["dc_type"] == 1
                    assert act_history[i]["user_remark"] == except_value["act_history_subtract_balance"]
                    assert act_history[i]["trade_msg"] == except_value["act_history_payer_type"]

                elif act_history[i]["dc_type"] == 2:
                    # 断言收款商户收取中间账户的收款流水的用户id、账户类型、交易金额、借贷类型、用户展示备注、交易信息
                    assert act_history[i]["user_id"] == int(payee_user_id)
                    if is_guarantee == "FALSE":
                        # 即时到账交易支付，收款方的交易账户增加金额
                        assert act_history[i]["act_type"] == 11
                    else:
                        # 担保交易支付，收款方的担保账户增加金额
                        assert act_history[i]["act_type"] == 18
                    assert act_history[i]["tran_amount"] == int(send_data["pay_amount"])
                    assert act_history[i]["dc_type"] == 2
                    assert act_history[i]["user_remark"] == except_value["act_history_add_balance"]
                    assert act_history[i]["trade_msg"] == except_value["act_history_payee_type"]

    # 三方财务流水校验-单笔-其他非个人余额/商户余额支付
    def assert_act_history_single_other(self, send_data, except_value, trade_no, pay_data=None):
        """
        Functions:
            1.三方财务流水校验-单笔-他非个人余额/商户余额支付
            2.非个人余额/商户余额的三方支付三笔流水：中间账户充值、收款账户收款、中间账户付款
        Parameters:
            send_data: 支付发起时发送的参数数据
            pay_data: 支付数据，配置文件中pay_data内容
            except_value: 期望值，配置文件中except_value内容
            trade_no: 单笔交易的订单号
        Returns:
            None: 无返回值
        Raises:
            RuntimeError：获取财务流水数据异常！
        """

        # 用于判断是否是担保交易
        is_guarantee = send_data["is_guarantee"]
        payee_user_id = send_data["partner"]
        # 根据订单号查询支付总单号
        pay_total_no = OperationDbOrder().query_pay_total_no_by_trade_no(trade_no)

        # 根据支付总单号查询财务流水，并按pay_flow_no升序
        act_history = OperationDbAct().query_act_history_by_pay_total_no(pay_total_no)
        run_count = 1
        # 循环判断是否获取到外部通知数据，只有获取到数据之后才会进行后续操作
        while act_history is None:
            time.sleep(5)
            act_history = OperationDbAct().query_act_history_by_pay_total_no(pay_total_no)
            run_count += 1
            if run_count > 20:
                raise RuntimeError('获取财务流水数据异常！')

        act_history_length = len(act_history)

        # 根据支付总单号查询银行账户流水，充值流水校验
        bank_act_history = OperationDbBankAct().query_bank_act_by_pay_total_no(pay_total_no)

        # 非个人余额/商户余额的其他三方支付
        for i in range(act_history_length):
            # 中间账户充值流水校验，按pay_flow_no升序，第一笔为充值流水
            if i == 0:
                # 断言充值流水的用户id、账户类型、交易金额、借贷类型、用户展示备注、交易信息
                assert act_history[i]["act_type"] == 10
                assert act_history[i]["tran_amount"] == int(send_data["pay_amount"])
                assert act_history[i]["dc_type"] == 2
                assert act_history[i]["user_remark"] == except_value["act_history_add_balance"]
                assert act_history[i]["trade_msg"] == except_value["act_history_charge_type"]

                # 断言银行账户流水的借贷类型、交易金额、内部展示信息、交易信息
                assert bank_act_history[0]["dc_type"] == 1
                assert bank_act_history[0]["tran_amount"] == int(send_data["pay_amount"])
                assert bank_act_history[0]["inner_remark"] == except_value["act_history_add_balance"]
                assert bank_act_history[0]["trade_msg"] == except_value["act_history_charge_type"]

            # 付款流水校验
            elif act_history[i]["dc_type"] == 1:
                # 断言付款流水的用户id、账户类型、交易金额、借贷类型、用户展示备注、交易信息
                assert act_history[i]["act_type"] == 10
                assert act_history[i]["tran_amount"] == int(send_data["pay_amount"])
                assert act_history[i]["dc_type"] == 1
                assert act_history[i]["user_remark"] == except_value["act_history_subtract_balance"]
                assert act_history[i]["trade_msg"] == except_value["act_history_payer_type"]
            # 收款流水校验
            elif act_history[i]["dc_type"] == 2:
                # 断言收款流水的用户id、账户类型、交易金额、借贷类型、用户展示备注、交易信息
                assert act_history[i]["user_id"] == int(payee_user_id)
                if is_guarantee == "FALSE":
                    # 即时到账交易支付，收款方的交易账户增加金额
                    assert act_history[i]["act_type"] == 11
                else:
                    # 担保交易支付，收款方的担保账户增加金额
                    assert act_history[i]["act_type"] == 18
                assert act_history[i]["tran_amount"] == int(send_data["pay_amount"])
                assert act_history[i]["dc_type"] == 2
                assert act_history[i]["user_remark"] == except_value["act_history_add_balance"]
                assert act_history[i]["trade_msg"] == except_value["act_history_payee_type"]

    # 三方账务流水校验-合单-个人余额/商户余额
    def assert_act_history_batch_balance(self, send_data, except_value, trade_no, pay_data=None):
        """
        Functions:
            1.三方财务流水校验-合单-个人余额/商户余额
            2.个人余额/商户余额四笔流水：支付账户付款、中间商户收款、中间账户付款、收款账户收款
        Parameters:
            send_data: 支付发起时发送的参数数据
            pay_data: 支付数据，配置文件中pay_data内容
            except_value: 期望值，配置文件中except_value内容
            trade_no: 合单交易中任意一笔子单的订单号
        Returns:
            None: 无返回值
        Raises:
            RuntimeError：获取财务流水数据异常！
        """

        is_guarantee = send_data["is_guarantee"]
        payee_user_id = send_data["partner"]

        # 根据订单号查询支付总单号
        pay_total_no = OperationDbOrder().query_pay_total_no_by_trade_no(trade_no)

        # 根据支付总单号查询财务流水
        act_history = OperationDbAct().query_act_history_by_pay_total_no(pay_total_no)
        run_count = 1
        # 循环判断是否获取到外部通知数据，只有获取到数据之后才会进行后续操作
        while act_history is None:
            time.sleep(5)
            act_history = OperationDbAct().query_act_history_by_pay_total_no(pay_total_no)
            run_count += 1
            if run_count > 20:
                raise RuntimeError('获取财务流水数据异常！')

        # 根据总单号查询pay_flow_no
        pay_flow_no = OperationDbPay().query_pay_flow_no_by_pay_total_no(pay_total_no)
        pay_flow_no_length = len(pay_flow_no)

        # 如果是个人余额/商户余额支付
        for i in range(pay_flow_no_length):
            # 支付账户付款到中间账户的收付款流水校验
            if i == 0:
                # 如果第一笔是付款流水
                if act_history[i]["dc_type"] == 1:
                    # 断言支付账户付款到中间账户付款流水的用户id、账户类型、交易金额、借贷类型、用户展示备注、交易信息
                    assert act_history[i]["act_type"] == 10
                    assert act_history[i]["tran_amount"] == int(send_data["total_amount"])
                    assert act_history[i]["dc_type"] == 1
                    assert act_history[i]["user_remark"] == except_value["act_history_subtract_balance"]
                    assert act_history[i]["trade_msg"] == except_value["act_history_payer_type"]

                    # 断言中间账户收取支付账户的收款流水的用户id、账户类型、交易金额、借贷类型、用户展示备注、交易信息
                    assert act_history[i + 1]["act_type"] == 10
                    assert act_history[i + 1]["tran_amount"] == int(send_data["total_amount"])
                    assert act_history[i + 1]["dc_type"] == 2
                    assert act_history[i + 1]["user_remark"] == except_value["act_history_add_balance"]
                    assert act_history[i + 1]["trade_msg"] == except_value["act_history_payee_type"]
                # 如果第一笔是收款流水
                if act_history[i]["dc_type"] == 2:
                    # 断言中间账户收取支付账户的收款流水的用户id、账户类型、交易金额、借贷类型、用户展示备注、交易信息
                    assert act_history[i]["act_type"] == 10
                    assert act_history[i]["tran_amount"] == int(send_data["total_amount"])
                    assert act_history[i]["dc_type"] == 2
                    assert act_history[i]["user_remark"] == except_value["act_history_add_balance"]
                    assert act_history[i]["trade_msg"] == except_value["act_history_payee_type"]

                    # 断言支付账户付款到中间账户付款流水的用户id、账户类型、交易金额、借贷类型、用户展示备注、交易信息
                    assert act_history[i + 1]["act_type"] == 10
                    assert act_history[i + 1]["tran_amount"] == int(send_data["total_amount"])
                    assert act_history[i + 1]["dc_type"] == 1
                    assert act_history[i + 1]["user_remark"] == except_value[
                        "act_history_subtract_balance"]
                    assert act_history[i + 1]["trade_msg"] == except_value["act_history_payer_type"]

            # 子单：中间账户付款给收款商户的收付款流水校验
            else:
                # 如果第一笔是付款流水
                if act_history[2 * i]["dc_type"] == 1:
                    # 断言中间账户付款到收款账户的付款流水的用户id、账户类型、交易金额、借贷类型、用户展示备注、交易信息
                    assert act_history[2 * i]["act_type"] == 10
                    assert act_history[2 * i]["tran_amount"] == int(
                        json.loads(send_data["sub_orders"])[i - 1]["pay_amount"])
                    assert act_history[2 * i]["dc_type"] == 1
                    assert act_history[2 * i]["user_remark"] == except_value[
                        "act_history_subtract_balance"]
                    assert act_history[2 * i]["trade_msg"] == except_value["act_history_payer_type"]

                    # 断言收款商户收取中间商户的收款流水的用户id、账户类型、交易金额、借贷类型、用户展示备注、交易信息
                    if is_guarantee == "FALSE":
                        # 即时到账交易支付，收款方的交易账户增加金额
                        assert act_history[2 * i + 1]["act_type"] == 11
                    else:
                        # 担保交易支付，收款方的担保账户增加金额
                        assert act_history[2 * i + 1]["act_type"] == 18
                    assert act_history[2 * i + 1]["tran_amount"] == int(
                        json.loads(send_data["sub_orders"])[i - 1]["pay_amount"])
                    assert act_history[2 * i + 1]["dc_type"] == 2
                    assert act_history[2 * i + 1]["user_remark"] == except_value[
                        "act_history_add_balance"]
                    assert act_history[2 * i + 1]["trade_msg"] == except_value["act_history_payee_type"]
                # 如果第一笔是收款流水
                if act_history[2 * i]["dc_type"] == 2:
                    # 断言收款商户收取中间商户的收款流水的用户id、账户类型、交易金额、借贷类型、用户展示备注、交易信息
                    assert act_history[2 * i]["user_id"] == int(payee_user_id)
                    if is_guarantee == "FALSE":
                        # 即时到账交易支付，收款方的交易账户增加金额
                        assert act_history[2 * i]["act_type"] == 11
                    else:
                        # 担保交易支付，收款方的担保账户增加金额
                        assert act_history[2 * i]["act_type"] == 18
                    assert act_history[2 * i]["tran_amount"] == int(
                        json.loads(send_data["sub_orders"])[i - 1]["pay_amount"])
                    assert act_history[2 * i]["dc_type"] == 2
                    assert act_history[2 * i]["user_remark"] == except_value["act_history_add_balance"]
                    assert act_history[2 * i]["trade_msg"] == except_value["act_history_payee_type"]

                    # 断言中间账户付款到收款账户的付款流水的用户id、账户类型、交易金额、借贷类型、用户展示备注、交易信息
                    assert act_history[2 * i + 1]["act_type"] == 10
                    assert act_history[2 * i + 1]["tran_amount"] == int(
                        json.loads(send_data["sub_orders"])[i - 1]["pay_amount"])
                    assert act_history[2 * i + 1]["dc_type"] == 1
                    assert act_history[2 * i + 1]["user_remark"] == except_value[
                        "act_history_subtract_balance"]
                    assert act_history[2 * i + 1]["trade_msg"] == except_value["act_history_payer_type"]

    # 三方财务流水校验-合单-其他非个人余额/商户余额支付
    def assert_act_history_batch_other(self, send_data, except_value, trade_no, pay_data=None):
        """
        Functions:
            1.三方财务流水校验-合单-他非个人余额/商户余额支付
            2.非个人余额/商户余额的三方支付三笔流水：中间账户充值、收款账户收款、中间账户付款
        Parameters:
            send_data: 支付发起时发送的参数数据
            pay_data: 支付数据，配置文件中pay_data内容
            except_value: 期望值，配置文件中except_value内容
            trade_no: 合单交易中任意一笔子单的订单号
        Returns:
            None: 无返回值
        Raises:
            RuntimeError：获取财务流水数据异常！
        """

        is_guarantee = send_data["is_guarantee"]
        payee_user_id = send_data["partner"]
        # 根据登录名称查询用户ID

        # 根据订单号查询支付总单号
        pay_total_no = OperationDbOrder().query_pay_total_no_by_trade_no(trade_no)

        # 根据支付总单号查询财务流水
        act_history = OperationDbAct().query_act_history_by_pay_total_no(pay_total_no)
        run_count = 1
        # 循环判断是否获取到外部通知数据，只有获取到数据之后才会进行后续操作
        while act_history is None:
            time.sleep(5)
            act_history = OperationDbAct().query_act_history_by_pay_total_no(pay_total_no)
            run_count += 1
            if run_count > 30:
                raise RuntimeError('获取财务流水数据异常！')

        # 根据支付总单号查询银行账户流水
        bank_act_history = OperationDbBankAct().query_bank_act_by_pay_total_no(pay_total_no)

        # 根据总单号查询pay_flow_no
        pay_flow_no = OperationDbPay().query_pay_flow_no_by_pay_total_no(pay_total_no)
        pay_flow_no_length = len(pay_flow_no)

        # 非个人余额/商户余额支付
        for i in range(pay_flow_no_length):
            # 充值流水校验，因为按pay_flow_no排序，第一笔就是充值流水
            if i == 0:
                # 断言充值流水的用户id、账户类型、交易金额、借贷类型、用户展示备注、交易信息
                assert act_history[i]["act_type"] == 10
                assert act_history[i]["tran_amount"] == int(send_data["total_amount"])
                assert act_history[i]["dc_type"] == 2
                assert act_history[i]["user_remark"] == except_value["act_history_add_balance"]
                assert act_history[i]["trade_msg"] == except_value["act_history_charge_type"]
                # 断言银行账户流水的借贷类型、交易金额、内部展示信息、交易信息
                assert bank_act_history[0]["dc_type"] == 1
                assert bank_act_history[0]["tran_amount"] == int(send_data["total_amount"])
                assert bank_act_history[0]["inner_remark"] == except_value["act_history_add_balance"]
                assert bank_act_history[0]["trade_msg"] == except_value["act_history_charge_type"]
            # 子单收付款流水校验，从第二笔账务流水往后
            else:
                # 因为收款和付款的流水不能确定付款先还是收款先，不确定
                # 如果对应的收付款流水中第一笔是付款流水
                if act_history[2 * i - 1]["dc_type"] == 1:
                    # 断言付款流水的用户id、账户类型、交易金额、借贷类型、用户展示备注、交易信息
                    assert act_history[2 * i - 1]["act_type"] == 10
                    assert act_history[2 * i - 1]["tran_amount"] == int(
                        json.loads(send_data["sub_orders"])[i - 1]["pay_amount"])
                    assert act_history[2 * i - 1]["dc_type"] == 1
                    assert act_history[2 * i - 1]["user_remark"] == except_value["act_history_subtract_balance"]
                    assert act_history[2 * i - 1]["trade_msg"] == except_value["act_history_payer_type"]

                    # 断言收款流水的用户id、账户类型、交易金额、借贷类型、用户展示备注、交易信息
                    assert act_history[2 * i]["user_id"] == int(payee_user_id)
                    if is_guarantee == "FALSE":
                        # 即时到账交易支付，收款方的交易账户增加金额
                        assert act_history[2 * i]["act_type"] == 11
                    else:
                        # 担保交易支付，收款方的担保账户增加金额
                        assert act_history[2 * i]["act_type"] == 18
                    assert act_history[2 * i]["tran_amount"] == int(
                        json.loads(send_data["sub_orders"])[i - 1]["pay_amount"])
                    assert act_history[2 * i]["dc_type"] == 2
                    assert act_history[2 * i]["user_remark"] == except_value["act_history_add_balance"]
                    assert act_history[2 * i]["trade_msg"] == except_value["act_history_payee_type"]
                # 如果对应的收付款流水中第一笔是收款流水
                if act_history[2 * i - 1]["dc_type"] == 2:
                    # 断言收款流水的用户id、账户类型、交易金额、借贷类型、用户展示备注、交易信息
                    assert act_history[2 * i - 1]["user_id"] == int(payee_user_id)
                    if is_guarantee == "FALSE":
                        # 即时到账交易支付，收款方的交易账户增加金额
                        assert act_history[2 * i - 1]["act_type"] == 11
                    else:
                        # 担保交易支付，收款方的担保账户增加金额
                        assert act_history[2 * i - 1]["act_type"] == 18
                    assert act_history[2 * i - 1]["tran_amount"] == int(
                        json.loads(send_data["sub_orders"])[i - 1]["pay_amount"])
                    assert act_history[2 * i - 1]["dc_type"] == 2
                    assert act_history[2 * i - 1]["user_remark"] == except_value["act_history_add_balance"]
                    assert act_history[2 * i - 1]["trade_msg"] == except_value["act_history_payee_type"]

                    # 断言付款流水的用户id、账户类型、交易金额、借贷类型、用户展示备注、交易信息
                    assert act_history[2 * i]["act_type"] == 10
                    assert act_history[2 * i]["tran_amount"] == int(
                        json.loads(send_data["sub_orders"])[i - 1]["pay_amount"])
                    assert act_history[2 * i]["dc_type"] == 1
                    assert act_history[2 * i]["user_remark"] == except_value["act_history_subtract_balance"]
                    assert act_history[2 * i]["trade_msg"] == except_value["act_history_payer_type"]

    # 通知校验
    def assert_notify(self, send_data, pay_data, except_value, trade_no):
        """
        Functions:
            商户外部通知校验，涵盖单笔合单交易，以及担保和即时到账交易
        Parameters:
            send_data: 支付发起时发送的参数数据
            pay_data: 支付数据，配置文件中pay_data内容
            except_value: 期望值，配置文件中except_value内容
            trade_no: 如果是单笔交易，传入该交易的订单号；如果是合单交易，传入任意一笔子单的订单号
        Returns:
            None: 无返回值
        Raises:
            暂无
        """


        # 先判断是否是合单交易,合单交易会有必填的sub_orders字段
        if "sub_orders" in send_data.keys():
            # 合单交易需要通过main_trade_no去查询外部通知数据
            main_trade_no = OperationDbOrder().query_main_trade_no_by_trade_no(trade_no)
            self.assert_notify_batch(send_data, except_value, main_trade_no, pay_data)
        else:
            # 单笔交易直接通过交易订单号trade_no查询外部通知数据
            self.assert_notify_single(send_data, except_value, trade_no, pay_data)



    # 单笔交易-通知校验
    def assert_notify_single(self, send_data, except_value, trade_no, pay_data=None):
        """
        Functions:
            单笔交易的通知校验
        Parameters:
            send_data: 支付发起时发送的参数数据
            pay_data: 支付数据，配置文件中pay_data内容
            except_value: 期望值，配置文件中except_value内容
            trade_no: 单笔交易，传入交易的订单号即可
        Returns:
            None: 无返回值
        Raises:
            RuntimeError：获取外部通知数据异常！
        """
        # 获取商户外部通知数据
        notify_data = OperationDbPartnerNotify().query_out_notify_by_trade_no(trade_no)
        run_count = 1
        # 循环判断是否获取到外部通知数据，只有获取到数据之后才会进行后续操作
        while notify_data is None:
            time.sleep(5)
            notify_data = OperationDbPartnerNotify().query_out_notify_by_trade_no(trade_no)
            run_count += 1
            if run_count > 20:
                raise RuntimeError('获取外部通知数据异常！')

        # 获取商户外部通知数据中的content内容,notify_content中所有字段都是字符串
        notify_content = json.loads(notify_data["content"])
        # 判断通知接收者是否为支付时的收款商户
        assert notify_data["receiver"] == str(send_data["partner"])
        # 判断通知地址是否为支付时的notify_url
        assert notify_data["notify_url"] == send_data["notify_url"]
        # 判断通知的订单号是否为传入的交易单号
        assert notify_data["order_no"] == trade_no
        # 获取三级业务类型
        business_types = str(except_value["business_type1"]) + str(except_value["business_type2"]) + str(
            except_value["business_type3"])
        # 判断通知内容中的三级业务类型是否正确
        assert notify_content["business_types"] == business_types
        # 判断通知内容中的商户是否为支付时传入的商户
        assert notify_content["partner"] == str(send_data["partner"])
        # 判断通知内容中的支付金额是否为支付时的金额
        assert notify_content["pay_amount"] == str(send_data["pay_amount"])
        # 判断通知内容中的担保交易标志是否与支付时一致
        assert notify_content["is_guarantee"] == send_data["is_guarantee"]
        # 支付时如果有营销金额，判断通知内容中的营销金额和营销账户是否与支付时一致
        if "market_amount" in send_data.keys():
            # 营销金额不为空的，判断营销金额和营销账户是否正确
            if send_data["market_amount"] is not None:
                assert notify_content["market_amount"] == str(send_data["market_amount"])
                assert notify_content["market_partner"] == str(send_data["market_acc_partner"])
            # 如果营销金额为空，通知内容中返回营销金额为0
            else:
                assert notify_content["market_amount"] == '0'

    # 合单交易-通知校验
    def assert_notify_batch(self, send_data, except_value, trade_no, pay_data=None):
        """
        Functions:
            合单交易的通知校验
        Parameters:
            send_data: 支付发起时发送的参数数据
            pay_data: 支付数据，配置文件中pay_data内容
            except_value: 期望值，配置文件中except_value内容
            trade_no: 合单交易，传入任意一笔子单的订单号即可
        Returns:
            None: 无返回值
        Raises:
            RuntimeError： 获取外部通知数据异常
        """
        # 获取商户外部通知数据
        notify_data = OperationDbPartnerNotify().query_out_notify_by_trade_no(trade_no)
        run_count = 1
        # 循环判断是否获取到外部通知数据，只有获取到数据之后才会进行后续操作
        while notify_data is None:
            time.sleep(5)
            notify_data = OperationDbPartnerNotify().query_out_notify_by_trade_no(trade_no)
            run_count += 1
            if run_count > 20:
                raise RuntimeError('获取外部通知数据异常！')
        # 获取商户外部通知数据中的content内容
        notify_content = json.loads(notify_data["content"])
        # 获取外部通知数据content中的子单信息
        sub_orders = json.loads(notify_content["sub_orders"])
        # 判断通知接收者是否为支付时的收款商户
        assert notify_data["receiver"] == str(send_data["partner"])
        # 判断通知地址是否为支付时的notify_url
        assert notify_data["notify_url"] == send_data["notify_url"]
        # 判断通知的订单号是否为传入的交易单号
        assert notify_data["order_no"] == trade_no
        # 获取三级业务类型
        business_types = str(except_value["business_type1"]) + str(except_value["business_type2"]) + str(
            except_value["business_type3"])
        # 判断通知内容中的三级业务类型是否正确
        assert notify_content["business_types"] == business_types
        # 判断通知内容中的商户是否为支付时传入的商户
        assert notify_content["partner"] == str(send_data["partner"])
        # 判断通知内容中的支付金额是否为支付时的金额
        assert notify_content["total_amount"] == str(send_data["total_amount"])
        # 判断通知内容中的担保交易标志是否与支付时一致
        assert notify_content["is_guarantee"] == send_data["is_guarantee"]
        # 支付时如果有营销金额，判断通知内容中的营销金额和营销账户是否与支付时一致
        for i in range(len(sub_orders)):
            # 可能存在notify_content中的sub_orders顺序与send_data的sub_order中的顺序不一致
            for j in range(len(sub_orders)):
                """
                思路：取notify_content中的sub_orders的sub_trade_no
                匹配send_data的sub_order中的sub_out_trade_no的记录进行校验
                """
                out_trade_no = json.loads(send_data["sub_orders"])[j]["sub_out_trade_no"]
                trade_no = OperationDbOrder().query_trade_no_by_out_trade_no(out_trade_no)
                if sub_orders[i]["sub_trade_no"] == trade_no:
                    assert sub_orders[i]["partner"] == str(json.loads(send_data["sub_orders"])[j]["partner"])
                    #
                    assert sub_orders[i]["pay_amount"] == str(json.loads(send_data["sub_orders"])[j]["pay_amount"])

                    if "market_amount" in json.loads(send_data["sub_orders"])[j].keys():
                        # 营销金额不为空的，判断营销金额和营销账户是否正确
                        # 实际上值一直都是非None的，如果配置中不填实际上也是0，如果填0，接口会报错
                        if json.loads(send_data["sub_orders"])[j][
                                   "market_amount"] is not None:
                            assert sub_orders[i]["market_amount"] == str(json.loads(send_data["sub_orders"])[j][
                                                                             "market_amount"])
                            assert sub_orders[i]["market_acc_partner"] == str(json.loads(send_data["sub_orders"])[j][
                                                                                  "market_acc_partner"])
                        # 如果营销金额为空，通知内容中返回营销金额为0
                        else:
                            assert sub_orders[i]["market_amount"] == '0'
                else:
                    continue


if __name__ == '__main__':
    pay_total_no = '1021202111210000000369'
    act_history_sql = 'SELECT user_id,act_type,tran_amount,dc_type,user_remark,trade_msg from db_act.t_act_history WHERE pay_no = "%s" limit 10' % pay_total_no
    db_act = OperationMysql("db_act")
    act_history = db_act.query(act_history_sql)
    act_history_length = len(act_history)
    print(act_history_length)
