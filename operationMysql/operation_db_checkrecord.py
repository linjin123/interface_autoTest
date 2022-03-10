from common.common_db import OperationMysql
from operationMysql.operation_db_escrow_channel import OperationDbEscrowChannel


class OperationDbCheckrecord():
    def __init__(self):
        self.op_mysql = OperationMysql("db_checkrecord")

    # 插入渠道对账明细
    def insert_escrow_channel_trade_detail(self, trade_no):
        ebank_tran_list = OperationDbEscrowChannel().query_ebank_tran_by_tradeNo(trade_no)
        if ebank_tran_list:
            trade_detail = ebank_tran_list
            self.op_mysql.update('''INSERT INTO db_checkrecord.t_escrow_channel_trade_detail (
                                    send_tran_no,
                                    pay_flow_no,
                                    trade_no,
                                    channel_id,
                                    channel_name,
                                    channel_prod_id,
                                    channel_prod_name,
                                    trade_date,
                                    tran_type,
                                    trade_amount,
                                    fee_rate,
                                    single_price,
                                    fee_amount,
                                    create_time,
                                    modify_time)
                                    values ("%s", "%s", "%s", "%s", "%s", 
                                            "%s", "%s", "%s", "%s", "%s", 
                                            "%s", "%s", "%s", "%s", "%s")'''
                                 % (trade_detail["send_tran_no"], trade_detail["pay_flow_no"],
                                    trade_detail["trade_no"], trade_detail["channel_id"],
                                    trade_detail["channel_name"], trade_detail["channel_prod_id"],
                                    trade_detail["channel_prod_name"], trade_detail["trade_date"],
                                    trade_detail["channel_type"], trade_detail["pay_amount"],
                                    trade_detail["fee_rate"], trade_detail["single_price"],
                                    trade_detail["fee_amount"], trade_detail["create_time"],
                                    trade_detail["modify_time"]))
        else:
            return None
