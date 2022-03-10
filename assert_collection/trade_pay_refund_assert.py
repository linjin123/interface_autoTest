# @Author:linxy57
# @Time:2021/11/20:16:12
# @Desc: 托管交易退款断言
import json

from operationMysql.operation_db_order import OperationDbOrder
from operationMysql.operation_db_escrow_trade import OperationDbEscrowTrade
from operationMysql.operation_db_escrow_act import OperationDbEscrowAct
from operationMysql.operation_db_partner_notify import OperationDbPartnerNotify
from common.common_enum import CommonEnum


class TradePayRefundAssert:

    def __init__(self):
        self.common_enum = CommonEnum()

    # 退款订单校验
    def assert_refund_order(self, send_data, except_value, refund_detail):
        out_trade_no = send_data["out_trade_no"]
        partner = send_data["partner"]
        origi_trade_detail = OperationDbOrder().query_trade_detail(out_trade_no, partner)
        # 原收款方信息
        assert refund_detail["partner"] == origi_trade_detail["partner"]
        # 校验原订单号、原支付单号、原商户订单号是否与原单一致
        assert refund_detail["origi_trade_no"] == origi_trade_detail["trade_no"]
        assert refund_detail["origi_pay_total_no"] == origi_trade_detail["pay_total_no"]
        assert refund_detail["origi_out_trade_no"] == origi_trade_detail["out_trade_no"]
        # 退款金额
        assert refund_detail["refund_amount"] == send_data["refund_amount"]
        # 退款订单状态+内部状态
        assert refund_detail["refund_status"] == self.common_enum.OrderStatusEnum.SUCCESS.value
        assert refund_detail["arrival_status"] == self.common_enum.ArrivalStatusEnum.RECEIVED.value
        assert refund_detail["inner_arrival_status"] == self.common_enum.InnerArrivalStatusEnum.ALL_RECEIVED.value
        # 三级业务类型
        assert refund_detail["business_type1"] == except_value["business_type1"]
        assert refund_detail["business_type2"] == except_value["business_type2"]
        assert refund_detail["business_type3"] == except_value["business_type3"]
        # 商户附言校验
        assert refund_detail["attach"] == send_data["attach"]
        # 平台ID、平台商户号

    # 退款总单校验
    def assert_refund_total(self, send_data, except_value, pay_total_detail):
        out_refund_no = send_data["out_refund_no"]
        out_trade_no = send_data["out_trade_no"]
        partner = send_data["partner"]
        refund_detail = OperationDbOrder().query_refund_trade_by_out_trade_no(out_refund_no, partner)
        origi_trade_detail = OperationDbOrder().query_trade_detail(out_trade_no, partner)
        origi_pay_total_no = origi_trade_detail["pay_total_no"]
        origi_pay_total_detail = OperationDbEscrowTrade().query_pay_total_order(origi_pay_total_no)
        # 退款金额
        assert pay_total_detail["amount"] == send_data["refund_amount"]
        # 交易类型
        assert pay_total_detail["trade_type"] == self.common_enum.TradeTypeEnum.REFUND_TRADE.value
        # 关联订单号、关联订单类型
        assert pay_total_detail["rele_order_no"] == refund_detail["refund_no"]
        assert pay_total_detail["rele_order_type"] == self.common_enum.ReleOrderTypeEnum.REFUND_ORDER.value
        # 校验退款支付总单的原订单号、订单类型与原交易支付总单的关联订单号、关联订单类型是否一致
        assert pay_total_detail["origi_rele_order_no"] == origi_pay_total_detail["rele_order_no"]
        assert pay_total_detail["origi_rele_order_type"] == origi_pay_total_detail["rele_order_type"]
        # 原商户订单号
        assert pay_total_detail["origi_trade_no"] == origi_pay_total_detail["trade_no"]
        # 原内部ID
        assert pay_total_detail["origi_trade_inner_id"] == origi_pay_total_detail["trade_inner_id"]
        # 平台ID、平台商户号
        if origi_pay_total_detail["plat_id"] is not None:
            assert pay_total_detail["plat_id"] == origi_pay_total_detail["plat_id"]
        if origi_pay_total_detail["plat_partner"] is not None:
            assert pay_total_detail["plat_partner"] == origi_pay_total_detail["plat_partner"]
        # 当原支付总单付款方信息不为空，校验与退款支付总单收款方是否一致
        if origi_pay_total_detail["payer_login_act"] is not None:
            assert pay_total_detail["payee_login_act"] == origi_pay_total_detail["payer_login_act"]
        if origi_pay_total_detail["payer_user_id"] is not None:
            assert pay_total_detail["payee_user_id"] == origi_pay_total_detail["payer_user_id"]
        if origi_pay_total_detail["payer_name"] is not None:
            assert pay_total_detail["payee_name"] == origi_pay_total_detail["payer_name"]
        if origi_pay_total_detail["payer_user_type"] is not None:
            assert pay_total_detail["payee_user_type"] == origi_pay_total_detail["payer_user_type"]
        if origi_pay_total_detail["payer_bank_name"] is not None:
            assert pay_total_detail["payee_bank_name"] == origi_pay_total_detail["payer_bank_name"]
        if origi_pay_total_detail["payer_bank_act"] is not None:
            assert pay_total_detail["payee_bank_act"] == origi_pay_total_detail["payer_bank_act"]
        if origi_pay_total_detail["payer_bank_act_name"] is not None:
            assert pay_total_detail["payee_bank_act_name"] == origi_pay_total_detail["payer_bank_act_name"]
        if origi_pay_total_detail["payer_bank_act_tail"] is not None:
            assert pay_total_detail["payee_bank_act_tail"] == origi_pay_total_detail["payer_bank_act_tail"]
        if origi_pay_total_detail["payer_bank_act_type"] is not None:
            assert pay_total_detail["payee_bank_act_type"] == origi_pay_total_detail["payer_bank_act_type"]
        # 校验退款支付总单付款方信息与原支付总单收款方信息是否一致
        assert pay_total_detail["payer_user_id"] == origi_pay_total_detail["payee_user_id"]
        assert pay_total_detail["payer_name"] == origi_pay_total_detail["payee_name"]
        assert pay_total_detail["payer_user_type"] == origi_pay_total_detail["payee_user_type"]
        assert pay_total_detail["payer_bank_name"] == origi_pay_total_detail["payee_bank_name"]
        assert pay_total_detail["payer_bank_act"] == origi_pay_total_detail["payee_bank_act"]
        assert pay_total_detail["payer_bank_act_name"] == origi_pay_total_detail["payee_bank_act_name"]
        assert pay_total_detail["payer_bank_act_tail"] == origi_pay_total_detail["payee_bank_act_tail"]
        assert pay_total_detail["payer_bank_act_type"] == origi_pay_total_detail["payee_bank_act_type"]
        # 退款总单状态+内部状态
        assert pay_total_detail["pay_status"] == self.common_enum.PayStatusEnum.SUCCESS.value
        assert pay_total_detail["pay_inner_status"] == self.common_enum.PayInnerStatusEnum.CASH_ARRIVED.value
        # 渠道ID+名称
        assert pay_total_detail["channel_id"] == except_value["profit_channel_id"]
        assert pay_total_detail["channel_name"] == except_value["profit_channel_name"]
        # 渠道产品ID+名称
        assert pay_total_detail["channel_prod_id"] == except_value["profit_channel_prod_id"]
        assert pay_total_detail["channel_prod_name"] == except_value["profit_channel_prod_name"]
        # 原支付总单已退金额
        pay_total_detail_list = OperationDbEscrowTrade().query_pay_total_by_origi_pay_total_no(origi_pay_total_no)
        amount = 0
        for i in range(len(pay_total_detail_list)):
            amount = amount + pay_total_detail_list[i]["amount"]
        assert origi_pay_total_detail["have_refund_amount"] == amount

    # 托管账户付款流水校验
    def assert_escrow_pay_flow(self, send_data, except_value, pay_total_detail):
        # 退款支付总单号
        pay_total_no = pay_total_detail["trade_no"]
        # 退款单内部ID
        trade_inner_id = pay_total_detail["trade_inner_id"]
        # 原交易总单号
        origi_pay_total_no = pay_total_detail["origi_trade_no"]
        # 托管账户付款流水号
        pay_flow_no = pay_total_no + '-' + str(trade_inner_id) + '-' + '01'
        # 托管账户付款流水信息
        pay_flow_detail = OperationDbEscrowTrade().query_trade_flow(pay_flow_no)
        # 关联原交易流水号
        origi_pay_flow_no = pay_flow_detail["origi_trade_flow_no"]
        # 原交易流水信息
        origi_pay_flow_detail = OperationDbEscrowTrade().query_trade_flow(origi_pay_flow_no)
        # 退款金额
        assert pay_flow_detail["amount"] == send_data["refund_amount"]
        # 交易流水类型
        assert pay_flow_detail["trade_type"] == self.common_enum.TradeTypeEnum.REFUND_TRADE.value
        assert pay_flow_detail["trade_flow_type"] ==self.common_enum.TradeFlowTypeEnum.REFUND.value
        # 原支付总单及流水
        assert pay_flow_detail["origi_trade_no"] == origi_pay_total_no
        # 付款方信息
        assert pay_flow_detail["payer_user_id"] == origi_pay_flow_detail["payee_user_id"]
        assert pay_flow_detail["payer_name"] == origi_pay_flow_detail["payee_name"]
        assert pay_flow_detail["payer_user_type"] == origi_pay_flow_detail["payee_user_type"]
        assert pay_flow_detail["payer_act_type"] == origi_pay_flow_detail["payee_act_type"]
        assert pay_flow_detail["payer_bank_name"] == origi_pay_flow_detail["payee_bank_name"]
        assert pay_flow_detail["payer_bank_act"] == origi_pay_flow_detail["payee_bank_act"]
        assert pay_flow_detail["payer_bank_act_name"] == origi_pay_flow_detail["payee_bank_act_name"]
        assert pay_flow_detail["payer_bank_act_type"] == origi_pay_flow_detail["payee_bank_act_type"]
        assert pay_flow_detail["payer_bank_act_province"] == origi_pay_flow_detail["payee_bank_act_province"]
        assert pay_flow_detail["payer_bank_act_city"] == origi_pay_flow_detail["payee_bank_act_city"]
        assert pay_flow_detail["payer_bank_detail_info"] == origi_pay_flow_detail["payee_bank_detail_info"]
        assert pay_flow_detail["payer_bank_code"] == origi_pay_flow_detail["payee_bank_code"]
        # 收款方信息
        assert pay_flow_detail["payee_user_id"] == origi_pay_flow_detail["payer_user_id"]
        assert pay_flow_detail["payee_name"] == origi_pay_flow_detail["payer_name"]
        assert pay_flow_detail["payee_user_type"] == origi_pay_flow_detail["payer_user_type"]
        assert pay_flow_detail["payee_bank_name"] == origi_pay_flow_detail["payer_bank_name"]
        assert pay_flow_detail["payee_bank_act"] == origi_pay_flow_detail["payer_bank_act"]
        assert pay_flow_detail["payee_bank_act_name"] == origi_pay_flow_detail["payer_bank_act_name"]
        assert pay_flow_detail["payee_bank_act_type"] == origi_pay_flow_detail["payer_bank_act_type"]
        assert pay_flow_detail["payee_bank_code"] == origi_pay_flow_detail["payer_bank_code"]
        # 渠道ID+名称
        assert pay_flow_detail["channel_id"] == origi_pay_flow_detail["channel_id"]
        assert pay_flow_detail["channel_name"] == origi_pay_flow_detail["channel_name"]
        # 渠道产品ID+名称
        assert pay_flow_detail["channel_prod_id"] == origi_pay_flow_detail["channel_prod_id"]
        assert pay_flow_detail["channel_prod_name"] == origi_pay_flow_detail["channel_prod_name"]
        # 退款流水状态+内部状态
        assert pay_flow_detail["pay_status"] == self.common_enum.PayStatusEnum.SUCCESS.value
        assert pay_flow_detail["pay_inner_status"] == self.common_enum.PayInnerStatusEnum.CASH_ARRIVED.value


    # 渠道退款流水校验
    def assert_channel_refund_flow(self, send_data, except_value, pay_total_detail):
        pay_total_no = pay_total_detail["trade_no"]
        trade_inner_id = pay_total_detail["trade_inner_id"]
        origi_pay_total_no = pay_total_detail["origi_trade_no"]
        origi_arrival_status = except_value["origi_arrival_status"]
        # 如果是到账后退款则存在两笔流水，渠道退款为第二笔
        if origi_arrival_status == 3:
            channel_refund_flow_no = pay_total_no + '-' + str(trade_inner_id) + '-' + '02'
        else:
            channel_refund_flow_no = pay_total_no + '-' + str(trade_inner_id) + '-' + '01'
        channel_refund_flow_detail = OperationDbEscrowTrade().query_trade_flow(channel_refund_flow_no)
        origi_pay_flow_no = channel_refund_flow_detail["origi_trade_flow_no"]
        origi_pay_flow_detail = OperationDbEscrowTrade().query_trade_flow(origi_pay_flow_no)
        # 退款金额
        assert channel_refund_flow_detail["amount"] == send_data["refund_amount"]
        # 交易流水类型
        assert channel_refund_flow_detail["trade_type"] == self.common_enum.TradeTypeEnum.REFUND_TRADE.value
        assert channel_refund_flow_detail["trade_flow_type"] == self.common_enum.TradeFlowTypeEnum.ONLINE_REFUND.value
        # 原订单支付总单、支付流水
        assert channel_refund_flow_detail["origi_trade_no"] == origi_pay_flow_detail["trade_no"]
        # 付款方信息
        assert channel_refund_flow_detail["payer_user_id"] == origi_pay_flow_detail["payee_user_id"]
        assert channel_refund_flow_detail["payer_name"] == origi_pay_flow_detail["payee_name"]
        assert channel_refund_flow_detail["payer_user_type"] == origi_pay_flow_detail["payee_user_type"]
        assert channel_refund_flow_detail["payer_act_type"] == origi_pay_flow_detail["payee_act_type"]
        # 渠道ID+名称
        assert channel_refund_flow_detail["channel_id"] == except_value["channel_id"]
        assert channel_refund_flow_detail["channel_name"] == except_value["channel_name"]
        # 渠道产品ID+名称
        assert channel_refund_flow_detail["channel_prod_id"] == except_value["channel_prod_id"]
        assert channel_refund_flow_detail["channel_prod_name"] == except_value["channel_prod_name"]
        # 退款流水状态+内部状态
        assert channel_refund_flow_detail["pay_status"] == self.common_enum.PayStatusEnum.SUCCESS.value
        assert channel_refund_flow_detail["pay_inner_status"] == self.common_enum.TradeFlowInnerStatusEnum.CASH_ARRIVED.value
        # 校验原交易流水已退金额与退款订单金额是否一致
        # 根据原交易总单号查询原交易所有流水
        origi_pay_flow_detail_list = OperationDbEscrowTrade().query_pay_flow_list_by_pay_total_no(origi_pay_total_no)
        # 轮询原交易流水
        for i in range(len(origi_pay_flow_detail_list)):
            # 当原交易订单号不为空则判断已退款金额与退款订单金额是否一致
            if origi_pay_flow_detail_list[i]["origi_sub_rele_order_no"] is not None:
                have_refund_amount = origi_pay_flow_detail_list[i]["have_refund_amount"]
                origi_sub_rele_order_no = origi_pay_flow_detail_list[i]["origi_sub_rele_order_no"]
                # 根据原交易订单号查询其所有退款订单
                refund_detail_list = OperationDbOrder().query_refund_list_by_origi_trade_no(origi_sub_rele_order_no)
                refund_amount = 0
                for j in range(len(refund_detail_list)):
                    pay_total_no = refund_detail_list[j]["refund_pay_no"]
                    refund_pay_flow_detail = OperationDbEscrowTrade().query_pay_flow_list_by_pay_total_no(pay_total_no)
                    refund_amount = refund_amount + refund_pay_flow_detail[0]["amount"]
                assert have_refund_amount == refund_amount

    # 账务流水校验
    def assert_act_history(self, send_data, refund_pay_total_detail):
        trade_inner_id = refund_pay_total_detail["trade_inner_id"]
        partner = send_data["partner"]
        trade_flow_no = pay_total_no + '-' + str(trade_inner_id) + '-' + '01'
        # 退款为托管账户出金
        act_type = self.common_enum.EscrowActType.TRADE.value
        escrow_act = OperationDbEscrowAct().query_act_by_partner_and_act_type(partner, act_type)
        escrow_act_history = OperationDbEscrowAct().query_act_history_by_trade_flow_no(trade_flow_no)
        refund_pay_flow_detail = OperationDbEscrowTrade().query_trade_flow(trade_flow_no)
        # 账户类型
        assert escrow_act_history['act_type'] == act_type
        # 账户号
        assert escrow_act_history['act_no'] == escrow_act['act_no']
        # 内部账号
        assert escrow_act_history['user_id'] == partner
        # 交易订单类型
        assert escrow_act_history['trade_type'] == self.common_enum.TradeTypeEnum.REFUND_TRADE.value
        # 账务流水类型
        assert escrow_act_history['trade_flow_type'] == self.common_enum.TradeFlowTypeEnum.REFUND.value
        # 交易金额
        assert escrow_act_history['tran_amount'] == refund_pay_flow_detail['amount']
        # 借贷类型
        assert escrow_act_history['dc_type'] == self.common_enum.DcTypeEnum.SUB.value

    # 外部通知
    def assert_notify(self, send_data, refund_detail):
        refund_no = refund_detail["refund_no"]
        notify_list = OperationDbPartnerNotify().query_out_notify_list_by_trade_no(refund_no)
        if notify_list is None:
            RuntimeError('发送外部通知异常，退款单号： %s' % refund_no)
        # 内转成功通知
        inner_transfer_notify = notify_list[0]
        if inner_transfer_notify is None:
            RuntimeError('内转成功通知发送异常，退款单号：%s' % refund_no)
        inner_transfer_notify_content = json.loads(inner_transfer_notify["content"])
        # 退款到账通知
        refund_arrival_notify = notify_list[1]
        if refund_arrival_notify is None:
            RuntimeError('退款到账通知发送异常，退款单号：%s' % refund_no)
        refund_arrival_notify_content = json.loads(refund_arrival_notify["content"])
        # 判断通知接收者是否为退款时的原交易收款商户
        assert inner_transfer_notify["receiver"] == str(send_data["partner"])
        assert refund_arrival_notify["receiver"] == str(send_data["partner"])
        # 判断通知的订单号是否为传入的交易单号
        assert inner_transfer_notify["order_no"] == refund_no
        assert refund_arrival_notify["order_no"] == refund_no
        # 判断通知状态
        assert inner_transfer_notify["notify_status"] == self.common_enum.NotifyStatus.SUCCESS.value
        assert refund_arrival_notify["notify_status"] == self.common_enum.NotifyStatus.SUCCESS.value
        # 内转成功通知断言
        # 判断通知内容中的商户是否为支付时传入的商户
        assert inner_transfer_notify_content["partner"] == str(send_data["partner"])
        # 判断通知内容中的订单金额是否为支付时的金额
        assert inner_transfer_notify_content["refund_amount"] == str(send_data["refund_amount"])
        # 判断退款状态是否为成功
        assert inner_transfer_notify_content["refund_status"] == self.common_enum.OrderStatusEnum.SUCCESS
        # 判断到账状态
        assert inner_transfer_notify_content["arrival_status"] == self.common_enum.NotifyArrivalStatus.PAYMENT_PROCESSING

        # 退款到账通知断言
        # 判断通知内容中的商户是否为支付时传入的商户
        assert refund_arrival_notify_content["partner"] == str(send_data["partner"])
        # 判断通知内容中的订单金额是否为支付时的金额
        assert refund_arrival_notify_content["refund_amount"] == str(send_data["refund_amount"])
        # 判断退款状态是否为成功
        assert refund_arrival_notify_content["refund_status"] == self.common_enum.OrderStatusEnum.SUCCESS
        # 判断到账状态
        assert refund_arrival_notify_content["arrival_status"] == self.common_enum.NotifyArrivalStatus.PAYMENT_RECEIVED



if __name__ == '__main__':
    origi_pay_flow_detail_list = OperationDbEscrowTrade().query_pay_flow_list_by_pay_total_no('1021202112130000002133')
    for i in range(len(origi_pay_flow_detail_list)):
        if origi_pay_flow_detail_list[i]["origi_sub_rele_order_no"] is not None:
            have_refund_amount = origi_pay_flow_detail_list[i]["have_refund_amount"]
            origi_sub_rele_order_no = origi_pay_flow_detail_list[i]["origi_sub_rele_order_no"]
            refund_detail_list = OperationDbOrder().query_refund_list_by_origi_trade_no(origi_sub_rele_order_no)
            refund_amount = 0
            for j in range(len(refund_detail_list)):
                pay_total_no = refund_detail_list[j]["refund_pay_no"]
                refund_pay_flow_detail = OperationDbEscrowTrade().query_pay_flow_list_by_pay_total_no(pay_total_no)
                refund_amount = refund_amount + refund_pay_flow_detail[0]["amount"]
            print(have_refund_amount)
            print(refund_amount)
