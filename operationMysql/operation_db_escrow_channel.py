from common.common_db import OperationMysql
from operationMysql.operation_db_escrow_trade import OperationDbEscrowTrade
import random
import math
import datetime


class OperationDbEscrowChannel(object):
    def __init__(self):
        self.op_mysql = OperationMysql("db_escrow_channel")

    # 查询渠道付款流水
    def query_pay_tran(self, tran_no):
        res = self.op_mysql.query(
            'SELECT * FROM db_escrow_channel.`t_pay_tran` WHERE tran_no="%s"' % tran_no)
        if res:
            return res[0]
        else:
            return None

    # 更新托管渠道收款流水（网银支付流水）
    def update_ebank_tran(self, tran_no):
        self.op_mysql.update(
            'UPDATE db_escrow_channel.t_ebank_tran SET PAY_STATUS=1, pay_time = NOW(), modify_time = NOW() '
            'WHERE tran_no = "%s"' % tran_no)

    # 更新托管渠道付款流水
    def update_pay_tran(self, tran_no):

        self.op_mysql.update(
            'UPDATE db_escrow_channel.t_pay_tran SET pay_status=1, payment_time = NOW(), modify_time = NOW() '
            'WHERE tran_no = "%s"' % tran_no)

    # 查询托管渠道退款流水
    def update_refund_tran(self, refund_tran_no):
        self.op_mysql.update(
            'UPDATE db_escrow_channel.t_refund_tran SET refund_status=1, refund_time = NOW(), modify_time = NOW() '
            'WHERE refund_tran_no = "%s"' % refund_tran_no)

    # 更新邮储数字人民币托管渠道流水
    def update_ecny_ebank_tran(self, trade_no):
        res = self.op_mysql.update(
            'UPDATE db_escrow_channel.t_ecny_ebank_tran SET pay_status=1 WHERE trade_no = "%s"' % trade_no)
        if res:
            return True
        else:
            return None

    # 更新邮储数字人民币重复支付托管渠道退款流水
    def update_ecny_ebank_repeat_refund_tran(self, pos_no):
        res = self.op_mysql.update(
            'UPDATE db_escrow_channel.t_refund_tran SET refund_status=1 WHERE refund_tran_no = "%s"' % pos_no)
        if res:
            return True
        else:
            return None

    # 查询托管渠道网银流水（用于插入对账数据）
    def query_ebank_tran_by_tradeNo(self, trade_no):
        res = self.op_mysql.query('''SELECT send_tran_no, 
                                    pay_flow_no, 
                                    trade_no, 
                                    channel_id, 
                                    channel_name, 
                                    channel_prod_id, 
                                    channel_prod_name, 
                                    DATE_SUB(CURDATE(),INTERVAL 0 DAY) as trade_date, 
                                    channel_type, 
                                    pay_amount, 
                                    pay_status as fee_rate, 
                                    pay_status as single_price, 
                                    pay_status as fee_amount, 
                                    NOW() as create_time,
                                    NOW() as modify_time
                                    FROM db_escrow_channel.t_ebank_tran 
                                    WHERE trade_no = "%s"''' % trade_no)
        if res:
            return res[0]
        else:
            return None

    # 模拟安心户加款
    def insert_reverse_tran(self, profit_pay_flow):
        tran_no = '10' + str(
            math.ceil(random.random() * 9000000000000000000000000000 + 1000000000000000000000000000))
        channel_tran_no = '21' + str(
            math.ceil(random.random() * 9000000000000000000000000000 + 1000000000000000000000000000))
        create_time = datetime.datetime.now()
        modify_time = datetime.datetime.now()
        trade_flow_list = OperationDbEscrowTrade().query_trade_flow(profit_pay_flow)
        self.op_mysql.update('''INSERT INTO db_escrow_channel.t_reverse_tran(
                            `tran_no`, 
                            `channel_tran_no`, 
                            `channel_id` , 
                            `channel_name`, 
                            `channel_prod_id`, 
                            `channel_prod_name`, 
                            `amount`, 
                            `payer_real_name`, 
                            `payer_bank_act`, 
                            `payer_bank_name`, 
                            `payee_real_name`, 
                            `payee_bank_act`, 
                            `payee_bank_name`, 
                            `payee_bank_code`, 
                            `bank_attach`, 
                            `create_time`, 
                            `modify_time`) value ("%s", "%s", "%s", "%s", "%s", 
                                            "%s", "%s", "%s", "%s", "%s", "%s", 
                                            "%s", "%s", "%s", "%s", "%s", "%s")'''
                             % (tran_no, channel_tran_no, trade_flow_list["channel_id"],
                                trade_flow_list["channel_name"], trade_flow_list["channel_prod_id"],
                                trade_flow_list["channel_prod_name"], trade_flow_list["amount"],
                                trade_flow_list["payer_bank_act_name"], trade_flow_list["payer_bank_act"],
                                trade_flow_list["payer_bank_name"], trade_flow_list["payee_bank_act_name"],
                                trade_flow_list["payee_bank_act"], trade_flow_list["payee_bank_name"],
                                trade_flow_list["payee_bank_code"], trade_flow_list["bank_attach"],
                                create_time, modify_time))
