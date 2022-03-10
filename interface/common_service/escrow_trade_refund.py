# @Author:linxy57
# @Time:2021/12/14 14:15
# @Desc: 托管交易退款
import logging
import time
import requests
import settings_uat
from common.common_util import data_init
from common.dubbo import dubbo
from common.elasticjob import elasticjob
from common.common_enum import CommonEnum
from operationMysql.operation_db_order import OperationDbOrder
from operationMysql.operation_db_escrow_trade import OperationDbEscrowTrade
from operationMysql.operation_db_escrow_channel import OperationDbEscrowChannel


class EscrowTradeRefund(object):

    def __init__(self):

        self.elasticjob_url = {"elasticjob_url": "http://10.16.157.96:20814"}
        self.common_enum = CommonEnum()
        # 生成请求序列号
        self.req_seq_no = data_init().req_seq_no()
        # 生成提交订单时间
        self.time = data_init().token_time()
        # 生成退款订单号
        self.out_refund_no = data_init().refund_no()

    # ****************************退款下单****************************
    def escrow_trade_refund(self, send_data, trade_detail):
        out_trade_no = trade_detail["out_trade_no"]
        partner = trade_detail["partner"]
        pay_amount = trade_detail["pay_amount"]
        business_type3 = trade_detail["business_type3"]
        send_data["partner"] = partner
        send_data.update({'req_seq_no': self.req_seq_no})
        send_data.update({'out_refund_no': self.out_refund_no})
        send_data.update({'out_refund_time': self.time})
        send_data.update({'out_trade_no': out_trade_no})
        send_data.update({'refund_total_amount': pay_amount})
        send_data.update({'refund_amount': pay_amount})
        # 签名
        sign = data_init().get_sign_no_sort(send_data)
        send_data.update({'sign': sign})
        # 进行退款下单
        refund_result = requests.post(settings_uat.B2C_refund_url, send_data, verify=False)
        result_code = refund_result.json()["result_code"]
        result_info = refund_result.json()["result_info"]
        # 断言下单结果是否为成功，成功才往下执行
        if result_code == '1001':
            refund_no = refund_result.json()["refund_no"]
        # 托管支付宝APP已确认收货不允许退款
        elif result_code == '110350077' and (business_type3 == 82 or business_type3 == 83):
            refund_no = None
        else:
            raise RuntimeError('退款下单失败，原交易订单号：%s' % out_trade_no)
        return refund_no, result_info

    # *************************托管网银/快捷/数字人民币交易当天退款*************************
    def escrow_trade_refund_on_trade_date(self, send_data, trade_detail):
        # 进行退款下单
        refund_no, result_info = EscrowTradeRefund().escrow_trade_refund(send_data, trade_detail)
        # 查询退款单信息
        refund_detail = OperationDbOrder().query_refund_trade_by_refund_no(refund_no)
        refund_pay_total_no = refund_detail["refund_pay_no"]
        if refund_pay_total_no is not None:
            refund_pay_total_detail = OperationDbEscrowTrade().query_pay_total_order(refund_pay_total_no)
            trade_inner_id = refund_pay_total_detail["trade_inner_id"]
            # 退款付款流水号
            channel_refund_flow_no = refund_pay_total_no + '-' + str(trade_inner_id) + '-' + '01'
            refund_detail, refund_pay_total_detail = EscrowTradeRefund().handle_channel_refund_flow(refund_no,
                                                                                                    channel_refund_flow_no)
            return refund_detail, refund_pay_total_detail
        else:
            raise RuntimeError('创建托管交易总单及流水异常,退款订单号 %s' % refund_no)

    # *************************托管网银/快捷/数字人民币交易未到账跨天退款/到账退款-即时到账/已确认收货退款-担保交易*************************
    def escrow_trade_refund_common(self, send_data, trade_detail):
        # 进行退款下单
        refund_no, result_info = EscrowTradeRefund().escrow_trade_refund(send_data, trade_detail)
        if refund_no:
            # 查询退款订单信息
            refund_detail = OperationDbOrder().query_refund_trade_by_refund_no(refund_no)
            refund_pay_total_no = refund_detail["refund_pay_no"]
            refund_status = refund_detail["refund_status"]
            # 判断退款订单退款状态不为成功
            if refund_status != self.common_enum.OrderStatusEnum.WAITING_PAY.value:
                raise RuntimeError('托管交易退款异常，退款单号：%s' % refund_no)
            # 判断退款支付总单及流水不存在
            refund_pay_total_detail = OperationDbEscrowTrade().query_pay_total_order(refund_pay_total_no)
            refund_flow_detail = OperationDbEscrowTrade().query_pay_flow_list_by_pay_total_no(refund_pay_total_no)
            if refund_pay_total_detail is not None or refund_flow_detail:
                raise RuntimeError('托管交易退款异常，退款单号：%s' % refund_no)
        else:
            refund_detail = None
        return refund_detail, result_info

    # *************************托管网银/快捷/数字人民币到账当天/跨天退款-担保交易*************************
    def escrow_trade_refund_arrival_guarantee(self, send_data, trade_detail):
        # 进行退款下单
        refund_no, result_info = EscrowTradeRefund().escrow_trade_refund(send_data, trade_detail)
        # 查询退款单信息
        refund_detail = OperationDbOrder().query_refund_trade_by_refund_no(refund_no)
        refund_pay_total_no = refund_detail["refund_pay_no"]
        if refund_pay_total_no is not None:
            refund_pay_total_detail = OperationDbEscrowTrade().query_pay_total_order(refund_pay_total_no)
            trade_inner_id = refund_pay_total_detail["trade_inner_id"]
            # 退款付款流水号
            refund_pay_flow_no = refund_pay_total_no + '-' + str(trade_inner_id) + '-' + '01'
            # 网银退款流水号
            channel_refund_flow_no = refund_pay_total_no + '-' + str(trade_inner_id) + '-' + '02'
            handle_result = EscrowTradeRefund().handle_refund_pay_flow(refund_no, refund_pay_flow_no)
            assert handle_result == True
            OperationDbEscrowChannel().insert_reverse_tran(refund_pay_flow_no)
            elasticjob(self.elasticjob_url, "escrow-channe-task-schedule-job").jobTrigger("ReverseAccountingJob")
            time.sleep(5)
            refund_detail, refund_pay_total_detail = EscrowTradeRefund().handle_channel_refund_flow(refund_no,
                                                                                                    channel_refund_flow_no)
            return refund_detail, refund_pay_total_detail
        else:
            raise RuntimeError('创建托管交易总单及流水异常,退款订单号 %s' % refund_no)

    # 处理付款流水
    def handle_refund_pay_flow(self, refund_no, refund_pay_flow_no):
        refund_pay_flow_detail = OperationDbEscrowTrade().query_trade_flow(refund_pay_flow_no)
        if refund_pay_flow_detail:
            refund_pay_flow_pay_inner_status = refund_pay_flow_detail["pay_inner_status"]
            tran_no = refund_pay_flow_detail["pos_no"]
            if refund_pay_flow_pay_inner_status != 6 or refund_pay_flow_pay_inner_status != 8:
                if refund_pay_flow_pay_inner_status == 4 or refund_pay_flow_pay_inner_status == 1:
                    time.sleep(5)
                    refund_pay_flow_detail = OperationDbEscrowTrade().query_trade_flow(refund_pay_flow_no)
                    refund_pay_flow_pay_inner_status = refund_pay_flow_detail["pay_inner_status"]
                    loop_count = 0
                    while refund_pay_flow_pay_inner_status != 5 and loop_count < 10:
                        refund_pay_flow_detail = OperationDbEscrowTrade().query_trade_flow(refund_pay_flow_no)
                        refund_pay_flow_pay_inner_status = refund_pay_flow_detail["pay_inner_status"]
                        loop_count += 1
                    if loop_count == 10:
                        raise RuntimeError('付款流水内部状态异常，流水号为： %s' % refund_pay_flow_no)
                    # 修改渠道流水
                    OperationDbEscrowChannel().update_pay_tran(tran_no)
                    elasticjob(self.elasticjob_url, "escrow-trade-job").jobTrigger("payRepairProducerJob")
                    # dubbo().RepairTradeFacade_payRepair_dubbo(refund_pay_flow_no)
                elif refund_pay_flow_pay_inner_status == 5:
                    # 修改渠道流水
                    OperationDbEscrowChannel().update_pay_tran(tran_no)
                    elasticjob(self.elasticjob_url, "escrow-trade-job").jobTrigger("payRepairProducerJob")
                    # dubbo().RepairTradeFacade_payRepair_dubbo(refund_pay_flow_no)
                else:
                    raise RuntimeError('付款流水内部状态异常，流水号为： %s' % refund_pay_flow_no)
                time.sleep(3)
                refund_pay_flow_detail = OperationDbEscrowTrade().query_trade_flow(refund_pay_flow_no)
                refund_pay_flow_pay_status = refund_pay_flow_detail["pay_status"]
                refund_pay_flow_pay_inner_status = refund_pay_flow_detail["pay_inner_status"]
                loop_count = 0
                while (refund_pay_flow_pay_status != 3 or refund_pay_flow_pay_inner_status != 6) and loop_count < 10:
                    time.sleep(3)
                    elasticjob(self.elasticjob_url, "escrow-trade-job").jobTrigger("payRepairProducerJob")
                    refund_pay_flow_detail = OperationDbEscrowTrade().query_trade_flow(refund_pay_flow_no)
                    refund_pay_flow_pay_status = refund_pay_flow_detail["pay_status"]
                    refund_pay_flow_pay_inner_status = refund_pay_flow_detail["pay_inner_status"]
                    loop_count += 1
                if loop_count == 10:
                    raise RuntimeError('更新付款流水状态异常,退款单号为：%s' % refund_no)
            else:
                logging.info('付款流水内部状态为渠道受理成功或资金已到账，流水号为： %s' % refund_pay_flow_no)
            return True

    # 处理渠道退款流水
    def handle_channel_refund_flow(self, refund_no, channel_refund_flow_no):
        channel_refund_flow_detail = OperationDbEscrowTrade().query_trade_flow(channel_refund_flow_no)
        if channel_refund_flow_detail:
            # 提取渠道流水号
            refund_tran_no = channel_refund_flow_detail["pos_no"]
            refund_pay_total_no = channel_refund_flow_detail["trade_no"]
            channel_refund_flow_pay_inner_status = channel_refund_flow_detail["pay_inner_status"]
            # 渠道退款流水状态为待下网关单，则触发退款下单补单job
            loop_count = 0
            while channel_refund_flow_pay_inner_status == 9 and loop_count < 10:
                time.sleep(2)
                elasticjob(self.elasticjob_url, "escrow-trade-job").jobTrigger("refundRepairProducerJob")
                channel_refund_flow_detail = OperationDbEscrowTrade().query_trade_flow(channel_refund_flow_no)
                channel_refund_flow_pay_inner_status = channel_refund_flow_detail["pay_inner_status"]
                loop_count += 1
            if loop_count == 10:
                raise RuntimeError("托管渠道退款流水下单异常，退款订单号： %s" % refund_no)
            # 判断渠道退款流水内部状态是否为“渠道已受理”
            if channel_refund_flow_pay_inner_status == 5:
                # 修改渠道流水为“交易成功”
                OperationDbEscrowChannel().update_refund_tran(refund_tran_no)
                time.sleep(60)
                elasticjob(self.elasticjob_url, "escrow-trade-job").jobTrigger("refundQueryRepairProducerJob")
            else:
                raise RuntimeError('托管渠道退款流水内部状态异常,退款订单号 %s' % refund_no)
            channel_refund_flow_detail = OperationDbEscrowTrade().query_trade_flow(channel_refund_flow_no)
            channel_refund_flow_pay_status = channel_refund_flow_detail["pay_status"]
            channel_refund_flow_pay_inner_status = channel_refund_flow_detail["pay_inner_status"]
            # 判断托管交易退款流水状态是否为“支付成功”+内部状态是否为“资金已到账”
            loop_count = 0
            while (
                    channel_refund_flow_pay_status != 3 or channel_refund_flow_pay_inner_status != 8) and loop_count < 10:
                time.sleep(3)
                elasticjob(self.elasticjob_url, "escrow-trade-job").jobTrigger("refundQueryRepairProducerJob")
                channel_refund_flow_detail = OperationDbEscrowTrade().query_trade_flow(channel_refund_flow_no)
                channel_refund_flow_pay_status = channel_refund_flow_detail["pay_status"]
                channel_refund_flow_pay_inner_status = channel_refund_flow_detail["pay_inner_status"]
                loop_count += 1
            if loop_count == 10:
                raise RuntimeError('更新托管渠道退款流水内部状态异常，退款单号：%s' % refund_no)
            refund_pay_total_detail = OperationDbEscrowTrade().query_pay_total_order(refund_pay_total_no)
            refund_pay_total_pay_status = refund_pay_total_detail["pay_status"]
            refund_pay_total_pay_inner_status = refund_pay_total_detail["pay_inner_status"]
            loop_count = 0
            # 判断托管交易退款总单支付状态是否为“成功”+内部状态是否为“资金已到账”
            while (refund_pay_total_pay_status != 3 or refund_pay_total_pay_inner_status != 5) and loop_count < 10:
                time.sleep(2)
                refund_pay_total_detail = OperationDbEscrowTrade().query_pay_total_order(refund_pay_total_no)
                refund_pay_total_pay_status = refund_pay_total_detail["pay_status"]
                refund_pay_total_pay_inner_status = refund_pay_total_detail["pay_inner_status"]
                loop_count += 1
            if loop_count >= 10:
                raise RuntimeError('更新托管交易退款总单内部状态异常，退款单号：%s' % refund_no)
            refund_detail = OperationDbOrder().query_refund_trade_by_refund_no(refund_no)
            refund_status = refund_detail["refund_status"]
            arrival_status = refund_detail["arrival_status"]
            inner_arrival_status = refund_detail["inner_arrival_status"]
            loop_count = 0
            while (refund_status != 3 or arrival_status != 3 or inner_arrival_status != 99) and loop_count < 10:
                time.sleep(2)
                refund_detail = OperationDbOrder().query_refund_trade_by_refund_no(refund_no)
                refund_status = refund_detail["refund_status"]
                arrival_status = refund_detail["arrival_status"]
                inner_arrival_status = refund_detail["inner_arrival_status"]
                loop_count += 1
            if loop_count >= 10:
                raise RuntimeError('更新托管交易订单状态异常，退款单号：%s' % refund_no)
            return refund_detail, refund_pay_total_detail
        else:
            raise RuntimeError('渠道退款流水不存在，退款单号：%s' % refund_no)
    # ************************************托管网银/快捷/数字人民币结算后退款***********************************

    # ************************************托管余额交易退款***********************************************

    # ************************************助贷-华润退款***********************************************

    # ************************************助贷-平安退款***********************************************
