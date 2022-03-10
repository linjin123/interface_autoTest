# @Author:linxy57
# @Time:2021/11/14:17:04
# @Desc: 托管交易校验

import json
from common.config import Config
from operationMysql.operation_db_escrow_trade import OperationDbEscrowTrade
from operationMysql.operation_db_escrow_act import OperationDbEscrowAct
from operationMysql.operation_db_order import OperationDbOrder
from common.common_util import data_init
from common.common_enum import CommonEnum
from operationMysql.operation_db_partner_notify import OperationDbPartnerNotify


class TradePayAssert:

    def __init__(self):
        self.common_enum = CommonEnum()

    # 托管交易订单校验
    def assert_order_detail(self, send_data, except_value, trade_detail):
        # order_detail = OperationDbOrder().query_trade_detail(out_trade_no, partner)
        pay_total_no = trade_detail["pay_total_no"]
        assert trade_detail["partner_id"] == send_data["partner"]
        # 三级业务类型
        assert trade_detail["business_type1"] == except_value["business_type1"]
        assert trade_detail["business_type2"] == except_value["business_type2"]
        assert trade_detail["business_type3"] == except_value["business_type3"]
        # 交易状态、订单内部状态、到账状态
        assert trade_detail["trade_status"] == self.common_enum.PayStatusEnum.SUCCESS.value
        # assert order_detail["order_inner_status"] == 1
        assert trade_detail["arrival_status"] == self.common_enum.ArrivalStatusEnum.RECEIVED.value
        # is_guarantee = send_data["is_guarantee"]
        # if is_guarantee == 'TRUE':
        #     assert trade_detail["confirm_receive_status"] == 1
        is_batch = TradePayAssert().is_batch(pay_total_no)
        if is_batch == True:
            total_count = send_data["total_count"]
            sub_orders = data_init().sub_orders_string_to_json(send_data)
            for i in range(total_count):
                sub_out_trade_no = sub_orders[i]["sub_out_trade_no"]
                partner = sub_orders[i]['partner']
                trade_detail = OperationDbOrder().query_trade_detail(sub_out_trade_no, partner)
                out_trade_no = trade_detail['out_trade_no']
                if sub_out_trade_no == out_trade_no:
                    assert trade_detail["pay_amount"] == int(sub_orders[i]["pay_amount"])
                    # assert order_detail["market_amount"] == send_data["sub_orders"][i]["pay_amount"]
                    assert trade_detail["trade_amount"] == int(sub_orders[i]["pay_amount"])
        # 交易金额、支付金额、营销金额
        else:
            assert trade_detail["pay_amount"] == send_data["pay_amount"]
            # assert order_detail["market_amount"] == send_data["market_amount"]
            assert trade_detail["trade_amount"] == send_data["order_amount"]

    # 托管交易总单校验
    def assert_pay_total(self, send_data, except_value, pay_total_no):
        pay_total_detail = OperationDbEscrowTrade().query_pay_total_order(pay_total_no)
        # payee_user_id = send_data["partner"]
        # payee_bank_act = OperationDbUser().query_escrow_act_mapping(payee_user_id)
        # 1:B2C交易,42:合单支付,49:B2C担保交易,50:B2C担保合并交易
        # rele_order_type = pay_total_detail["rele_order_type"]
        # 付款方信息
        # assert pay_total_detail["payer_user_id"]
        # assert pay_total_detail["payer_bank_act"]
        # assert pay_total_detail["payer_bank_act_type"]
        # # 收款方信息
        # assert pay_total_detail["payee_user_id"] == send_data["partner"]
        # assert pay_total_detail["payee_bank_act"] == payee_bank_act
        # assert pay_total_detail["payee_bank_act_type"]
        # 三级业务类型
        assert pay_total_detail["business_types"] == except_value["business_types"]
        # 渠道ID+名称
        assert pay_total_detail["channel_id"] == except_value["channel_id"]
        assert pay_total_detail["channel_name"] == except_value["channel_name"]
        # 渠道产品ID+名称
        assert pay_total_detail["channel_prod_id"] == except_value["channel_prod_id"]
        assert pay_total_detail["channel_prod_name"] == except_value["channel_prod_name"]
        # 支付单状态+内部状态
        assert pay_total_detail["pay_status"] == 3
        assert pay_total_detail["pay_inner_status"] == 5
        # 交易金额
        is_batch = TradePayAssert().is_batch(pay_total_no)
        if is_batch == True:
            assert pay_total_detail["amount"] == send_data['total_amount']
        else:
            assert pay_total_detail["amount"] == send_data["pay_amount"]

    # 托管交易收款流水校验
    def assert_receive_pay_flow(self, send_data, except_value, pay_total_no):
        pay_total_detail = OperationDbEscrowTrade().query_pay_total_order(pay_total_no)
        trade_inner_id = pay_total_detail["trade_inner_id"]
        receive_pay_flow_no = pay_total_no + '-' + str(trade_inner_id) + '-' + '01'
        receive_pay_flow_detail = OperationDbEscrowTrade().query_trade_flow(receive_pay_flow_no)
        partner = send_data["partner"]
        # 付款方信息
        # assert receive_pay_flow_detail["payer_user_id"]
        # assert receive_pay_flow_detail["payer_bank_act"]
        # assert receive_pay_flow_detail["payer_bank_act_type"]
        business_types = pay_total_detail["business_types"]
        # 当支付类型为工行支付宝app需要从配置读取中间商户
        if business_types == '111383' or business_types == '101383':
            middle_partner = TradePayAssert().query_middle_partner(partner)
        else:
            middle_partner = partner
        # 收款方信息
        assert receive_pay_flow_detail["payee_user_id"] == middle_partner
        # assert receive_pay_flow_detail["payee_bank_act"]
        # assert receive_pay_flow_detail["payee_bank_act_type"]
        # 三级业务类型
        assert receive_pay_flow_detail["business_types"] == except_value["business_types"]
        # 渠道ID+名称
        assert receive_pay_flow_detail["channel_id"] == except_value["channel_id"]
        assert receive_pay_flow_detail["channel_name"] == except_value["channel_name"]
        # 渠道产品ID+名称
        assert receive_pay_flow_detail["channel_prod_id"] == except_value["channel_prod_id"]
        assert receive_pay_flow_detail["channel_prod_name"] == except_value["channel_prod_name"]
        # 支付单状态+内部状态
        assert receive_pay_flow_detail["pay_status"] == self.common_enum.PayStatusEnum.SUCCESS.value
        assert receive_pay_flow_detail[
                   "pay_inner_status"] == self.common_enum.TradeFlowInnerStatusEnum.CASH_ARRIVED.value
        is_batch = TradePayAssert().is_batch(pay_total_no)
        if is_batch == True:
            # 交易金额
            assert receive_pay_flow_detail["amount"] == send_data["total_amount"]
        else:
            # 交易金额
            assert receive_pay_flow_detail["amount"] == send_data["pay_amount"]

    # 托管交易分账流水校验
    def assert_profit_pay_flow(self, send_data, except_value, pay_total_no):
        pay_total_detail = OperationDbEscrowTrade().query_pay_total_order(pay_total_no)
        trade_inner_id = pay_total_detail["trade_inner_id"]
        business_types = pay_total_detail["business_types"]
        partner = send_data["partner"]
        is_batch = TradePayAssert().is_batch(pay_total_no)
        # 当支付类型为工行支付宝app需要从配置读取中间商户
        if business_types == '111383' or business_types == '101383':
            middle_partner = TradePayAssert().query_middle_partner(partner)
        else:
            middle_partner = partner
        if is_batch == True:
            # main_trade_no = pay_total_detail["rele_order_no"]
            # main_trade_detail = OperationDbOrder().query_main_trade_detail(main_trade_no)
            # total_count = main_trade_detail["total_count"]
            total_count = send_data['total_count']
            sub_orders = data_init().sub_orders_string_to_json(send_data)
        else:
            total_count = 1
        for i in range(1, total_count + 1):
            profit_pay_flow_no = pay_total_no + '-' + str(trade_inner_id) + '-' + str(i + 1).zfill(2)
            profit_pay_flow_detail = OperationDbEscrowTrade().query_trade_flow(profit_pay_flow_no)
            # 付款方信息
            assert profit_pay_flow_detail["payer_user_id"] == middle_partner
            # assert profit_pay_flow_detail["payer_bank_act"]
            # assert profit_pay_flow_detail["payer_bank_act_type"]

            if is_batch == True:
                # 收款方信息
                assert profit_pay_flow_detail["payee_user_id"] == int(sub_orders[i - 1]["partner"])
                # 交易金额
                assert profit_pay_flow_detail["amount"] == int(sub_orders[i - 1]["pay_amount"])
            else:
                assert profit_pay_flow_detail["payee_user_id"] == send_data['partner']
                assert profit_pay_flow_detail["amount"] == send_data['pay_amount']
            # assert profit_pay_flow_detail["payee_bank_act"]
            # assert profit_pay_flow_detail["payee_bank_act_type"]
            # 三级业务类型
            assert profit_pay_flow_detail["business_types"] == except_value["business_types"]
            # 渠道ID+名称
            assert profit_pay_flow_detail["channel_id"] == except_value["profit_channel_id"]
            assert profit_pay_flow_detail["channel_name"] == except_value["profit_channel_name"]
            # 渠道产品ID+名称
            assert profit_pay_flow_detail["channel_prod_id"] == except_value["profit_channel_prod_id"]
            assert profit_pay_flow_detail["channel_prod_name"] == except_value["profit_channel_prod_name"]
            # 支付单状态+内部状态
            assert profit_pay_flow_detail["pay_status"] == self.common_enum.PayStatusEnum.SUCCESS.value
            assert profit_pay_flow_detail[
                       "pay_inner_status"] == self.common_enum.TradeFlowInnerStatusEnum.CASH_ARRIVED.value

    # 账务流水校验
    def assert_act_history(self, send_data, pay_total_no):
        pay_total_detail = OperationDbEscrowTrade().query_pay_total_order(pay_total_no)
        trade_inner_id = pay_total_detail["trade_inner_id"]
        business_types = pay_total_detail["business_types"]
        partner = send_data["partner"]
        is_batch = TradePayAssert().is_batch(pay_total_no)
        # 当支付类型为工行支付宝app需要从配置读取中间商户
        if business_types == '111383' or business_types == '101383':
            middle_partner = TradePayAssert().query_middle_partner(partner)
        else:
            middle_partner = partner
        if is_batch == True:
            total_count = send_data['total_count']
        else:
            total_count = 1
        for i in range(1, total_count + 1):
            trade_flow_no = pay_total_no + '-' + str(trade_inner_id) + '-' + str(i + 1).zfill(2)
            act_type = self.common_enum.EscrowActType.PRIMARY.value
            escrow_act = OperationDbEscrowAct().query_act_by_partner_and_act_type(middle_partner, act_type)
            escrow_act_history = OperationDbEscrowAct().query_act_history_by_trade_flow_no(trade_flow_no)
            profit_pay_flow_detail = OperationDbEscrowTrade().query_trade_flow(trade_flow_no)
            # 账户类型
            assert escrow_act_history['act_type'] == act_type
            # 账户号
            assert escrow_act_history['act_no'] == escrow_act['act_no']
            # 内部账号
            assert escrow_act_history['user_id'] == middle_partner
            # 交易订单类型
            assert escrow_act_history['trade_type'] == self.common_enum.TradeTypeEnum.PAY_TRADE.value
            # 账务流水类型
            assert escrow_act_history['trade_flow_type'] == self.common_enum.TradeFlowTypeEnum.PROFIT.value
            # 交易金额
            assert escrow_act_history['tran_amount'] == profit_pay_flow_detail['profit_amount']
            # 借贷类型
            assert escrow_act_history['dc_type'] == self.common_enum.DcTypeEnum.SUB.value

    # 通知校验
    def assert_notify(self, send_data, except_value, trade_detail):
        pay_total_no = trade_detail['pay_total_no']
        # 判断交易是否合单，如果合单则用合单号查
        is_batch = TradePayAssert().is_batch(pay_total_no)
        if is_batch == True:
            trade_no = trade_detail['main_trade_no']
            total_count = send_data['total_count']
        else:
            trade_no = trade_detail['trade_no']
            total_count = 1
        notify_data = OperationDbPartnerNotify().query_out_notify_by_trade_no(trade_no)
        # 获取商户外部通知数据中的content内容,notify_content中所有字段都是字符串
        notify_content = json.loads(notify_data["content"])
        # 判断通知接收者是否为支付时的收款商户
        assert notify_data["receiver"] == str(send_data["partner"])
        # 判断通知的订单号是否为传入的交易单号
        assert notify_data["order_no"] == trade_no
        # 判断通知内容中的接口类型是否正确
        assert notify_content['service'] == send_data['service']
        # 判断通知内容中的三级业务类型是否正确
        assert notify_content["business_types"] == except_value['business_types']
        if is_batch == True:
            # 获取外部通知数据content中的子单信息
            notify_content_sub_orders = json.loads(notify_content["sub_orders"])
            # 获取请求数据中的子单信息
            send_data_sub_orders = json.loads(send_data["sub_orders"])
            for i in range(total_count):
                for j in range(total_count):
                    # 判断通知内容中的商户是否为支付时传入的商户
                    assert notify_content_sub_orders[i]["partner"] == send_data_sub_orders[j]["partner"]
                    # 判断通知内容中的订单金额是否为支付时的金额
                    assert notify_content_sub_orders[i]["order_amount"] == send_data_sub_orders[j]["pay_amount"]
                    # 判断通知内容中的支付金额是否为支付时的金额
                    assert notify_content_sub_orders[i]["pay_amount"] == send_data_sub_orders[j]["pay_amount"]
                    # 判断通知内容中的营销金额是否为支付时的金额
                    if "market_amount" in send_data_sub_orders[j].keys():
                        if send_data_sub_orders[j]["market_amount"] is not None:
                            assert notify_content_sub_orders[i]["market_amount"] == send_data_sub_orders[j][
                                "market_amount"]
            # 总支付金额
            assert notify_content["total_amount"] == str(send_data["total_amount"])
            # 总订单金额
            assert notify_content["total_order_amount"] == str(send_data["total_order_amount"])
        else:
            # 判断通知内容中的商户是否为支付时传入的商户
            assert notify_content["partner"] == str(send_data["partner"])
            # 判断通知内容中的订单金额是否为支付时的金额
            assert notify_content["order_amount"] == str(send_data["order_amount"])
            # 判断通知内容中的支付金额是否为支付时的金额
            assert notify_content["pay_amount"] == str(send_data["pay_amount"])
            # 判断通知内容中的营销金额是否为支付时的金额
            if "market_amount" in send_data.keys():
                if send_data["market_amount"] is not None:
                    assert notify_content["market_amount"] == str(send_data["market_amount"])

    def query_middle_partner(self, partner):
        info = Config().getConfigData("UAT", "escrow.ali.app.pay.middle.partner.info").split(",")
        dict_01 = {}
        for i in range(len(info)):
            info_list = info[i].split("|")
            dict_01[info_list[0]] = info_list[1]
            dict_01.update(dict_01)
        for key in dict_01.keys():
            if key == str(partner):
                return int(dict_01[key])

    def is_batch(self, pay_total_no):
        pay_total_detail = OperationDbEscrowTrade().query_pay_total_order(pay_total_no)
        # 1:B2C交易   42:合单支付   49:B2C担保交易  50:B2C担保合并交易
        rele_order_type = pay_total_detail["rele_order_type"]
        # 如果为合单，则需要查询有多少笔子单
        if rele_order_type == 42 or rele_order_type == 50:
            return True
        else:
            return False

